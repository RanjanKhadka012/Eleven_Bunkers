/**
 * Lobby Storage Utilities
 * Manages lobby creation and persistence using browser localStorage
 * Lobbies are stored as a map of code -> lobby_object
 * Each lobby tracks code, status, host ID, and player list
 */

/** Storage key for all lobbies in localStorage */
export const STORAGE_KEY = 'bunker_lobbies_v1'

/** Minimum number of players required to start a game */
export const MIN_PLAYERS = 2

/** Maximum number of players allowed in a lobby */
export const MAX_PLAYERS = 12

/**
 * Read all lobbies from localStorage
 * Returns empty object if storage is empty or corrupted
 * @returns {Object} Map of access code -> lobby object
 */
export function readLobbies() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    // If JSON parse fails, return empty object to avoid crashes
    return {}
  }
}

/**
 * Write all lobbies to localStorage
 * @param {Object} lobbies - Map of access code -> lobby object
 */
export function writeLobbies(lobbies) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(lobbies))
}

/**
 * Generate a random 6-character access code
 * Uses uppercase letters and numbers (no ambiguous characters like 0, 1, I, O)
 * @returns {string} Unique 6-character code
 */
function generateCode() {
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  return Array.from({ length: 6 }, () => alphabet[Math.floor(Math.random() * alphabet.length)]).join('')
}

/**
 * Create a new lobby with a unique access code
 * Initializes with host player and waiting status
 * @returns {Object} Newly created lobby object
 *   - code: unique 6-character access code
 *   - status: 'waiting' or 'started'
 *   - hostId: unique identifier for the host player
 *   - players: array of player objects
 */
export function createLobby() {
  const lobbies = readLobbies()
  let code = generateCode()
  const hostId = `host-${Date.now()}`

  // Keep generating codes until we get one that doesn't exist
  while (lobbies[code]) {
    code = generateCode()
  }

  // Create new lobby with host as first player
  const lobby = {
    code,
    status: 'waiting',
    hostId,
    players: [
      {
        id: hostId,
        name: 'Host',
        isHost: true,
      },
    ],
  }

  // Persist to localStorage
  lobbies[code] = lobby
  writeLobbies(lobbies)
  return lobby
}
