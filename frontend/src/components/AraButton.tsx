import { useState } from 'react'
import { Button } from './ui/button'
import { Mic } from 'lucide-react'

export default function AraButton() {
  const [isPlaying, setIsPlaying] = useState(false)

  const handleClick = () => {
    setIsPlaying(true)
    const ws = new WebSocket(`ws://127.0.0.1:5002`)

    const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 })

    ws.onopen = () => {
      console.log('Connected to Ara voice')
      ws.send('start')
    }

    let audioQueue: AudioBuffer[] = []
    let isPlayingAudio = false

    ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        console.log('Text from server/Ara:', event.data)
      } else {
        event.data.arrayBuffer().then((rawBuffer: ArrayBuffer) => {
          // Wrap raw PCM in WAV header (24kHz, 16-bit, mono)
          const sampleRate = 24000
          const numChannels = 1
          const bitsPerSample = 16
          const byteRate = sampleRate * numChannels * (bitsPerSample / 8)
          const blockAlign = numChannels * (bitsPerSample / 8)
          const dataSize = rawBuffer.byteLength
          const wavBuffer = new ArrayBuffer(44 + dataSize)
          const view = new DataView(wavBuffer)

          // RIFF header
          view.setUint32(0, 0x52494646, false) // 'RIFF'
          view.setUint32(4, 36 + dataSize, true)
          view.setUint32(8, 0x57415645, false) // 'WAVE'

          // fmt chunk
          view.setUint32(12, 0x666d7420, false) // 'fmt '
          view.setUint32(16, 16, true)
          view.setUint16(20, 1, true) // PCM
          view.setUint16(22, numChannels, true)
          view.setUint32(24, sampleRate, true)
          view.setUint32(28, byteRate, true)
          view.setUint16(32, blockAlign, true)
          view.setUint16(34, bitsPerSample, true)

          // data chunk
          view.setUint32(36, 0x64617461, false) // 'data'
          view.setUint32(40, dataSize, true)

          // Copy raw PCM data
          const rawBytes = new Uint8Array(rawBuffer)
          new Uint8Array(wavBuffer, 44, dataSize).set(rawBytes)

          console.log('Received audio chunk', rawBytes.length, 'bytes (wrapped in WAV)')

          audioCtx.decodeAudioData(wavBuffer, (decodedBuffer: AudioBuffer) => {
            audioQueue.push(decodedBuffer)
            if (!isPlayingAudio) playNextChunk()
          }, (err: DOMException) => {
            console.error('Decode error:', err)
          })
        }).catch((err: Error) => {
          console.error('ArrayBuffer error:', err)
        })
      }
    }

    function playNextChunk() {
      if (audioQueue.length === 0) {
        isPlayingAudio = false
        setIsPlaying(false)
        return
      }
      isPlayingAudio = true
      const buffer = audioQueue.shift()!
      const source = audioCtx.createBufferSource()
      source.buffer = buffer
      source.connect(audioCtx.destination)
      source.onended = () => playNextChunk()
      source.start()
    }

    ws.onclose = () => {
      setIsPlaying(false)
    }
  }

  return (
    <Button
      onClick={handleClick}
      disabled={isPlaying}
      className="bg-accent-cyan hover:bg-accent-cyan/80 text-black font-semibold px-6 py-3 text-lg shadow-lg hover:shadow-glow transition-all duration-200 disabled:opacity-50"
    >
      <Mic className="w-5 h-5 mr-2" />
      {isPlaying ? 'Playing Ara Report...' : 'Get Ara Voice Report'}
    </Button>
  )
}