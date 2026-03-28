import { useMemo, useState } from 'react'
import { CATEGORY_LABELS, REVEAL_ORDER, getVisibleCards } from '../lib/gameEngine'

function GameScreen({ lobby, session, onRevealCategory, onSubmitVote, onLeaveGame }) {
  const { game } = lobby
  const currentRound = game.currentRound
  const currentPlayer = game.players.find((player) => player.id === session.playerId) ?? null
  const isHostView = session.isHost
  const activePlayers = game.players.filter((player) => !player.isEliminated)
  const currentVote = currentRound.votes[session.playerId]
  const currentPlayerHasRevealed = currentRound.revealedBy.includes(session.playerId)
  const votesSubmitted = Object.keys(currentRound.votes).length
  const lastRound = game.completedRounds.at(-1)
  const lastEliminated =
    lastRound && game.players.find((player) => player.id === lastRound.eliminatedPlayerId)
  const [selectedReveal, setSelectedReveal] = useState('')

  const revealChoices = useMemo(() => {
    if (!currentPlayer) {
      return []
    }

    return REVEAL_ORDER.filter(
      (category) =>
        category !== 'profession' && !currentPlayer.revealedCategories.includes(category),
    )
  }, [currentPlayer])

  const canConfirmReveal =
    currentRound.phase === 'reveal' &&
    !isHostView &&
    currentPlayer &&
    !currentPlayer.isEliminated &&
    !currentPlayerHasRevealed &&
    Boolean(selectedReveal)

  const handleConfirmReveal = () => {
    if (!canConfirmReveal) {
      return
    }

    onRevealCategory(selectedReveal)
    setSelectedReveal('')
  }

  return (
    <main className="page game-page">
      <section className="game-topbar game-topbar-minimal">
        <div>
          <p className="eyebrow">Round</p>
          <h2>
            {game.survived !== null ? 'Final result' : `${currentRound.roundNumber} of ${game.totalRounds}`}
          </h2>
        </div>
        <button className="ghost-button compact-button" onClick={onLeaveGame}>
          Leave
        </button>
      </section>

      {game.survived === null ? (
        <section className="panel-card gameplay-panel">
          <div className="progress-strip">
            <div className="progress-card">
              <span className="info-label">
                {currentRound.phase === 'reveal' ? 'Reveals submitted' : 'Votes submitted'}
              </span>
              <strong>
                {currentRound.phase === 'reveal'
                  ? `${currentRound.revealedBy.length}/${activePlayers.length}`
                  : `${votesSubmitted}/${activePlayers.length}`}
              </strong>
            </div>
            <div className="progress-card">
              <span className="info-label">Eliminations left</span>
              <strong>{Math.max(0, activePlayers.length - game.survivorsNeeded)}</strong>
            </div>
          </div>

          <div className="phase-box">
            {currentRound.phase === 'reveal' ? (
              isHostView ? (
                <p className="phase-copy phase-copy-tight">
                  Players are choosing one hidden category to reveal this round.
                </p>
              ) : (
                <>
                  <p className="phase-copy">
                    Profession is already visible. Choose one other hidden category on
                    your own card, then confirm the reveal.
                  </p>
                  {currentPlayerHasRevealed ? (
                    <p className="phase-copy phase-copy-tight">You already revealed this round.</p>
                  ) : (
                    <button
                      className="primary-button"
                      onClick={handleConfirmReveal}
                      disabled={!canConfirmReveal}
                    >
                      {selectedReveal
                        ? `Confirm ${CATEGORY_LABELS[selectedReveal]}`
                        : 'Select a category on your card'}
                    </button>
                  )}
                </>
              )
            ) : isHostView ? (
              <p className="phase-copy phase-copy-tight">
                Players are voting now. Elimination happens only after every active player votes.
              </p>
            ) : (
              <>
                <p className="phase-copy">
                  Vote for one player. Your vote locks immediately and elimination
                  happens only after every active player votes.
                </p>
                <p className="phase-copy phase-copy-tight">
                  Use the vote button on a player card below.
                </p>
              </>
            )}
          </div>

          {lastEliminated && (
            <p className="message neutral">
              Last eliminated: {lastEliminated.name} in round {lastRound.roundNumber}.
            </p>
          )}
        </section>
      ) : (
        <section className="panel-card gameplay-panel">
          <div className="round-header">
            <div>
              <p className="eyebrow">Final scoring</p>
              <h2>{game.survived ? 'Humanity survives' : 'Total failure'}</h2>
            </div>
            <span className={`phase-pill ${game.survived ? 'phase-pill-success' : 'phase-pill-danger'}`}>
              {game.finalScore} / {game.finalThreshold}
            </span>
          </div>
          <p className="phase-copy">
            All surviving cards are now fully visible. Hidden points are revealed only
            at the end.
          </p>
        </section>
      )}

      <section className="cards-section">
        <div className="cards-header">
          <p className="eyebrow">Players</p>
          {currentRound.phase === 'voting' && game.survived === null ? (
            <span className="cards-helper">
              {votesSubmitted}/{activePlayers.length} votes in
            </span>
          ) : null}
        </div>

        <div className="cards-strip">
          {game.players.map((player) => {
            const visibleCards = getVisibleCards(
              isHostView ? null : session.playerId,
              player,
              game.survived !== null,
            )
            const canVoteForPlayer =
              currentRound.phase === 'voting' &&
              !isHostView &&
              currentPlayer &&
              !currentPlayer.isEliminated &&
              !player.isEliminated &&
              player.id !== session.playerId
            const canSelectRevealCategory =
              currentRound.phase === 'reveal' &&
              !isHostView &&
              currentPlayer &&
              player.id === session.playerId &&
              !currentPlayer.isEliminated &&
              !currentPlayerHasRevealed

            return (
              <article
                key={player.id}
                className={`player-card ${player.isEliminated ? 'player-card-eliminated' : ''}`}
              >
                <div className="player-card-header">
                  <div>
                    <strong>{player.name}</strong>
                    <p>{!isHostView && player.id === session.playerId ? 'You' : `Seat ${player.seat}`}</p>
                  </div>
                  <span className="player-badge">{player.isEliminated ? 'Out' : 'In'}</span>
                </div>

                <div className="category-list">
                  {REVEAL_ORDER.map((category) => {
                    const isSelectable =
                      canSelectRevealCategory &&
                      category !== 'profession' &&
                      !currentPlayer.revealedCategories.includes(category)

                    return (
                      <button
                        key={`${player.id}-${category}`}
                        type="button"
                        className={`category-row ${isSelectable ? 'category-row-selectable' : ''} ${
                          selectedReveal === category ? 'category-row-selected' : ''
                        }`}
                        onClick={() => {
                          if (isSelectable) {
                            setSelectedReveal(category)
                          }
                        }}
                        disabled={!isSelectable}
                      >
                        <span>{CATEGORY_LABELS[category]}</span>
                        <strong>{visibleCards[category] ? visibleCards[category].name : 'Hidden'}</strong>
                      </button>
                    )
                  })}
                </div>

                {canVoteForPlayer && (
                  <button
                    className={`vote-button card-vote-button ${currentVote === player.id ? 'vote-button-selected' : ''}`}
                    onClick={() => onSubmitVote(player.id)}
                    disabled={Boolean(currentVote)}
                  >
                    {currentVote === player.id ? 'Vote submitted' : `Vote ${player.name}`}
                  </button>
                )}
              </article>
            )
          })}
        </div>
      </section>
    </main>
  )
}

export default GameScreen
