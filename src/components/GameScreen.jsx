import { useEffect, useMemo, useState } from 'react'
import { CATEGORY_LABELS, REVEAL_ORDER, getVisibleCards } from '../lib/gameEngine'

const CARD_OUTLINE_COLORS = [
  '#a6c36f',
  '#d3a85d',
  '#7cb8ff',
  '#d584a7',
  '#66c1b7',
  '#caa2ff',
  '#e28d6f',
  '#8ecb6b',
]

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
  const [pendingVote, setPendingVote] = useState('')

  const revealChoices = useMemo(() => {
    if (!currentPlayer) {
      return []
    }

    return REVEAL_ORDER.filter(
      (category) =>
        category !== 'profession' && !currentPlayer.revealedCategories.includes(category),
    )
  }, [currentPlayer])

  const orderedPlayers = useMemo(() => {
    if (session.isHost) {
      return game.players
    }

    const ownIndex = game.players.findIndex((player) => player.id === session.playerId)

    if (ownIndex <= 0) {
      return game.players
    }

    return [...game.players.slice(ownIndex), ...game.players.slice(0, ownIndex)]
  }, [game.players, session.isHost, session.playerId])

  const canConfirmReveal =
    currentRound.phase === 'reveal' &&
    !isHostView &&
    currentPlayer &&
    !currentPlayer.isEliminated &&
    !currentPlayerHasRevealed &&
    Boolean(selectedReveal)

  useEffect(() => {
    if (currentRound.phase !== 'voting' || currentVote) {
      setPendingVote('')
    }
  }, [currentRound.phase, currentVote, currentRound.roundNumber])

  const handleConfirmReveal = () => {
    if (!canConfirmReveal) {
      return
    }

    onRevealCategory(selectedReveal)
    setSelectedReveal('')
  }

  return (
    <main className="page game-page">
      <section className="game-topbar game-topbar-minimal game-topbar-centered">
        <div className="game-round-heading">
          <p className="eyebrow">Round</p>
          <h2>{game.survived !== null ? 'Final result' : currentRound.roundNumber}</h2>
        </div>
      </section>

      <section className="scenario-panel">
        {game.scenario?.label && (
          <div className="scenario-item">
            <span className="info-label">Scenario</span>
            <strong>{game.scenario.label}</strong>
          </div>
        )}
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
          <p className="round-copy">
            {currentRound.phase === 'reveal'
              ? isHostView
                ? 'Players are choosing one hidden category to reveal this round.'
                : currentPlayerHasRevealed
                  ? 'You already revealed this round.'
                  : ''
              : isHostView
                ? 'Players are voting now. Elimination happens only after every active player votes.'
                : 'Select a player, then confirm your vote. Once confirmed, it locks for the round.'}
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
          {orderedPlayers.map((player, index) => {
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
                style={{ '--card-accent': CARD_OUTLINE_COLORS[index % CARD_OUTLINE_COLORS.length] }}
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
                    const isHiddenCategory = !visibleCards[category]
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
                        <strong className={isHiddenCategory ? 'category-value-hidden' : ''}>
                          {visibleCards[category] ? visibleCards[category].name : 'Hidden'}
                        </strong>
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
                    className={`vote-button card-vote-button ${
                      currentVote === player.id || pendingVote === player.id
                        ? 'vote-button-selected'
                        : ''
                    }`}
                    onClick={() => {
                      if (currentVote) {
                        return
                      }

                      if (pendingVote === player.id) {
                        onSubmitVote(player.id)
                        setPendingVote('')
                        return
                      }

                      setPendingVote(player.id)
                    }}
                    disabled={Boolean(currentVote)}
                  >
                    {currentVote === player.id
                      ? 'Vote submitted'
                      : pendingVote === player.id
                        ? `Confirm vote for ${player.name}`
                        : `Vote ${player.name}`}
                  </button>
                )}
              </article>
            )
          })}
        </div>
      </section>

      <div className="page-footer-action">
        <button className="ghost-button compact-button" onClick={onLeaveGame}>
          Leave
        </button>
      </div>
    </main>
  )
}

export default GameScreen
