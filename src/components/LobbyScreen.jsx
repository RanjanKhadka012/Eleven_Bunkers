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
            <strong>{lobby.status === 'started' ? 'Started' : 'Waiting'}</strong>
          </div>
        </div>

        <p className="message neutral">{waitingLabel}</p>
        {message && <p className="message error">{message}</p>}

        <div className="player-list">
          {lobby.players.map((player) => (
            <div key={player.id} className="player-row">
              <span>{player.name}</span>
              <span className="player-badge">{player.isHost ? 'Host' : 'Player'}</span>
            </div>
          ))}
        </div>

        <div className="button-stack">
          {isHost ? (
            <button
              className="primary-button"
              onClick={onStartGame}
              disabled={!canStart || lobby.status === 'started'}
            >
              {lobby.status === 'started' ? 'Game Started' : 'Start Game'}
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
