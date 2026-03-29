import {
  BUNKERS,
  CARD_POOLS,
  CATEGORY_LABELS,
  CATASTROPHES,
  REVEAL_ORDER,
  THRESHOLD_RULES,
} from './gameData'
import { pickScenarioForCatastrophe } from './scenarioNarratives'

export const DISCUSSION_DURATION_MS = 90 * 1000

function randomItem(items) {
  return items[Math.floor(Math.random() * items.length)]
}

function getSurvivorTarget(playerCount) {
  if (playerCount <= 3) return 2
  if (playerCount <= 5) return 3
  if (playerCount <= 7) return 4
  if (playerCount <= 9) return 5
  if (playerCount <= 11) return 6
  return 7
}

function buildRoundState(roundIndex) {
  return {
    roundIndex,
    roundNumber: roundIndex + 1,
    phase: 'reveal',
    revealedBy: [],
    votes: {},
    eliminatedPlayerId: null,
    discussionEndsAt: null,
  }
}

function getTotalRounds(playerCount, survivorsNeeded) {
  return Math.max(0, playerCount - survivorsNeeded)
}

function getActivePlayers(players) {
  return players.filter((player) => !player.isEliminated)
}

function calculatePlayerScore(cards) {
  return Object.values(cards).reduce((total, card) => total + card.points, 0)
}

function calculateThreshold(survivorsNeeded, catastropheModifier, bunkerModifier) {
  const baseThreshold = survivorsNeeded * THRESHOLD_RULES.basePerSurvivor
  const weightedModifiers = Math.round(
    (catastropheModifier + bunkerModifier) * THRESHOLD_RULES.modifierWeight,
  )

  return {
    baseThreshold,
    finalThreshold: Math.max(0, baseThreshold + weightedModifiers),
  }
}

function drawCard(category) {
  return randomItem(CARD_POOLS[category])
}

export function startLobbyGame(lobby) {
  const catastrophe = randomItem(CATASTROPHES)
  const scenario = pickScenarioForCatastrophe(catastrophe.name)
  const bunker = randomItem(BUNKERS)
  const survivorsNeeded = Math.max(
    1,
    Math.min(getSurvivorTarget(lobby.players.length), lobby.players.length || 1),
  )
  const { baseThreshold, finalThreshold } = calculateThreshold(
    survivorsNeeded,
    catastrophe.modifier,
    bunker.modifier,
  )
  const totalRounds = getTotalRounds(lobby.players.length, survivorsNeeded)

  const players = lobby.players.map((player, index) => {
    const cards = Object.fromEntries(
      REVEAL_ORDER.map((category) => [category, drawCard(category)]),
    )

    return {
      ...player,
      seat: index + 1,
      isEliminated: false,
      eliminatedRound: null,
      revealedCategories: ['profession'],
      cards,
      score: calculatePlayerScore(cards),
    }
  })

  return {
    ...lobby,
    status: 'in_progress',
    game: {
      catastrophe,
      bunker,
      scenario,
      survivorsNeeded,
      baseThreshold,
      finalThreshold,
      finalScore: null,
      survived: null,
      totalRounds,
      revealOrder: REVEAL_ORDER,
      currentRound: buildRoundState(0),
      completedRounds: [],
      players,
    },
  }
}

export function revealForPlayer(lobby, playerId, category) {
  if (!lobby.game || lobby.game.currentRound.phase !== 'reveal') {
    return lobby
  }

  if (
    !category ||
    category === 'profession' ||
    !REVEAL_ORDER.includes(category) ||
    lobby.game.currentRound.revealedBy.includes(playerId)
  ) {
    return lobby
  }

  const players = lobby.game.players.map((player) =>
    player.id === playerId
      ? {
          ...player,
          revealedCategories: player.revealedCategories.includes(category)
            ? player.revealedCategories
            : [...player.revealedCategories, category],
        }
      : player,
  )

  const revealedBy = [...lobby.game.currentRound.revealedBy, playerId]
  const activePlayers = getActivePlayers(players)
  const everyoneRevealed = activePlayers.every((player) => revealedBy.includes(player.id))

  return {
    ...lobby,
    game: {
      ...lobby.game,
      players,
      currentRound: {
        ...lobby.game.currentRound,
        revealedBy,
        phase: everyoneRevealed ? 'discussion' : 'reveal',
        discussionEndsAt: everyoneRevealed ? Date.now() + DISCUSSION_DURATION_MS : null,
      },
    },
  }
}

export function advanceDiscussionPhase(lobby, now = Date.now()) {
  if (!lobby?.game || lobby.game.currentRound.phase !== 'discussion') {
    return lobby
  }

  const { discussionEndsAt } = lobby.game.currentRound
  if (!discussionEndsAt || now < discussionEndsAt) {
    return lobby
  }

  return {
    ...lobby,
    game: {
      ...lobby.game,
      currentRound: {
        ...lobby.game.currentRound,
        phase: 'voting',
      },
    },
  }
}

function resolveVotingRound(game) {
  const activePlayers = getActivePlayers(game.players)
  const voteCounts = {}

  Object.values(game.currentRound.votes).forEach((targetId) => {
    voteCounts[targetId] = (voteCounts[targetId] ?? 0) + 1
  })

  const eliminatedPlayer = activePlayers
    .filter((player) => voteCounts[player.id])
    .sort((left, right) => {
      const diff = voteCounts[right.id] - voteCounts[left.id]
      if (diff !== 0) {
        return diff
      }
      return left.seat - right.seat
    })[0]

  const players = game.players.map((player) =>
    player.id === eliminatedPlayer.id
      ? {
          ...player,
          isEliminated: true,
          eliminatedRound: game.currentRound.roundNumber,
        }
      : player,
  )

  const completedRound = {
    ...game.currentRound,
    eliminatedPlayerId: eliminatedPlayer.id,
  }

  const survivors = getActivePlayers(players)
  const endNow =
    survivors.length <= game.survivorsNeeded ||
    game.currentRound.roundIndex === game.totalRounds - 1

  if (endNow) {
    const finalScore = survivors.reduce((sum, player) => sum + player.score, 0)
    return {
      ...game,
      players,
      completedRounds: [...game.completedRounds, completedRound],
      currentRound: {
        ...completedRound,
        phase: 'completed',
      },
      finalScore,
      survived: finalScore >= game.finalThreshold,
    }
  }

  return {
    ...game,
    players,
    completedRounds: [...game.completedRounds, completedRound],
    currentRound: buildRoundState(game.currentRound.roundIndex + 1),
  }
}

export function castVoteForPlayer(lobby, voterId, targetId) {
  if (!lobby.game || lobby.game.currentRound.phase !== 'voting') {
    return lobby
  }

  if (voterId === targetId || lobby.game.currentRound.votes[voterId]) {
    return lobby
  }

  const activePlayers = getActivePlayers(lobby.game.players)
  const validVoter = activePlayers.some((player) => player.id === voterId)
  const validTarget = activePlayers.some((player) => player.id === targetId)

  if (!validVoter || !validTarget) {
    return lobby
  }

  const game = {
    ...lobby.game,
    currentRound: {
      ...lobby.game.currentRound,
      votes: {
        ...lobby.game.currentRound.votes,
        [voterId]: targetId,
      },
    },
  }

  const allVotesIn = activePlayers.every((player) => game.currentRound.votes[player.id])
  const resolvedGame = allVotesIn ? resolveVotingRound(game) : game

  return {
    ...lobby,
    status: resolvedGame.survived === null ? 'in_progress' : 'completed',
    game: resolvedGame,
  }
}

export function getVisibleCards(viewerId, player, revealEverything = false) {
  return Object.fromEntries(
    REVEAL_ORDER.map((category) => {
      const visible =
        revealEverything ||
        category === 'profession' ||
        viewerId === player.id ||
        player.revealedCategories.includes(category)

      return [category, visible ? player.cards[category] : null]
    }),
  )
}

export function pauseDiscussion(lobby, now = Date.now()) {
  if (!lobby?.game || lobby.game.currentRound.phase !== 'discussion') {
    return lobby
  }

  const { discussionEndsAt } = lobby.game.currentRound
  if (!discussionEndsAt) {
    return lobby
  }

  const remainingMs = Math.max(0, discussionEndsAt - now)

  return {
    ...lobby,
    game: {
      ...lobby.game,
      currentRound: {
        ...lobby.game.currentRound,
        discussionEndsAt: null,
        discussionPausedRemaining: remainingMs,
      },
    },
  }
}

export function resumeDiscussion(lobby, now = Date.now()) {
  if (!lobby?.game || lobby.game.currentRound.phase !== 'discussion') {
    return lobby
  }

  if (lobby.game.currentRound.discussionEndsAt) {
    return lobby
  }

  const remainingMs =
    lobby.game.currentRound.discussionPausedRemaining ?? DISCUSSION_DURATION_MS

  return {
    ...lobby,
    game: {
      ...lobby.game,
      currentRound: {
        ...lobby.game.currentRound,
        discussionEndsAt: now + remainingMs,
        discussionPausedRemaining: null,
      },
    },
  }
}

export function skipToVoting(lobby) {
  if (!lobby?.game || lobby.game.currentRound.phase !== 'discussion') {
    return lobby
  }

  return {
    ...lobby,
    game: {
      ...lobby.game,
      currentRound: {
        ...lobby.game.currentRound,
        phase: 'voting',
        discussionEndsAt: null,
        discussionPausedRemaining: null,
      },
    },
  }
}

export { CATEGORY_LABELS, REVEAL_ORDER }
