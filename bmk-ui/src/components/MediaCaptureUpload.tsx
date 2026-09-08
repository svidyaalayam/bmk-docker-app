import { useEffect, useMemo, useRef, useState } from 'react'
import { getErrorMessage } from '../utils/errors'

type Props = { label: string; onUpload: (file: File) => Promise<void>; maxBytes: number }
type Dialog = 'camera' | 'audio' | null

function fileProblem(file: File, maxBytes: number) {
  if (!(file.type.startsWith('image/') || file.type.startsWith('audio/') || file.type === 'application/pdf')) return 'Choose an image, audio recording, or PDF file.'
  return file.size > maxBytes ? `This file is too large. The maximum size is ${Math.floor(maxBytes / 1024 / 1024)} MB.` : null
}

export default function MediaCaptureUpload({ label, onUpload, maxBytes }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  const waveRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const animationRef = useRef<number | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const [dialog, setDialog] = useState<Dialog>(null)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  const [recording, setRecording] = useState(false)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)
  const imageUrl = useMemo(() => imageFile && URL.createObjectURL(imageFile), [imageFile])
  const audioUrl = useMemo(() => audioFile && URL.createObjectURL(audioFile), [audioFile])

  const stopMedia = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null; setCameraStream(null)
    if (animationRef.current !== null) cancelAnimationFrame(animationRef.current)
    animationRef.current = null
    audioContextRef.current?.close().catch(() => undefined)
    audioContextRef.current = null; analyserRef.current = null
  }

  useEffect(() => () => stopMedia(), [])
  useEffect(() => () => { if (imageUrl) URL.revokeObjectURL(imageUrl) }, [imageUrl])
  useEffect(() => () => { if (audioUrl) URL.revokeObjectURL(audioUrl) }, [audioUrl])
  useEffect(() => {
    if (dialog === 'camera' && cameraStream && videoRef.current) {
      videoRef.current.srcObject = cameraStream
      videoRef.current.play().catch(() => setError('The camera preview could not start.'))
    }
  }, [dialog, cameraStream])
  useEffect(() => {
    if (!recording || !analyserRef.current || !waveRef.current) return
    const analyser = analyserRef.current; const canvas = waveRef.current; const ctx = canvas.getContext('2d'); const values = new Uint8Array(analyser.fftSize)
    const draw = () => {
      if (!ctx) return
      analyser.getByteTimeDomainData(values); ctx.fillStyle = '#102a43'; ctx.fillRect(0, 0, canvas.width, canvas.height)
      ctx.strokeStyle = '#4fd1c5'; ctx.lineWidth = 2; ctx.beginPath()
      values.forEach((value, index) => { const x = index / (values.length - 1) * canvas.width; const y = value / 255 * canvas.height; index ? ctx.lineTo(x, y) : ctx.moveTo(x, y) })
      ctx.stroke(); animationRef.current = requestAnimationFrame(draw)
    }
    draw()
    return () => { if (animationRef.current !== null) cancelAnimationFrame(animationRef.current) }
  }, [recording])

  const upload = async (file: File) => {
    const problem = fileProblem(file, maxBytes)
    if (problem) { setError(problem); return false }
    setUploading(true); setError('')
    try { await onUpload(file); setImageFile(null); setAudioFile(null); return true }
    catch (err) { setError(getErrorMessage(err, 'Upload could not be completed.')); return false }
    finally { setUploading(false) }
  }
  const openCamera = async () => {
    setError(''); setImageFile(null); setDialog('camera')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } } })
      streamRef.current = stream; setCameraStream(stream)
    } catch { setError('Camera access was not granted or no camera is available. You can still choose an image file.') }
  }
  const capture = () => {
    const video = videoRef.current
    if (!video?.videoWidth || !video.videoHeight) { setError('The camera is still starting. Please try again in a moment.'); return }
    const canvas = document.createElement('canvas'); canvas.width = video.videoWidth; canvas.height = video.videoHeight
    canvas.getContext('2d')?.drawImage(video, 0, 0)
    canvas.toBlob((blob) => { if (blob) setImageFile(new File([blob], `camera-${Date.now()}.jpg`, { type: 'image/jpeg' })) }, 'image/jpeg', 0.92)
    stopMedia()
  }
  const crop = () => {
    const image = imageRef.current
    if (!image?.naturalWidth || !image.naturalHeight) return
    const side = Math.min(image.naturalWidth, image.naturalHeight); const canvas = document.createElement('canvas'); canvas.width = Math.min(side, 1200); canvas.height = Math.min(side, 1200)
    canvas.getContext('2d')?.drawImage(image, (image.naturalWidth - side) / 2, (image.naturalHeight - side) / 2, side, side, 0, 0, canvas.width, canvas.height)
    canvas.toBlob((blob) => { if (blob) setImageFile(new File([blob], `cropped-${Date.now()}.jpg`, { type: 'image/jpeg' })) }, 'image/jpeg', 0.92)
  }
  const startRecording = async () => {
    setError(''); setAudioFile(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); streamRef.current = stream
      const audioContext = new AudioContext(); audioContextRef.current = audioContext; const analyser = audioContext.createAnalyser(); analyser.fftSize = 2048; audioContext.createMediaStreamSource(stream).connect(analyser); analyserRef.current = analyser
      const recorder = new MediaRecorder(stream); chunksRef.current = []; recorder.ondataavailable = (event) => { if (event.data.size) chunksRef.current.push(event.data) }
      recorder.onstop = () => { const type = recorder.mimeType || 'audio/webm'; setAudioFile(new File([new Blob(chunksRef.current, { type })], `recording-${Date.now()}.webm`, { type })); stopMedia() }
      recorderRef.current = recorder; recorder.start(); setRecording(true)
    } catch { setError('Microphone access was not granted or no microphone is available. You can still choose an audio file.') }
  }
  const stopRecording = () => { recorderRef.current?.stop(); recorderRef.current = null; setRecording(false) }
  const cancel = () => { if (recording) stopRecording(); else stopMedia(); setDialog(null); setImageFile(null); setAudioFile(null) }
  const uploadAndClose = async (file: File) => { if (await upload(file)) setDialog(null) }

  return <div className="media-capture-upload">
    <label className="file-upload">{label}<input type="file" accept="image/*,application/pdf,audio/*" onChange={(event) => { const file = event.target.files?.[0]; if (file) upload(file); event.target.value = '' }} /></label>
    <button type="button" className="home-btn secondary" onClick={openCamera}>Take photo</button>
    <button type="button" className="home-btn secondary" onClick={() => { setError(''); setAudioFile(null); setDialog('audio') }}>Record audio</button>
    {error && !dialog && <p className="error">{error}</p>}
    {dialog && <div className="modal-backdrop" role="presentation" onClick={cancel}><div className="dash-panel edit-user-modal media-capture-modal" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
      <h2>{dialog === 'camera' ? 'Take a photo' : 'Record audio'}</h2>{error && <p className="error">{error}</p>}
      {dialog === 'camera' && (imageFile ? <><img ref={imageRef} src={imageUrl || undefined} alt="Photo preview" className="media-dialog-preview" /><p className="header-sub">Preview your photo. Crop creates a centred square image.</p><div className="form-actions"><button type="button" className="tab" onClick={crop}>Crop to square</button><button type="button" disabled={uploading} onClick={() => uploadAndClose(imageFile)}>{uploading ? 'Uploading…' : 'OK and upload'}</button><button type="button" className="tab" onClick={cancel}>Cancel</button></div></> : <><video ref={videoRef} autoPlay playsInline muted className="media-dialog-preview" /><div className="form-actions"><button type="button" onClick={capture} disabled={!cameraStream}>Capture photo</button><button type="button" className="tab" onClick={cancel}>Cancel</button></div></>)}
      {dialog === 'audio' && <>{recording && <><p className="recording-status">● Recording in progress</p><canvas ref={waveRef} className="audio-waveform" width="640" height="140" /></>}{audioFile && audioUrl && <audio controls src={audioUrl} />}<div className="form-actions">{!recording && !audioFile && <button type="button" onClick={startRecording}>Start recording</button>}{recording && <button type="button" onClick={stopRecording}>Stop recording</button>}{audioFile && <><button type="button" className="tab" onClick={startRecording}>Record again</button><button type="button" disabled={uploading} onClick={() => uploadAndClose(audioFile)}>{uploading ? 'Uploading…' : 'OK and upload'}</button></>}<button type="button" className="tab" onClick={cancel}>Cancel</button></div></>}
    </div></div>}
  </div>
}
