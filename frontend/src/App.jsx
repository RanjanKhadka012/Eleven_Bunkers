import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [gameData, setGameData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Try to fetch from backend API
    const fetchGameData = async () => {
      try {
        const response = await fetch('/api/catastrophes/')
        if (response.ok) {
          const data = await response.json()
          setGameData(data)
        }
      } catch (err) {
        console.log('Backend not running yet')
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchGameData()
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>⚔️ BUNKER</h1>
        <p className="subtitle">A Social Survival Game</p>
      </header>

      <main className="main-content">
        <section className="intro">
          <h2>Welcome to Bunker</h2>
          <p>A mysterious catastrophe has struck humanity. A bunker offers salvation for a select few.</p>
          <p>But who gets to survive?</p>
          
          <div className="features">
            <div className="feature-card">
              <h3>🎭 Hidden Personas</h3>
              <p>Each player receives 8 unique cards defining their character</p>
            </div>
            
            <div className="feature-card">
              <h3>🗳️ Strategic Voting</h3>
              <p>Eliminate players one by one through group consensus</p>
            </div>
            
            <div className="feature-card">
              <h3>📊 Point System</h3>
              <p>Survival depends on the combined score of your group</p>
            </div>
            
            <div className="feature-card">
              <h3>🎯 Complete Uncertainty</h3>
              <p>Cards reveal slowly - who will you eliminate?</p>
            </div>
          </div>

          <div className="cta-section">
            <button className="btn btn-primary">Create Game</button>
            <button className="btn btn-secondary">Join Game</button>
          </div>
        </section>

        {loading && <p className="status">Loading game data...</p>}
        {error && <p className="status error">Backend connection pending</p>}
        {gameData && <p className="status">✓ Backend connected</p>}

        <section className="info">
          <h3>How to Play</h3>
          <ol>
            <li>Create or join a game with 2-12 players</li>
            <li>Receive a random persona with 8 hidden cards</li>
            <li>Participate in reveal rounds as cards are shown</li>
            <li>Vote to eliminate players you deem unfit for survival</li>
            <li>At the end, all scores are revealed and totaled</li>
            <li>If your group's score meets the threshold... HUMANITY SURVIVES!</li>
          </ol>
        </section>
      </main>

      <footer className="footer">
        <p>Bunker Game © 2026 | An experiment in tough choices</p>
      </footer>
    </div>
  )
}

export default App
