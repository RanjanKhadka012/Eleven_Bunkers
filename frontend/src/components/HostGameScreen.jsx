import { useEffect, useRef, useState } from 'react'
import {
  buildScenarioNarration,
  playEliminationNarration,
  playOpeningNarration,
  playOutcomeNarration,
  playSpeech,
} from '../lib/ttsClient'

function HostGameScreen({ lobby, onLeaveGame }) {
  const { game } = lobby
  const currentRound = game.currentRound
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [ttsError, setTtsError] = useState('')
  const [hasPlayedOpening, setHasPlayedOpening] = useState(false)
  const openingStartedRef = useRef(false)
  const previousPhaseRef = useRef(currentRound.phase)
  const lastNarratedEliminationRoundRef = useRef(null)
  const hasNarratedOutcomeRef = useRef(false)
  const [discussionNow, setDiscussionNow] = useState(Date.now())

  const speak = async (action) => {
    setTtsError('')
    setIsSpeaking(true)

    try {
      await action()
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
    speak(() => playEliminationNarration(eliminatedPlayer.name, latestRound.roundNumber))
    return undefined
  }, [game.completedRounds.length, game.players])

  useEffect(() => {
    if (game.survived === null || hasNarratedOutcomeRef.current) {
      return undefined
    }

    hasNarratedOutcomeRef.current = true
    speak(() => playOutcomeNarration(game))
    return undefined
  }, [game])

  const discussionSecondsLeft =
    currentRound.phase === 'discussion' && currentRound.discussionEndsAt
      ? Math.max(0, Math.ceil((currentRound.discussionEndsAt - discussionNow) / 1000))
      : 0

  const formattedDiscussionTime = `${String(Math.floor(discussionSecondsLeft / 60)).padStart(
    2,
    '0',
  )}:${String(discussionSecondsLeft % 60).padStart(2, '0')}`

  return (
    <main className="page host-page">
      <section className="host-topbar">
        <p className="eyebrow">Host Console</p>
        <button className="ghost-button compact-button" onClick={onLeaveGame}>
          Leave
        </button>
      </section>

      <section className="host-hero">
        <p className="eyebrow">Catastrophe</p>
        <h1>{game.catastrophe.name}</h1>
        {game.scenario?.label && <p className="eyebrow">Scenario: {game.scenario.label}</p>}
      </section>

      {currentRound.phase === 'discussion' && (
        <section className="discussion-timer host-discussion-timer">
          <span className="info-label">Discussion Timer</span>
          <strong>{formattedDiscussionTime}</strong>
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
          <button
            className="ghost-button"
            type="button"
            onClick={() => speak(() => playSpeech(buildScenarioNarration(game)))}
            disabled={isSpeaking}
          >
            Play Scenario Summary
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
          {isSpeaking && <span className="host-note">Generating audio…</span>}
          {ttsError && <span className="host-note host-note-error">{ttsError}</span>}
        </div>

        <p className="host-note">
          ElevenLabs audio generation and playback can plug into this host screen
          without exposing player cards or hidden information.
        </p>
      </section>
    </main>
  )
}

export default HostGameScreen
