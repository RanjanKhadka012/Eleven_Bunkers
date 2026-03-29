import cors from 'cors'
import dotenv from 'dotenv'
import express from 'express'
import { ttsHandler } from './api/tts.js'

dotenv.config()

const app = express()
const port = process.env.PORT || 5001
app.use(
  cors({
    origin: true,
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  }),
)
app.options('*', cors())
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
})

server.on('error', (error) => {
  if (error?.code === 'EADDRINUSE') {
    console.error(`Port ${port} is already in use. Set PORT in backend/.env to a free port and restart the server.`)
    process.exit(1)
  }

  throw error
})
