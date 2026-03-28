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

      <section className="scenario-panel">
        <div className="scenario-item">
          <span className="info-label">Catastrophe</span>
          <strong>{game.catastrophe.name}</strong>
        </div>
        <div className="scenario-item">
          <span className="info-label">Bunker Size</span>
          <strong>{game.survivorsNeeded} survivors</strong>
        </div>
        <div className="scenario-item">
          <span className="info-label">Bunker Condition</span>
          <strong>{game.bunker.name}</strong>
        </div>
      </section>

      {game.survived === null ? (
        <section className="round-meta">
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

          <p className="round-copy">
            {currentRound.phase === 'reveal'
              ? isHostView
                ? 'Players are choosing one hidden category to reveal this round.'
                : currentPlayerHasRevealed
                  ? 'You already revealed this round.'
                  : 'Profession is already visible. Choose one other hidden category on your own card.'
              : isHostView
                ? 'Players are voting now. Elimination happens only after every active player votes.'
                : 'Vote for one player. Your vote locks immediately and elimination happens only after every active player votes.'}
          </p>

          {lastEliminated && (
            <p className="round-copy round-copy-muted">
              Last eliminated: {lastEliminated.name} in round {lastRound.roundNumber}.
            </p>
          )}
        </section>
      ) : (
        <section className="round-meta">
          <div className="result-inline">
            <span className={`phase-pill ${game.survived ? 'phase-pill-success' : 'phase-pill-danger'}`}>
              {game.finalScore} / {game.finalThreshold}
            </span>
            <p className="round-copy">
              {game.survived ? 'Humanity survives.' : 'Total failure.'} All surviving cards are
              now fully visible.
            </p>
          </div>
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
            const isOwnCard = !isHostView && player.id === session.playerId

            return (
              <article
                key={player.id}
                className={`player-card ${player.isEliminated ? 'player-card-eliminated' : ''} ${
                  isOwnCard ? 'player-card-own' : ''
                }`}
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
                          isOwnCard && selectedReveal === category ? 'category-row-selected' : ''
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

                {canSelectRevealCategory && (
                  <div className="card-action-area">
                    <button
                      className="primary-button card-confirm-button"
                      onClick={handleConfirmReveal}
                      disabled={!canConfirmReveal}
                    >
                      {selectedReveal
                        ? `Confirm ${CATEGORY_LABELS[selectedReveal]}`
                        : 'Choose a category'}
                    </button>
                  </div>
                )}

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
