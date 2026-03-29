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
  readLobby,
  saveLobby,
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

    let cancelled = false
    let running = false

    const syncLobby = async () => {
      if (running) return
      running = true

      try {
        const storedLobby = await readLobby(session.code)
        const nextLobby = storedLobby ? advanceDiscussionPhase(storedLobby) : storedLobby

        if (storedLobby && nextLobby !== storedLobby) {
          await saveLobby(nextLobby)
        }

        if (!nextLobby) {
          if (!cancelled) {
            setMessage('This lobby is no longer available.')
            setSession(null)
            setScreen('home')
          }
          return
        }

        if (nextLobby.status === 'in_progress' || nextLobby.status === 'completed') {
          setScreen('game')
        }

        if (!cancelled) {
          setSession((current) => ({
            ...current,
            lobby: nextLobby,
          }))
        }
      } finally {
        running = false
      }
    }

    syncLobby()
    const intervalId = window.setInterval(syncLobby, 1000)
    return () => {
      cancelled = true
      window.clearInterval(intervalId)
    }
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

  const handleHostGame = async () => {
    try {
      const lobbyData = await createLobby()
      setSession({
        code: lobbyData.code,
        playerId: lobbyData.hostId,
        isHost: true,
        lobby: lobbyData,
      })
      setMessage('')
      setCopied(false)
      setScreen('lobby')
    } catch (error) {
      setMessage(error?.message || 'Failed to create lobby')
    }
  }

  const handleJoinGame = async () => {
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

    let targetLobby = null

    try {
      targetLobby = await readLobby(normalizedCode)
    } catch (error) {
      setMessage(error?.message || 'Unable to load lobby')
      return
    }

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

    try {
      await saveLobby(updatedLobby)
    } catch (error) {
      setMessage(error?.message || 'Unable to join lobby')
      return
    }

    setSession({
      code: normalizedCode,
      playerId,
      isHost: false,
      lobby: updatedLobby,
    })
    setMessage('')
    setScreen('lobby')
  }

  const handleStartGame = async () => {
    if (!lobby || !canStart) {
      return
    }

    try {
      const updatedLobby = await saveLobby(startLobbyGame(lobby))
      setSession((current) => ({
        ...current,
        lobby: updatedLobby,
      }))
      setScreen('game')
    } catch (error) {
      setMessage(error?.message || 'Failed to start game')
    }
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

  const handleRevealCategory = async (category) => {
    if (!lobby || !session?.playerId || !category) {
      return
    }

    try {
      const updatedLobby = await saveLobby(revealForPlayer(lobby, session.playerId, category))
      setSession((current) => ({
        ...current,
        lobby: updatedLobby,
      }))
    } catch (error) {
      setMessage(error?.message || 'Failed to submit reveal')
    }
  }

  const handleSubmitVote = async (targetId) => {
    if (!lobby || !session?.playerId) {
      return
    }

    try {
      const updatedLobby = await saveLobby(castVoteForPlayer(lobby, session.playerId, targetId))
      setSession((current) => ({
        ...current,
        lobby: updatedLobby,
      }))
    } catch (error) {
      setMessage(error?.message || 'Failed to submit vote')
    }
  }

  const handlePauseDiscussion = async () => {
    if (!lobby) {
      return
    }

    try {
      const updatedLobby = await saveLobby(pauseDiscussion(lobby))
      setSession((current) => ({
        ...current,
        lobby: updatedLobby,
      }))
    } catch (error) {
      setMessage(error?.message || 'Failed to pause discussion')
    }
  }

  const handleResumeDiscussion = async () => {
    if (!lobby) {
      return
    }

    try {
      const updatedLobby = await saveLobby(resumeDiscussion(lobby))
      setSession((current) => ({
        ...current,
        lobby: updatedLobby,
      }))
    } catch (error) {
      setMessage(error?.message || 'Failed to resume discussion')
    }
  }

  const handleSkipToVoting = async () => {
    if (!lobby) {
      return
    }

    try {
      const updatedLobby = await saveLobby(skipToVoting(lobby))
      setSession((current) => ({
        ...current,
        lobby: updatedLobby,
      }))
    } catch (error) {
      setMessage(error?.message || 'Failed to skip to voting')
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
