export const STORAGE_KEY = 'bunker_lobbies_v1'
export const MIN_PLAYERS = 1
export const MAX_PLAYERS = 12

export function readLobbies() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

export function writeLobbies(lobbies) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(lobbies))
}

export function saveLobby(lobby) {
  const lobbies = readLobbies()
  lobbies[lobby.code] = lobby
  writeLobbies(lobbies)
  return lobby
}

function generateCode() {
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  return Array.from({ length: 6 }, () => alphabet[Math.floor(Math.random() * alphabet.length)]).join('')
}

export function createLobby() {
  const lobbies = readLobbies()
  let code = generateCode()
  const hostId = `host-${Date.now()}`

  while (lobbies[code]) {
    code = generateCode()
  }

  const lobby = {
    code,
    status: 'waiting',
    hostId,
    hostName: 'Host',
    players: [],
  }

  lobbies[code] = lobby
  writeLobbies(lobbies)
  return lobby
}
