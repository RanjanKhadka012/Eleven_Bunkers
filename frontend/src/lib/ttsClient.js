// ElevenLabs text-to-speech helper for the host screen.
// Calls a backend proxy so secrets stay server-side.

const defaultVoiceId = import.meta.env.VITE_ELEVENLABS_VOICE_ID
const defaultModelId = 'eleven_multilingual_v2'
const defaultRemoteTts = 'https://eleven-bunkers-backend-production.up.railway.app/api/tts'

const ttsEndpoint = (() => {
  const envEndpoint = import.meta.env.VITE_TTS_ENDPOINT?.trim()
  if (envEndpoint) return envEndpoint

  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    const isLocal = host === 'localhost' || host === '127.0.0.1'
    if (isLocal) return '/api/tts'
  }

  return defaultRemoteTts
})()

function getBackendBase() {
  if (ttsEndpoint.startsWith('http')) {
    try {
      return new URL(ttsEndpoint).origin
    } catch {
      // fall through
    }
  }

  if (typeof window !== 'undefined') {
    return window.location.origin
  }

  return ''
}

function getApiEndpoint(path) {
  if (path.startsWith('/')) {
    if (ttsEndpoint.startsWith('http')) {
      const origin = getBackendBase()
      return origin ? `${origin}${path}` : path
    }

    return path
  }

  return path
}
let speechQueue = Promise.resolve()
let currentAudio = null
let currentUrl = null
const eliminationFollowUps = [
  'Time to reveal new categories.',
  'Let us see who else will fail to earn a place in the bunker.',
  'The bunker is smaller now. Choose your next reveal carefully.',
  'The pressure is rising. Another decision is coming.',
  'Survival just got harsher. Prepare for the next reveal.',
]

function enqueueSpeech(task) {
  const nextTask = speechQueue.catch(() => {}).then(task)
  speechQueue = nextTask.catch(() => {})
  return nextTask
}

async function synthesizeToBlob(text, voiceId = defaultVoiceId, modelId = defaultModelId) {
  console.debug('[tts] sending request', { endpoint: ttsEndpoint, voiceId, modelId })

  const response = await fetch(ttsEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      voiceId,
      modelId,
    }),
  })

  if (!response.ok) {
    const detail = await response.text().catch(() => '')
    console.error('[tts] request failed', { status: response.status, detail })
    throw new Error(`ElevenLabs TTS failed (${response.status}): ${detail}`)
  }

  const arrayBuffer = await response.arrayBuffer()
  console.debug('[tts] response ok', { bytes: arrayBuffer.byteLength })
  return new Blob([arrayBuffer], { type: 'audio/mpeg' })
}

export async function playSpeech(text, options = {}) {
  return enqueueSpeech(async () => {
    const { voiceId = defaultVoiceId, modelId = defaultModelId } = options
    console.info('[tts] playSpeech:start', {
      chars: text?.length ?? 0,
      preview: text?.slice?.(0, 140),
      voiceId,
      modelId,
    })
    const blob = await synthesizeToBlob(text, voiceId, modelId)
    const url = URL.createObjectURL(blob)

    try {
      const audio = new Audio(url)
      currentAudio?.pause()
      if (currentUrl) {
        URL.revokeObjectURL(currentUrl)
      }

      currentAudio = audio
      currentUrl = url

      audio.addEventListener(
        'ended',
        () => {
          console.info('[tts] playSpeech:ended')
          URL.revokeObjectURL(url)
          if (currentAudio === audio) {
            currentAudio = null
            currentUrl = null
          }
        },
        { once: true },
      )

      await audio.play()
      console.info('[tts] playSpeech:playing')
      return audio
    } catch (error) {
      console.error('[tts] playSpeech:error', { message: error?.message })
      URL.revokeObjectURL(url)
      throw error
    }
  })
}

export function pauseCurrentSpeech() {
  if (currentAudio && !currentAudio.paused) {
    currentAudio.pause()
  }
}

export function resumeCurrentSpeech() {
  if (currentAudio && currentAudio.paused) {
    return currentAudio.play()
  }

  return Promise.resolve()
}

export function stopCurrentSpeech() {
  if (!currentAudio) {
    return
  }

  try {
    currentAudio.pause()
    currentAudio.currentTime = currentAudio.duration || 0
  } catch {
    // ignore
  }

  if (currentUrl) {
    URL.revokeObjectURL(currentUrl)
  }

  currentAudio = null
  currentUrl = null
}

export async function pingBackendHealth() {
  const base = getBackendBase()

  if (!base) {
    console.warn('[tts] backend base unresolved; skipping health ping')
    return
  }

  const url = `${base}/health`
  console.debug('[tts] pinging backend health', { url })

  try {
    const res = await fetch(url, { method: 'GET' })
    const ok = res.ok
    console.info('[tts] backend health response', { status: res.status, ok })
  } catch (error) {
    console.error('[tts] backend health ping failed', { message: error?.message })
  }
}

export function buildScenarioNarration(game) {
  if (game?.scenario) {
    return [
      game.scenario.opening,
      game.scenario.explanation,
      `Catastrophe: ${game.catastrophe.name}.`,
      `Bunker condition: ${game.bunker.name}.`,
      `Survivors needed: ${game.survivorsNeeded}.`,
    ]
      .filter(Boolean)
      .join(' ')
  }

  return [
    `Catastrophe: ${game.catastrophe?.name}.`,
    `Bunker condition: ${game.bunker?.name}.`,
    `Survivors needed: ${game.survivorsNeeded}.`,
    'Make your reveals, then vote to decide who survives.',
  ]
    .filter(Boolean)
    .join(' ')
}

export function buildOpeningNarration(game) {
  if (!game) return ''

  if (game.scenario) {
    return [game.scenario.opening, game.scenario.explanation]
      .filter(Boolean)
      .join(' ')
  }

  return buildScenarioNarration(game)
}

export function buildOutcomeNarration(game) {
  if (!game || game.survived === null) {
    return ''
  }

  if (game.scenario) {
    return [
      game.survived
        ? 'The chances of survival are high.'
        : 'The chances of survival are low.',
      game.survived ? game.scenario.endingWin : game.scenario.endingLoss,
    ]
      .filter(Boolean)
      .join(' ')
  }

  return game.survived
    ? 'The chances of survival are high. Humanity survives. The bunker held together when it mattered.'
    : 'The chances of survival are low. The last defenses failed. Humanity fades into silence.'
}

function buildLocalOutcomeSummary(game) {
  const survivors = (game?.players || []).filter((player) => !player.isEliminated)
  if (survivors.length === 0) {
    return ''
  }

  const strongestSurvivor = [...survivors].sort((a, b) => b.score - a.score)[0]
  const strongestProfession = strongestSurvivor?.cards?.profession?.name
  const strongestSkill = strongestSurvivor?.cards?.skill?.name

  const keyRisk = survivors
    .flatMap((player) =>
      Object.values(player.cards || {}).map((card) => ({
        playerName: player.name,
        name: card?.name,
        points: card?.points ?? 0,
      })),
    )
    .filter((card) => card.name && card.points < 0)
    .sort((a, b) => a.points - b.points)[0]

  const parts = []

  if (strongestProfession || strongestSkill) {
    const strengths = [strongestProfession, strongestSkill].filter(Boolean).join(' and ')
    parts.push(`${strongestSurvivor.name} brings ${strengths}, which could make a real difference in ${game.catastrophe?.name}.`)
  }

  if (game.bunker?.name) {
    parts.push(`The bunker condition is ${game.bunker.name}, so every useful role matters.`)
  }

  if (keyRisk) {
    parts.push(`The biggest concern is ${keyRisk.name} carried by ${keyRisk.playerName}.`)
  }

  return parts.join(' ')
}

export async function fetchOutcomeSummary(game, timeoutMs = 2500) {
  if (!game || game.survived === null) {
    return ''
  }

  console.info('[tts] outcomeSummary:fetch:start', {
    endpoint: getApiEndpoint('/api/outcome-summary'),
    timeoutMs,
  })

  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null
  const timeoutId = controller
    ? window.setTimeout(() => controller.abort(), timeoutMs)
    : null

  let response
  try {
    response = await fetch(getApiEndpoint('/api/outcome-summary'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ game }),
      signal: controller?.signal,
    })
  } finally {
    if (timeoutId) {
      window.clearTimeout(timeoutId)
    }
  }

  if (!response.ok) {
    const detail = await response.text().catch(() => '')
    console.error('[tts] outcomeSummary:fetch:failed', { status: response.status, detail })
    throw new Error(`Outcome summary failed (${response.status}): ${detail}`)
  }

  const data = await response.json()
  const narration = data?.narration?.trim?.() || ''
  console.info('[tts] outcomeSummary:fetch:ok', {
    chars: narration.length,
    fallback: Boolean(data?.fallback),
    error: data?.error || null,
    preview: narration.slice(0, 140),
  })
  return narration
}

export function buildEliminationNarration(playerName, roundNumber = 1, isFinalElimination = false) {
  if (!playerName) {
    return ''
  }

  if (isFinalElimination) {
    return `Player ${playerName} has been eliminated.`
  }

  const followUp = eliminationFollowUps[(roundNumber - 1) % eliminationFollowUps.length]
  return `Player ${playerName} has been eliminated. ${followUp}`
}

export async function playOpeningNarration(game, options = {}) {
  const text = buildOpeningNarration(game)

  if (!text) {
    throw new Error('No opening narration available to play.')
  }

  return playSpeech(text, options)
}

export async function playOutcomeNarration(game, options = {}) {
  let narrationText = ''
  try {
    narrationText = await fetchOutcomeSummary(game)
  } catch (error) {
    console.error('[tts] outcome summary failed', { message: error?.message })
  }

  if (!narrationText) {
    narrationText = [buildOutcomeNarration(game), buildLocalOutcomeSummary(game)]
      .filter(Boolean)
      .join(' ')
    console.info('[tts] outcomeNarration:fallback-local', {
      chars: narrationText.length,
      preview: narrationText.slice(0, 140),
    })
  } else {
    console.info('[tts] outcomeNarration:using-remote-narration', {
      chars: narrationText.length,
    })
  }

  console.info('[tts] outcomeNarration:final', {
    chars: narrationText.length,
    preview: narrationText.slice(0, 200),
  })

  if (!narrationText) {
    throw new Error('No outcome narration available to play.')
  }

  return playSpeech(narrationText, options)
}

export async function playEliminationNarration(
  playerName,
  roundNumber,
  isFinalElimination = false,
  options = {},
) {
  const text = buildEliminationNarration(playerName, roundNumber, isFinalElimination)

  if (!text) {
    throw new Error('No elimination narration available to play.')
  }

  return playSpeech(text, options)
}
