import { useEffect, useState } from 'react'
import {
  buildScenarioNarration,
  playOpeningNarration,
  playOutcomeNarration,
  playSpeech,
} from '../lib/ttsClient'

function HostGameScreen({ lobby, onLeaveGame }) {
  const { game } = lobby
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [ttsError, setTtsError] = useState('')
  const [hasPlayedOpening, setHasPlayedOpening] = useState(false)

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
    if (!game || hasPlayedOpening) {
      return undefined
    }

    const run = async () => {
      await speak(() => playOpeningNarration(game))
      setHasPlayedOpening(true)
    }

    run()
    return undefined
  }, [game, hasPlayedOpening])

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
