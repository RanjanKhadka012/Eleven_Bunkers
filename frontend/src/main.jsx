/**
 * Frontend Entry Point
 * Initializes React and mounts the main App component to the DOM
 */

import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { pingBackendHealth } from './lib/ttsClient'

// Create React root and mount the App component
// React.StrictMode highlights potential issues during development (double renders, deprecated APIs, etc.)
function Root() {
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const onLoad = () => {
        pingBackendHealth()
      }

      if (document.readyState === 'complete') {
        onLoad()
      } else {
        window.addEventListener('load', onLoad, { once: true })
      }

      return () => window.removeEventListener('load', onLoad)
    }

    return undefined
  }, [])

  return <App />
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
)
