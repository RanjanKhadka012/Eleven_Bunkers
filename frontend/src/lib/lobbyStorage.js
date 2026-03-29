export const MIN_PLAYERS = 1
export const MAX_PLAYERS = 12
const lobbyEndpoint = '/api/lobbies'

async function fetchJson(url, options) {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  })

  if (!response.ok) {
    const detail = await response.text().catch(() => '')
    throw new Error(`Lobby request failed (${response.status}): ${detail}`)
  }

  return response.json()
}

function generateCode() {
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  return Array.from({ length: 6 }, () => alphabet[Math.floor(Math.random() * alphabet.length)]).join('')
}

export async function createLobby() {
  return fetchJson(lobbyEndpoint, { method: 'POST' })
}

export async function readLobby(code) {
  if (!code) return null

  try {
    return await fetchJson(`${lobbyEndpoint}/${code}`, { method: 'GET' })
  } catch (error) {
    if (String(error?.message || '').includes('404')) {
      return null
    }
    throw error
  }
}

export async function saveLobby(lobby) {
  if (!lobby?.code) {
    throw new Error('Lobby code required')
  }

  return fetchJson(`${lobbyEndpoint}/${lobby.code}`, {
    method: 'PUT',
    body: JSON.stringify(lobby),
  })
}
