function HostGameScreen({ lobby, onLeaveGame }) {
  const { game } = lobby

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
          <button className="primary-button" type="button">
            Narrate Scenario
          </button>
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
