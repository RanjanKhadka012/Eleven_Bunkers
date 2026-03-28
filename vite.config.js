/**
 * Vite Configuration
 * Defines build and development server settings for the React app
 */

import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

function elevenLabsDevApi(env) {
  return {
    name: 'elevenlabs-dev-api',
    configureServer(server) {
      server.middlewares.use('/api/tts', async (req, res, next) => {
        if (req.method !== 'POST') {
          next()
          return
        }

        const apiKey = env.ELEVENLABS_API_KEY

        if (!apiKey) {
          res.statusCode = 500
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({ error: 'Missing ELEVENLABS_API_KEY' }))
          return
        }

        const chunks = []
        for await (const chunk of req) {
          chunks.push(chunk)
        }

        let body = {}
        try {
          body = chunks.length ? JSON.parse(Buffer.concat(chunks).toString('utf8')) : {}
        } catch {
          body = {}
        }

        const text = body?.text
        const voiceId = body?.voiceId || env.ELEVENLABS_VOICE_ID || '21m00Tcm4TlvDq8ikWAM'
        const modelId = body?.modelId || 'eleven_multilingual_v2'

        if (!text || typeof text !== 'string') {
          res.statusCode = 400
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({ error: 'text is required' }))
          return
        }

        try {
          const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'xi-api-key': apiKey,
            },
            body: JSON.stringify({ text, model_id: modelId }),
          })

          if (!response.ok) {
            const detail = await response.text().catch(() => '')
            res.statusCode = response.status
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ error: `TTS failed (${response.status}): ${detail}` }))
            return
          }

          const audioBuffer = Buffer.from(await response.arrayBuffer())
          res.statusCode = 200
          res.setHeader('Content-Type', 'audio/mpeg')
          res.setHeader('Cache-Control', 'no-store')
          res.end(audioBuffer)
        } catch (error) {
          res.statusCode = 500
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({ error: error?.message || 'TTS request failed' }))
        }
      })
    },
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react(), elevenLabsDevApi(env)],
    server: {
      port: 3000,
    },
  }
})
