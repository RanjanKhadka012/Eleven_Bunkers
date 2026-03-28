export async function ttsHandler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' })
    return
  }

  const apiKey = process.env.ELEVENLABS_API_KEY
  if (!apiKey) {
    res.status(500).json({ error: 'Missing ELEVENLABS_API_KEY' })
    return
  }

  const { text, voiceId, modelId } = req.body || {}
  const resolvedVoiceId = voiceId || process.env.ELEVENLABS_VOICE_ID || '21m00Tcm4TlvDq8ikWAM'
  const resolvedModelId = modelId || 'eleven_multilingual_v2'

  if (!text || typeof text !== 'string') {
    res.status(400).json({ error: 'text is required' })
    return
  }

  try {
    const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${resolvedVoiceId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'xi-api-key': apiKey,
      },
      body: JSON.stringify({ text, model_id: resolvedModelId }),
    })

    if (!response.ok) {
      const detail = await response.text().catch(() => '')
      res.status(response.status).json({ error: `TTS failed (${response.status}): ${detail}` })
      return
    }

    const audioBuffer = Buffer.from(await response.arrayBuffer())
    res.setHeader('Content-Type', 'audio/mpeg')
    res.setHeader('Cache-Control', 'no-store')
    res.status(200).send(audioBuffer)
  } catch (error) {
    res.status(500).json({ error: error?.message || 'TTS request failed' })
  }
}
