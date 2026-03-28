/**
 * Main App Component
 * Manages the game flow between home, join, and lobby screens
 * Handles lobby creation, player joining, and game state synchronization
 */

import { useEffect, useMemo, useState } from 'react'
import HomeScreen from './components/HomeScreen'
import JoinScreen from './components/JoinScreen'
import LobbyScreen from './components/LobbyScreen'
import {
  MAX_PLAYERS,
  MIN_PLAYERS,
  createLobby,
  readLobbies,
  writeLobbies,
} from './lib/lobbyStorage'
import './styles/app.css'

function App() {
  // UI State: which screen to display (home, join, or lobby)
  const [screen, setScreen] = useState('home')
  
  // Player input: name to join with
  const [playerName, setPlayerName] = useState('')
  
  // Player input: 6-character lobby code to join
  const [joinCode, setJoinCode] = useState('')
  
  // UI State: error/status messages to display to the user
  const [message, setMessage] = useState('')
  
  // Game State: current session info (code, playerId, isHost, lobby data)
  const [session, setSession] = useState(null)
  
  // UI State: tracks if lobby code was copied to clipboard
  const [copied, setCopied] = useState(false)

  /**
   * Poll for lobby updates from local storage every 1 second
   * Keeps the current player's view in sync if other players join/leave
   * Dependencies: only re-run if session code changes
   */
  useEffect(() => {
    // No lobby yet, skip sync
    if (!session?.code) {
      return undefined
    }

    /**
     * Fetch latest lobby data from storage
     * If lobby was deleted, notify player and reset to home
     * Otherwise update session with fresh lobby data
     */
    const syncLobby = () => {
      const nextLobby = readLobbies()[session.code]

      // Lobby deleted - maybe host closed it
      if (!nextLobby) {
        setMessage('This lobby is no longer available.')
        setSession(null)
        setScreen('home')
        return
      }

      // Update session with fresh lobby data
      setSession((current) => ({
        ...current,
        lobby: nextLobby,
      }))
    }

    // Run sync immediately, then set up interval to run every 1000ms
    syncLobby()
    const intervalId = window.setInterval(syncLobby, 1000)
    
    // Cleanup: stop polling when component unmounts or session code changes
    return () => window.clearInterval(intervalId)
  }, [session?.code])

  // Derived state: lobby object from session, or null if not in lobby
  const lobby = session?.lobby ?? null
  
  // Derived state: count of players currently in the lobby
  const playerCount = lobby?.players.length ?? 0
  
  // Derived state: can host start the game? (must be host, have min players, not exceed max)
  const canStart = session?.isHost && playerCount >= MIN_PLAYERS && playerCount <= MAX_PLAYERS

  /**
   * Generates contextual waiting message based on lobby and player count
   * Shows status like "waiting for players" or "ready to start"
   */
  const waitingLabel = useMemo(() => {
    if (!lobby) {
      return ''
    }

    if (lobby.status === 'started') {
      return 'Game started. Move players into the first reveal phase.'
    }

    if (playerCount < MIN_PLAYERS) {
      return `Waiting for at least ${MIN_PLAYERS} players.`
    }

    return 'Lobby is ready. Host can start the game.'
  }, [lobby, playerCount])

  /**
   * Clear all state and send user back to home screen
   * Called when leaving a lobby or after game completes
   */
  const resetHome = () => {
    setScreen('home')
    setPlayerName('')
    setJoinCode('')
    setMessage('')
    setSession(null)
    setCopied(false)
  }

  /**
   * Create a new lobby and set current player as host
   * Generates a unique lobby code and host player ID
   */
  const handleHostGame = () => {
    const lobbyData = createLobby()
    setSession({
      code: lobbyData.code,
      playerId: lobbyData.hostId,
  /**
   * Join an existing lobby with validation
   * - Validates player name is provided
   * - Validates lobby code is 6 characters
   * - Checks lobby exists and hasn't started
   * - Checks lobby isn't full
   * - Adds player to the lobby with unique ID
   */
  const handleJoinGame = () => {
    const normalizedCode = joinCode.trim().toUpperCase()
    const normalizedName = playerName.trim()

    // Validation: player name required
    if (!normalizedName) {
      setMessage('Enter a player name before joining.')
      return
    }

    // Validation: code must be exactly 6 characters
    if (normalizedCode.length !== 6) {
      setMessage('Enter a valid 6-character access code.')
      return
    }

    // Fetch all lobbies and find the target lobby
    const lobbies = readLobbies()
    const targetLobby = lobbies[normalizedCode]

    // Validation: lobby must exist
    if (!targetLobby) {
      setMessage('Lobby not found.')
      return
    }

    // Validation: lobby must not have started already
    if (targetLobby.status !== 'waiting') {
      setMessage('That game has already started.')
      return
    }

    // Validation: lobby must have room for another player
    if (targetLobby.players.length >= MAX_PLAYERS) {
      setMessage('This lobby is already full.')
      return
    }

    // Create new player and add to lobby
    const playerId = `player-${Date.now()}`
    const updatedLobby = {
      ...targetLobby,
      players: [
        ...targetLobby.players,
        {
          id: playerId,
          name: normalizedName,
          isHost: false,
        },
      ],
    }

    // Persist updated lobby to local storage
    lobbies[normalizedCode] = updatedLobby
    writeLobbies(lobbies)

    // Update session state and navigate to lobby screen          name: normalizedName,
          isHost: false,
  /**
   * Host starts the game - transitions lobby status from 'waiting' to 'started'
   * Only the host can start, and must have valid player count
   */
  const handleStartGame = () => {
    // Guard: only allow if valid lobby and canStart conditions met
    if (!lobby || !canStart) {
      return
    }

    // Update lobby status to 'started'
    const lobbies = readLobbies()
    const updatedLobby = {
      ...lobby,
      status: 'started',
    }

    // Persist to local storage and update session
    lobbies[lobby.code] = updatedLobby
    writeLobbies(lobbies)

    setSession((current) => ({
      ...current,
      lobby: updatedLobby,
    }))
  }

  /**
   * Copy the lobby code to clipboard for easy sharing
   * Shows confirmation message that disappears after 1.5 seconds
   */
  const handleCopyCode = async () => {
    if (!lobby?.code) {
      return
    }

    tr{/* Ambient background animations */}
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      {/* HOME SCREEN: Initial entry point - host or join game */}
      {screen === 'home' && (
        <HomeScreen onHostGame={handleHostGame} onShowJoin={() => setScreen('join')} />
      )}

      {/* JOIN SCREEN: Enter player name and lobby code */}
      {screen === 'join' && (
        <JoinScreen
          playerName={playerName}
          joinCode={joinCode}
          message={message}
          onPlayerNameChange={setPlayerName}
          onJoinCodeChange={setJoinCode}
          onBack={resetHome}
          onJoinLobby={handleJoinGame}
        />
      )}

      {/* LOBBY SCREEN: Waiting area where players gather before game starts */}
    try {
      await navigator.clipboard.writeText(lobby.code)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    } catch {
      setMessage('Copy failed. Share the code manually.')
    }
  }

  return (
    <div className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      {screen === 'home' && (
        <HomeScreen onHostGame={handleHostGame} onShowJoin={() => setScreen('join')} />
      )}

      {screen === 'join' && (
        <JoinScreen
          playerName={playerName}
          joinCode={joinCode}
          message={message}
          onPlayerNameChange={setPlayerName}
          onJoinCodeChange={setJoinCode}
          onBack={resetHome}
          onJoinLobby={handleJoinGame}
        />
      )}

      {screen === 'lobby' && lobby && (
        <LobbyScreen
          lobby={lobby}
          copied={copied}
          message={message}
          waitingLabel={waitingLabel}
          playerCount={playerCount}
          minPlayers={MIN_PLAYERS}
          maxPlayers={MAX_PLAYERS}
          isHost={session.isHost}
          canStart={canStart}
          onCopyCode={handleCopyCode}
          onStartGame={handleStartGame}
          onLeaveLobby={resetHome}
        />
      )}
    </div>
  )
}

export default App
