function listKeyTraits(player) {
  const cards = Object.entries(player.cards || {})
    .map(([category, card]) => ({
      category,
      name: card?.name,
      points: card?.points ?? 0,
    }))
    .filter((card) => card.name)

  const positive = [...cards].sort((a, b) => b.points - a.points).slice(0, 3)
  const negative = [...cards].sort((a, b) => a.points - b.points).slice(0, 2)

  return { positive, negative }
}

function buildSurvivorSnapshot(survivors) {
  return survivors.map((player) => {
    const { positive, negative } = listKeyTraits(player)
    return {
      name: player.name,
      score: player.score,
      profession: player.cards?.profession?.name,
      skill: player.cards?.skill?.name,
      health: player.cards?.health?.name,
      positiveTraits: positive.map((trait) => `${trait.name} (${trait.points >= 0 ? '+' : ''}${trait.points})`),
      riskTraits: negative
        .filter((trait) => trait.points < 0)
        .map((trait) => ({
          name: trait.name,
          points: trait.points,
        })),
    }
  })
}

function buildFallbackSummary(payload) {
  const survivors = payload.survivors || []
  const strongPlayer = [...survivors].sort((a, b) => b.score - a.score)[0]
  const weakLink = [...survivors]
    .flatMap((player) =>
      (player.riskTraits || []).map((risk) => ({
        playerName: player.name,
        riskName: risk.name,
        riskPoints: risk.points,
      })),
    )[0]

  const parts = []

  if (payload.survived) {
    parts.push(`The chances of survival are high.`)
    parts.push(`In ${payload.catastrophe}, this bunker still has a realistic path forward.`)
  } else {
    parts.push(`The chances of survival are low.`)
    parts.push(`In ${payload.catastrophe}, this bunker is still in serious danger.`)
  }

  if (strongPlayer?.profession || strongPlayer?.skill) {
    const strengths = [strongPlayer.profession, strongPlayer.skill].filter(Boolean).join(' and ')
    parts.push(`${strongPlayer.name} brings ${strengths}, which could steady the group under ${payload.bunker}.`)
  }

  if (weakLink?.riskName) {
    parts.push(
      `${weakLink.playerName} is a major concern because of ${weakLink.riskName}, which could quickly destabilize the group.`,
    )
  } else {
    parts.push('The group has few obvious weak points, so discipline and coordination matter more than raw luck.')
  }

  return parts.join(' ')
}

async function requestClaudeSummary(payload) {
  const apiKey = process.env.CLAUDE_API_KEY
  if (!apiKey) {
    console.warn('[outcome-summary] CLAUDE_API_KEY missing, using fallback summary')
    return buildFallbackSummary(payload)
  }

  const model = process.env.CLAUDE_MODEL || 'claude-3-5-haiku-latest'
  const system = [
    'You write short post-apocalyptic narrator lines for a bunker survival game.',
    'Write the complete final narration for the end of the game.',
    'Write 3 to 5 concise sentences.',
    'Do not use bullet points.',
    'Do not repeat exact score numbers unless necessary.',
    'The first sentence must clearly say either "The chances of survival are high." or "The chances of survival are low."',
    'Mention concrete survivor strengths and important risks.',
    'Make the wording fit the catastrophe and bunker condition.',
    'The text must be natural for text-to-speech narration.',
    'Do not mention Claude, scoring formulas, thresholds, or hidden system mechanics.',
  ].join(' ')

  const user = JSON.stringify(payload, null, 2)

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model,
      max_tokens: 220,
      system,
      messages: [
        {
          role: 'user',
          content: `Create the full final endgame narration from this payload:\n${user}`,
        },
      ],
    }),
  })

  if (!response.ok) {
    const detail = await response.text().catch(() => '')
    console.error('[outcome-summary] Claude request failed', {
      status: response.status,
      detail,
      model,
    })
    throw new Error(`Claude summary failed (${response.status}): ${detail}`)
  }

  const data = await response.json()
  const text = data?.content
    ?.filter((item) => item.type === 'text')
    ?.map((item) => item.text)
    ?.join(' ')
    ?.trim()

  console.info('[outcome-summary] Claude request succeeded', {
    model,
    chars: text?.length ?? 0,
    preview: text?.slice?.(0, 160),
  })

  return text || buildFallbackSummary(payload)
}

export async function outcomeSummaryHandler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' })
    return
  }

  const { game } = req.body || {}
  if (!game || game.survived === null) {
    res.status(400).json({ error: 'A completed game payload is required' })
    return
  }

  const survivors = (game.players || []).filter((player) => !player.isEliminated)
  const payload = {
    scenarioLabel: game.scenario?.label || '',
    catastrophe: game.catastrophe?.name || 'Unknown catastrophe',
    bunker: game.bunker?.name || 'Unknown bunker condition',
    survived: Boolean(game.survived),
    finalScore: game.finalScore,
    finalThreshold: game.finalThreshold,
    survivors: buildSurvivorSnapshot(survivors),
  }

  try {
    const narration = await requestClaudeSummary(payload)
    console.info('[outcome-summary] Returning Claude narration', {
      chars: narration.length,
      preview: narration.slice(0, 160),
    })
    res.status(200).json({ narration })
  } catch (error) {
    console.error('[outcome-summary] Falling back to deterministic narration', {
      message: error?.message || 'Unknown Claude failure',
    })
    res.status(200).json({
      narration: buildFallbackSummary(payload),
      fallback: true,
      error: error?.message || 'Unable to generate Claude summary',
    })
  }
}
