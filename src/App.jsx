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
  const [screen, setScreen] = useState('home')
  const [playerName, setPlayerName] = useState('')
  const [joinCode, setJoinCode] = useState('')
  const [message, setMessage] = useState('')
  const [session, setSession] = useState(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!session?.code) {
      return undefined
    }

    const syncLobby = () => {
      const nextLobby = readLobbies()[session.code]

      if (!nextLobby) {
        setMessage('This lobby is no longer available.')
        setSession(null)
        setScreen('home')
        return
      }

      setSession((current) => ({
        ...current,
        lobby: nextLobby,
      }))
    }

    syncLobby()
    const intervalId = window.setInterval(syncLobby, 1000)
    return () => window.clearInterval(intervalId)
  }, [session?.code])

  const lobby = session?.lobby ?? null
  const playerCount = lobby?.players.length ?? 0
  const canStart = session?.isHost && playerCount >= MIN_PLAYERS && playerCount <= MAX_PLAYERS

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

  const resetHome = () => {
    setScreen('home')
    setPlayerName('')
    setJoinCode('')
    setMessage('')
    setSession(null)
    setCopied(false)
  }

  const handleHostGame = () => {
    const lobbyData = createLobby()
    setSession({
      code: lobbyData.code,
      playerId: lobbyData.hostId,
      isHost: true,
      lobby: lobbyData,
    })
    setMessage('')
    setCopied(false)
    setScreen('lobby')
  }

  const handleJoinGame = () => {
    const normalizedCode = joinCode.trim().toUpperCase()
    const normalizedName = playerName.trim()

    if (!normalizedName) {
      setMessage('Enter a player name before joining.')
      return
    }

    if (normalizedCode.length !== 6) {
      setMessage('Enter a valid 6-character access code.')
      return
    }

    const lobbies = readLobbies()
    const targetLobby = lobbies[normalizedCode]

    if (!targetLobby) {
      setMessage('Lobby not found.')
      return
    }

    if (targetLobby.status !== 'waiting') {
      setMessage('That game has already started.')
      return
    }

    if (targetLobby.players.length >= MAX_PLAYERS) {
      setMessage('This lobby is already full.')
      return
    }

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

    lobbies[normalizedCode] = updatedLobby
    writeLobbies(lobbies)

    setSession({
      code: normalizedCode,
      playerId,
      isHost: false,
      lobby: updatedLobby,
    })
    setMessage('')
    setScreen('lobby')
  }

  const handleStartGame = () => {
    if (!lobby || !canStart) {
      return
    }

    const lobbies = readLobbies()
    const updatedLobby = {
      ...lobby,
      status: 'started',
    }

    lobbies[lobby.code] = updatedLobby
    writeLobbies(lobbies)

    setSession((current) => ({
      ...current,
      lobby: updatedLobby,
    }))
  }

  const handleCopyCode = async () => {
    if (!lobby?.code) {
      return
    }

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
