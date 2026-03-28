/**
 * JoinScreen Component
 * Form for entering player name and lobby access code to join an existing game
 * Props:
 *   - playerName: current player name input value
 *   - joinCode: current access code input value
 *   - message: error/status message to display
 *   - onPlayerNameChange: callback when player name is typed
 *   - onJoinCodeChange: callback when access code is typed
 *   - onBack: callback for back button (return to home)
 *   - onJoinLobby: callback to submit form and join the game
 */
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
      {/* Form panel for joining a lobby */}
      <section className="panel-card">
        <p className="eyebrow">Join a lobby</p>
        <h2>Enter player details</h2>

        {/* Player name input field (max 20 characters) */}
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

        {/* Access code input field (max 6 characters, auto-uppercase) */}
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

        {/* Display error/status messages if any */}
        {message && <p className="message error">{message}</p>}

        {/* Navigation buttons */}
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
