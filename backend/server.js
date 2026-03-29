import cors from 'cors'
import dotenv from 'dotenv'
import express from 'express'
import { ttsHandler } from './api/tts.js'

dotenv.config()

const app = express()
const port = Number(process.env.PORT) || 8080 || 5000 ||5001
const allowList = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(',').map((value) => value.trim()).filter(Boolean)
  : null

const corsOptions = {
  origin: allowList && allowList.length > 0 ? allowList : true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}

console.log('[config] starting backend', {
  port,
  corsOrigins: corsOptions.origin,
})

app.use(cors(corsOptions))
app.options('*', cors(corsOptions))
app.use(express.json({ limit: '1mb' }))

app.post('/api/tts', ttsHandler)
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
