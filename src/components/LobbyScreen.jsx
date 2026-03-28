function LobbyScreen({
  lobby,
  copied,
  message,
  waitingLabel,
  playerCount,
  minPlayers,
  maxPlayers,
  isHost,
  canStart,
  onCopyCode,
  onStartGame,
  onLeaveLobby,
}) {
  return (
    <main className="page narrow-page">
      <section className="panel-card lobby-card">
        <div className="lobby-header">
          <div>
            <p className="eyebrow">Waiting room</p>
            <h2>Access code {lobby.code}</h2>
          </div>
          <button className="ghost-button" onClick={onCopyCode}>
            {copied ? 'Copied' : 'Copy code'}
          </button>
        </div>

        <div className="stats-grid">
          <div className="stat-box">
            <span className="info-label">Players joined</span>
            <strong>{playerCount}</strong>
          </div>
          <div className="stat-box">
            <span className="info-label">Allowed range</span>
            <strong>
              {minPlayers}-{maxPlayers}
            </strong>
          </div>
          <div className="stat-box">
            <span className="info-label">Status</span>
            <strong>{lobby.status === 'waiting' ? 'Waiting' : 'Ready'}</strong>
          </div>
        </div>

        <p className="message neutral">{waitingLabel}</p>
        {message && <p className="message error">{message}</p>}

        <div className="player-list">
          <div className="player-row">
            <span>{lobby.hostName ?? 'Host'}</span>
            <span className="player-badge">Host</span>
          </div>

          {lobby.players.map((player) => (
            <div key={player.id} className="player-row">
              <span>{player.name}</span>
              <span className="player-badge">Player</span>
            </div>
          ))}
        </div>

        <div className="button-stack">
          {isHost ? (
            <button
              className="primary-button"
              onClick={onStartGame}
              disabled={!canStart || lobby.status !== 'waiting'}
            >
              {lobby.status === 'waiting' ? 'Start Game' : 'Game Started'}
            </button>
          ) : (
            <div className="player-waiting">Wait for the host to start the game.</div>
          )}

          <button className="secondary-button" onClick={onLeaveLobby}>
            Leave Lobby
          </button>
        </div>
      </section>
    </main>
  )
}

export default LobbyScreen
