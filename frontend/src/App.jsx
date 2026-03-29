import { useEffect, useMemo, useState } from 'react'
import GameScreen from './components/GameScreen'
import HostGameScreen from './components/HostGameScreen'
import HomeScreen from './components/HomeScreen'
import JoinScreen from './components/JoinScreen'
import LobbyScreen from './components/LobbyScreen'
import {
  advanceDiscussionPhase,
  castVoteForPlayer,
  pauseDiscussion,
  revealForPlayer,
  resumeDiscussion,
  startLobbyGame,
  skipToVoting,
} from './lib/gameEngine'
import {
  MAX_PLAYERS,
  MIN_PLAYERS,
  createLobby,
  readLobbies,
  saveLobby,
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
      const storedLobby = readLobbies()[session.code]
      const nextLobby = storedLobby ? advanceDiscussionPhase(storedLobby) : storedLobby

      if (storedLobby && nextLobby !== storedLobby) {
        saveLobby(nextLobby)
      }

      if (!nextLobby) {
        setMessage('This lobby is no longer available.')
        setSession(null)
        setScreen('home')
        return
      }

      if (nextLobby.status === 'in_progress' || nextLobby.status === 'completed') {
        setScreen('game')
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

    if (lobby.status !== 'waiting') {
      return 'Game is ready. Players will move into their cards and reveal rounds.'
    }

    if (playerCount < MIN_PLAYERS) {
      if (MIN_PLAYERS === 1) {
        return 'Waiting for at least 1 player to join.'
      }

      return `Waiting for at least ${MIN_PLAYERS} players to join.`
    }

    return 'Lobby is ready. Host can start the game as moderator.'
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

    const updatedLobby = saveLobby(startLobbyGame(lobby))
    setSession((current) => ({
      ...current,
      lobby: updatedLobby,
    }))
    setScreen('game')
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

  const handleRevealCategory = (category) => {
    if (!lobby || !session?.playerId || !category) {
      return
    }

    const updatedLobby = saveLobby(revealForPlayer(lobby, session.playerId, category))
    setSession((current) => ({
      ...current,
      lobby: updatedLobby,
    }))
  }

  const handleSubmitVote = (targetId) => {
    if (!lobby || !session?.playerId) {
      return
    }

    const updatedLobby = saveLobby(castVoteForPlayer(lobby, session.playerId, targetId))
    setSession((current) => ({
      ...current,
      lobby: updatedLobby,
    }))
  }

  const handlePauseDiscussion = () => {
    if (!lobby) {
      return
    }

    const updatedLobby = saveLobby(pauseDiscussion(lobby))
    setSession((current) => ({
      ...current,
      lobby: updatedLobby,
    }))
  }

  const handleResumeDiscussion = () => {
    if (!lobby) {
      return
    }

    const updatedLobby = saveLobby(resumeDiscussion(lobby))
    setSession((current) => ({
      ...current,
      lobby: updatedLobby,
    }))
  }

  const handleSkipToVoting = () => {
    if (!lobby) {
      return
    }

    const updatedLobby = saveLobby(skipToVoting(lobby))
    setSession((current) => ({
      ...current,
      lobby: updatedLobby,
    }))
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

      {screen === 'game' && lobby?.game && session && (
        session.isHost ? (
          <HostGameScreen
            lobby={lobby}
            onPauseDiscussion={handlePauseDiscussion}
            onResumeDiscussion={handleResumeDiscussion}
            onSkipToVoting={handleSkipToVoting}
            onLeaveGame={resetHome}
          />
        ) : (
          <GameScreen
            lobby={lobby}
            session={session}
            onRevealCategory={handleRevealCategory}
            onSubmitVote={handleSubmitVote}
            onLeaveGame={resetHome}
          />
        )
      )}
    </div>
  )
}

export default App
