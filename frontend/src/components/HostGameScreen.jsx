import { useEffect, useRef, useState } from 'react'
import {
  playEliminationNarration,
  playOpeningNarration,
  playOutcomeNarration,
  playSpeech,
  pauseCurrentSpeech,
  resumeCurrentSpeech,
  stopCurrentSpeech,
} from '../lib/ttsClient'

function HostGameScreen({ lobby, onPauseDiscussion, onResumeDiscussion, onSkipToVoting, onLeaveGame }) {
  const { game } = lobby
  const currentRound = game.currentRound
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [playbackState, setPlaybackState] = useState('idle') // idle | playing | paused
  const [ttsError, setTtsError] = useState('')
  const [hasPlayedOpening, setHasPlayedOpening] = useState(false)
  const openingStartedRef = useRef(false)
  const previousPhaseRef = useRef(currentRound.phase)
  const lastNarratedEliminationRoundRef = useRef(null)
  const hasNarratedOutcomeRef = useRef(false)
  const outcomeTimeoutRef = useRef(null)
  const [discussionNow, setDiscussionNow] = useState(Date.now())

  const attachAudioHandlers = (audio) => {
    if (!audio) {
      setPlaybackState('idle')
      return
    }

    setPlaybackState(audio.paused ? 'paused' : 'playing')

    const handleEnded = () => {
      setPlaybackState('idle')
      audio.removeEventListener('ended', handleEnded)
    }

    audio.addEventListener('ended', handleEnded)
  }

  const speak = async (action) => {
    setTtsError('')
    setIsSpeaking(true)

    try {
      const audio = await action()
      attachAudioHandlers(audio)
      return audio
    } catch (error) {
      setTtsError(error?.message || 'Unable to play narration')
    } finally {
      setIsSpeaking(false)
    }
  }

  useEffect(() => {
    if (!game || hasPlayedOpening || openingStartedRef.current) {
      return undefined
    }

    openingStartedRef.current = true

    const run = async () => {
      await speak(() => playOpeningNarration(game))
      setHasPlayedOpening(true)
    }

    run()
    return undefined
  }, [game, hasPlayedOpening])

  useEffect(() => {
    if (currentRound.phase !== 'discussion' || !currentRound.discussionEndsAt) {
      setDiscussionNow(Date.now())
      return undefined
    }

    const tick = () => setDiscussionNow(Date.now())
    tick()
    const intervalId = window.setInterval(tick, 1000)
    return () => window.clearInterval(intervalId)
  }, [currentRound.phase, currentRound.discussionEndsAt])

  useEffect(() => {
    const previousPhase = previousPhaseRef.current

    if (previousPhase === 'discussion' && currentRound.phase === 'voting') {
      speak(() =>
        playSpeech('Time is up. It is time to make your decision and cast your vote.'),
      )
    }

    previousPhaseRef.current = currentRound.phase
  }, [currentRound.phase])

  // Narrate each elimination exactly once; keyed on completed rounds length.
  useEffect(() => {
    const latestRound = game.completedRounds.at(-1)
    if (!latestRound?.eliminatedPlayerId) {
      return undefined
    }

    if (lastNarratedEliminationRoundRef.current === latestRound.roundNumber) {
      return undefined
    }

    const eliminatedPlayer = game.players.find(
      (player) => player.id === latestRound.eliminatedPlayerId,
    )

    if (!eliminatedPlayer) {
      return undefined
    }

    lastNarratedEliminationRoundRef.current = latestRound.roundNumber
    const isFinalElimination = game.survived !== null
    speak(() =>
      playEliminationNarration(
        eliminatedPlayer.name,
        latestRound.roundNumber,
        isFinalElimination,
      ),
    )
    return undefined
  }, [game.completedRounds.length, game.players])

  useEffect(() => {
    if (game.survived === null || hasNarratedOutcomeRef.current) {
      return undefined
    }

    console.info('[host] outcomeNarration:scheduled', {
      survived: game.survived,
      finalScore: game.finalScore,
      finalThreshold: game.finalThreshold,
    })
    hasNarratedOutcomeRef.current = true
    console.info('[host] outcomeNarration:starting-immediately')
    speak(() => playOutcomeNarration(game))
    return undefined
  }, [game])

  useEffect(() => {
    return () => {
      if (outcomeTimeoutRef.current) {
        window.clearTimeout(outcomeTimeoutRef.current)
      }
    }
  }, [])

  const isDiscussionPhase = currentRound.phase === 'discussion'
  const isDiscussionPaused = isDiscussionPhase && !currentRound.discussionEndsAt
  const discussionMillisRemaining = isDiscussionPhase
    ? currentRound.discussionEndsAt
      ? Math.max(0, currentRound.discussionEndsAt - discussionNow)
      : currentRound.discussionPausedRemaining ?? 0
    : 0
  const discussionSecondsLeft = Math.ceil(discussionMillisRemaining / 1000)

  const formattedDiscussionTime = `${String(Math.floor(discussionSecondsLeft / 60)).padStart(
    2,
    '0',
  )}:${String(discussionSecondsLeft % 60).padStart(2, '0')}`

  return (
    <main className="page host-page">
      <section className="host-topbar">
        <p className="eyebrow">Host Console</p>
      </section>

      <section className="host-hero">
        <p className="eyebrow">Catastrophe</p>
        <h1>{game.catastrophe.name}</h1>
        {game.scenario?.label && <p className="eyebrow">Scenario: {game.scenario.label}</p>}
      </section>

      {isDiscussionPhase && (
        <section className="discussion-timer host-discussion-timer">
          <span className="info-label">Discussion Timer</span>
          <strong>{isDiscussionPaused ? 'Paused' : formattedDiscussionTime}</strong>
        </section>
      )}

      <section className="host-scenario-panel">
        <div className="host-scenario-item">
          <span className="info-label">Bunker Size</span>
          <strong>{game.survivorsNeeded} survivors</strong>
        </div>
        <div className="host-scenario-item">
          <span className="info-label">Bunker Condition</span>
          <strong>{game.bunker.name}</strong>
        </div>
      </section>

      <section className="host-narration-panel">
        <div className="host-panel-header">
          <div>
            <p className="eyebrow">Narration</p>
            <h2>ElevenLabs control area</h2>
          </div>
        </div>

        <p className="host-copy">
          This screen is reserved for scenario narration and host commentary for the
          players.
        </p>

        <div className="host-actions">
          <button
            className="primary-button"
            type="button"
            onClick={() => speak(() => playOpeningNarration(game))}
            disabled={isSpeaking}
          >
            Play Opening
          </button>
          {game.survived !== null && (
            <button
              className="ghost-button"
              type="button"
              onClick={() => speak(() => playOutcomeNarration(game))}
              disabled={isSpeaking}
            >
              Play Outcome
            </button>
          )}
          <button
            className="ghost-button"
            type="button"
            onClick={() => {
              pauseCurrentSpeech()
              setPlaybackState('paused')
            }}
            disabled={playbackState !== 'playing'}
            aria-label="Pause narration"
            title="Pause narration"
          >
            II
          </button>
          <button
            className="ghost-button"
            type="button"
            onClick={async () => {
              await resumeCurrentSpeech()
              setPlaybackState('playing')
            }}
            disabled={playbackState !== 'paused'}
            aria-label="Resume narration"
            title="Resume narration"
          >
            {'▶'}
          </button>
          <button
            className="primary-button"
            type="button"
            onClick={() => {
              stopCurrentSpeech()
              setPlaybackState('idle')
            }}
            disabled={playbackState === 'idle'}
          >
            Skip narration
          </button>
          {isSpeaking && <span className="host-note">Generating audio…</span>}
          {ttsError && <span className="host-note host-note-error">{ttsError}</span>}
        </div>

        <p className="host-note">
          ElevenLabs audio generation and playback can plug into this host screen
          without exposing player cards or hidden information.
        </p>
        <p className="host-note">Controls the currently playing ElevenLabs audio.</p>
      </section>

      <section className="host-narration-panel">
        <div className="host-panel-header">
          <div>
            <p className="eyebrow">Round Controls</p>
            <h2>Discussion pacing</h2>
          </div>
        </div>

        <p className="host-copy">
          Pause the discussion timer or skip directly to voting for quicker testing.
        </p>

        <div className="host-actions">
          <button
            className="ghost-button"
            type="button"
            onClick={onPauseDiscussion}
            disabled={!isDiscussionPhase || isDiscussionPaused}
          >
            Pause discussion
          </button>
          <button
            className="ghost-button"
            type="button"
            onClick={onResumeDiscussion}
            disabled={!isDiscussionPhase || !isDiscussionPaused}
          >
            Resume discussion
          </button>
          <button
            className="primary-button"
            type="button"
            onClick={onSkipToVoting}
            disabled={!isDiscussionPhase}
          >
            Skip to voting
          </button>
        </div>

        <p className="host-note">
          These controls only affect the current round&apos;s discussion phase.
        </p>
      </section>

      <div className="page-footer-action">
        <button className="ghost-button compact-button" onClick={onLeaveGame}>
          Leave
        </button>
      </div>
    </main>
  )
}

export default HostGameScreen
