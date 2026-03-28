function JoinScreen({
  playerName,
  joinCode,
  message,
  onPlayerNameChange,
  onJoinCodeChange,
  onBack,
  onJoinLobby,
}) {
  return (
    <main className="page narrow-page">
      <section className="panel-card">
        <p className="eyebrow">Join a lobby</p>
        <h2>Enter player details</h2>

        <label className="field">
          <span>Name</span>
          <input
            type="text"
            maxLength="20"
            value={playerName}
            onChange={(event) => onPlayerNameChange(event.target.value)}
            placeholder="Your display name"
          />
        </label>

        <label className="field">
          <span>Access code</span>
          <input
            type="text"
            maxLength="6"
            value={joinCode}
            onChange={(event) => onJoinCodeChange(event.target.value.toUpperCase())}
            placeholder="ABC123"
          />
        </label>

        {message && <p className="message error">{message}</p>}

        <div className="button-row">
          <button className="secondary-button" onClick={onBack}>
            Back
          </button>
          <button className="primary-button" onClick={onJoinLobby}>
            Join Lobby
          </button>
        </div>
      </section>
    </main>
  )
}

export default JoinScreen
