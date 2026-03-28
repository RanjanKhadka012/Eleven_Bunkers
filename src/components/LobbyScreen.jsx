/**
 * LobbyScreen Component
 * Waiting room where players gather before the game starts
 * Shows: access code, player list, join status, and host start button
 * Props:
 *   - lobby: lobby object with code, players, status
 *   - copied: whether code was just copied to clipboard
 *   - message: error/status message
 *   - waitingLabel: contextual message about game readiness
 *   - playerCount: number of players in lobby
 *   - minPlayers: minimum required players to start
 *   - maxPlayers: maximum allowed players
 *   - isHost: whether current user is the host
 *   - canStart: whether game can be started (host, min players, not started)
 *   - onCopyCode: callback to copy lobby code
 *   - onStartGame: callback to start the game
 *   - onLeaveLobby: callback to leave and return home
 */
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
      {/* Main lobby panel */}
      <section className="panel-card lobby-card">
        {/* Header with access code and copy button */}
        <div className="lobby-header">
          <div>
            <p className="eyebrow">Waiting room</p>
            <h2>Access code {lobby.code}</h2>
          </div>
          {/* Copy code button with feedback */}
          <button className="ghost-button" onClick={onCopyCode}>
            {copied ? 'Copied' : 'Copy code'}
          </button>
        </div>

        {/* Status stats: player count, min/max range, lobby status */}
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

        {/* Contextual message about game readiness */}
        <p className="message neutral">{waitingLabel}</p>
        {/* Error message if join failed etc */}
        {message && <p className="message error">{message}</p>}

        {/* List of players currently in the lobby */}
        <div className="player-list">
          {lobby.players.map((player) => (
            <div key={player.id} className="player-row">
              <span>{player.name}</span>
              <span className="player-badge">{player.isHost ? 'Host' : 'Player'}</span>
            </div>
          ))}
        </div>

        {/* Action buttons: Start Game (host only) or Leave Lobby */}
        <div className="button-stack">
          {isHost ? (
            /* Host can start the game if conditions are met */
            <button
              className="primary-button"
              onClick={onStartGame}
              disabled={!canStart || lobby.status === 'started'}
            >
              {lobby.status === 'started' ? 'Game Started' : 'Start Game'}
            </button>
          ) : (
            /* Non-host players must wait for host to start */
            <div className="player-waiting">Wait for the host to start the game.</div>
          )}

          {/* Leave lobby button available to all players */}
          <button className="secondary-button" onClick={onLeaveLobby}>
            Leave Lobby
          </button>
        </div>
      </section>
    </main>
  )
}

export default LobbyScreen
