import cors from 'cors'
import dotenv from 'dotenv'
import express from 'express'
import { outcomeSummaryHandler } from './api/outcomeSummary.js'
import { ttsHandler } from './api/tts.js'

dotenv.config()

const app = express()
const port = Number(process.env.PORT) || 8080
const lobbies = new Map()

const corsOptions = {
  origin: true,
  methods: ['GET', 'POST', 'PUT', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}

console.log('[config] starting backend', {
  port,
  corsOrigins: corsOptions.origin,
})

app.use(cors(corsOptions))
app.options('*', cors(corsOptions))
app.use(express.json({ limit: '1mb' }))

function generateCode() {
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  return Array.from({ length: 6 }, () => alphabet[Math.floor(Math.random() * alphabet.length)]).join('')
}

function createLobby() {
  let code = generateCode()

  while (lobbies.has(code)) {
    code = generateCode()
  }

  const lobby = {
    code,
    status: 'waiting',
    hostId: `host-${Date.now()}`,
    hostName: 'Host',
    players: [],
    updatedAt: Date.now(),
  }

  lobbies.set(code, lobby)
  return lobby
}

app.post('/api/lobbies', (req, res) => {
  const lobby = createLobby()
  console.log('[lobby] created', { code: lobby.code, players: lobby.players.length })
  res.status(201).json(lobby)
})

app.get('/api/lobbies/:code', (req, res) => {
  const lobby = lobbies.get(req.params.code?.trim())

  console.log('[lobby] fetch', { code: req.params.code?.trim(), found: Boolean(lobby) })

  if (!lobby) {
    res.status(404).json({ error: 'Lobby not found' })
    return
  }

  res.json(lobby)
})

app.put('/api/lobbies/:code', (req, res) => {
  const code = req.params.code?.trim()
  const lobby = req.body

  console.log('[lobby] update request', { code, hasBody: Boolean(lobby) })

  if (!code || !lobby || lobby.code !== code) {
    res.status(400).json({ error: 'Invalid lobby payload' })
    return
  }

  lobbies.set(code, { ...lobby, updatedAt: Date.now() })
  console.log('[lobby] updated', { code, players: lobby.players?.length ?? 0, status: lobby.status })
  res.json(lobbies.get(code))
})

app.post('/api/tts', ttsHandler)
app.post('/api/outcome-summary', outcomeSummaryHandler)
app.get('/health', (req, res) => {
  res.json({ status: 'ok' })
})
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' })
})

const server = app.listen(port, () => {
  console.log(`Backend listening on port ${port}`)
  console.log('Server has started and is ready to receive requests')
})

server.on('error', (error) => {
  if (error?.code === 'EADDRINUSE') {
    console.error(`Port ${port} is already in use. Set PORT in backend/.env to a free port and restart the server.`)
    process.exit(1)
  }

  throw error
})
