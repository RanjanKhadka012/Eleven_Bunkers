/**
 * Frontend Entry Point
 * Initializes React and mounts the main App component to the DOM
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Create React root and mount the App component
// React.StrictMode highlights potential issues during development (double renders, deprecated APIs, etc.)
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
