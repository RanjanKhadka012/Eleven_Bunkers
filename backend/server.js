import cors from 'cors'
import dotenv from 'dotenv'
import express from 'express'
import { ttsHandler } from './api/tts.js'

dotenv.config()

const app = express()
const port = process.env.PORT || 5000
const allowedOrigins = process.env.ALLOWED_ORIGINS

// Allow all origins if ALLOWED_ORIGINS is unset or set to "*"; otherwise restrict to the comma list.
const corsOptions = !allowedOrigins || allowedOrigins === '*'
  ? {}
  : {
      origin: allowedOrigins.split(',').map((origin) => origin.trim()),
      methods: ['GET', 'POST', 'OPTIONS'],
    }

app.use(cors(corsOptions))
app.use(express.json({ limit: '1mb' }))

app.post('/api/tts', ttsHandler)
app.get('/health', (req, res) => {
  res.json({ status: 'ok' })
})
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' })
})

app.listen(port, () => {
  console.log(`Backend listening on port ${port}`)
})
