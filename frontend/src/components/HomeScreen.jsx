/**
 * HomeScreen Component
 * Initial landing page with two options: host a new game or join an existing one
 * Props:
 *   - onHostGame: callback triggered when "Host Game" button is clicked
 *   - onShowJoin: callback triggered when "Join" button is clicked
 */
function HomeScreen({ onHostGame, onShowJoin }) {
  return (
    <main className="page page-home">
      {/* Hero section introducing the game */}
      <section className="hero-card">
        <p className="eyebrow">Social survival game</p>
        <h1>IIBunkers</h1>
        <p className="hero-copy">
          Build a bunker group, debate who gets in, and let the hidden survival
          system decide whether the final team can keep humanity alive.
        </p>
      </section>

      {/* Action buttons to select game mode */}
      <section className="action-grid">
        {/* Button to start hosting a new game */}
        <article className="action-card accent-host">
          <button className="primary-button" onClick={onHostGame}>
            Host Game
          </button>
        </article>

        {/* Button to join an existing game */}
        <article className="action-card accent-join">
          <button className="secondary-button" onClick={onShowJoin}>
            Join
          </button>
        </article>
      </section>

      {/* Tips for best experience */}
      <section className="tips-card">
        <p className="eyebrow">Recommendations</p>
        <div className="tips-list">
          <span>Host on desktop</span>
          <span>Play on phones</span>
        </div>
      </section>
    </main>
  )
}

export default HomeScreen
