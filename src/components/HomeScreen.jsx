function HomeScreen({ onHostGame, onShowJoin }) {
  return (
    <main className="page page-home">
      <section className="hero-card">
        <p className="eyebrow">Social survival game</p>
        <h1>IIBunkers</h1>
        <p className="hero-copy">
          Build a bunker group, debate who gets in, and let the hidden survival
          system decide whether the final team can keep humanity alive.
        </p>
      </section>

      <section className="action-grid">
        <article className="action-card accent-host">
          <button className="primary-button" onClick={onHostGame}>
            Host Game
          </button>
        </article>

        <article className="action-card accent-join">
          <button className="secondary-button" onClick={onShowJoin}>
            Join
          </button>
        </article>
      </section>

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
