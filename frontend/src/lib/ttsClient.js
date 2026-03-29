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
          URL.revokeObjectURL(url)
          if (currentAudio === audio) {
            currentAudio = null
            currentUrl = null
          }
        },
        { once: true },
      )

      await audio.play()
      return audio
    } catch (error) {
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

export function buildEliminationNarration(playerName, roundNumber = 1) {
  if (!playerName) {
    return ''
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
  const text = buildOutcomeNarration(game)

  if (!text) {
    throw new Error('No outcome narration available to play.')
  }

  return playSpeech(text, options)
}

export async function playEliminationNarration(playerName, roundNumber, options = {}) {
  const text = buildEliminationNarration(playerName, roundNumber)

  if (!text) {
    throw new Error('No elimination narration available to play.')
  }

  return playSpeech(text, options)
}
