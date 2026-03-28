// ElevenLabs text-to-speech helper for the host screen.
// Calls a backend proxy so secrets stay server-side.

const defaultVoiceId = import.meta.env.VITE_ELEVENLABS_VOICE_ID || '21m00Tcm4TlvDq8ikWAM' // Rachel
const defaultModelId = 'eleven_multilingual_v2'
const ttsEndpoint = import.meta.env.VITE_TTS_ENDPOINT || 'http://localhost:5000/api/tts'
let speechQueue = Promise.resolve()

function enqueueSpeech(task) {
  const nextTask = speechQueue.catch(() => {}).then(task)
  speechQueue = nextTask.catch(() => {})
  return nextTask
}

async function synthesizeToBlob(text, voiceId = defaultVoiceId, modelId = defaultModelId) {
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
    throw new Error(`ElevenLabs TTS failed (${response.status}): ${detail}`)
  }

  const arrayBuffer = await response.arrayBuffer()
  return new Blob([arrayBuffer], { type: 'audio/mpeg' })
}

export async function playSpeech(text, options = {}) {
  return enqueueSpeech(async () => {
    const { voiceId = defaultVoiceId, modelId = defaultModelId } = options
    const blob = await synthesizeToBlob(text, voiceId, modelId)
    const url = URL.createObjectURL(blob)

    try {
      const audio = new Audio(url)
      await audio.play()
      audio.addEventListener('ended', () => URL.revokeObjectURL(url), { once: true })
      return audio
    } catch (error) {
      URL.revokeObjectURL(url)
      throw error
    }
  })
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
    return game.survived ? game.scenario.endingWin : game.scenario.endingLoss
  }

  return game.survived
    ? 'Humanity survives. The bunker held together when it mattered.'
    : 'The last defenses failed. Humanity fades into silence.'
}

export async function playOpeningNarration(game, options = {}) {
  const text = buildOpeningNarration(game)

  if (!text) {
    throw new Error('No opening narration available to play.')
  }

  return playSpeech(text, options)
}

export async function playOutcomeNarration(game, options = {}) {
  const text = buildOutcomeNarration(game)

  if (!text) {
    throw new Error('No outcome narration available to play.')
  }

  return playSpeech(text, options)
}
