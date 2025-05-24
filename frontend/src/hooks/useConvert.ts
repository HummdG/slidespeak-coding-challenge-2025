import { useState } from 'react'

export type Status = 'idle' | 'ready' | 'uploading' | 'processing' | 'done' | 'error'
export interface ConvertState {
  status: Status
  file?: File
  jobId?: string
  url?: string
  error?: string
}
export interface ConvertActions {
  select(file: File): void
  upload(): Promise<void>
  complete(url: string): void
  fail(message: string): void
  reset(): void
}

export function useConvert(): [ConvertState, ConvertActions] {
  const [state, setState] = useState<ConvertState>({ status: 'idle' })

  const select = (file: File) => setState({ status: 'ready', file })
  const reset  = ()             => setState({ status: 'idle' })
  const complete = (url: string) => setState(s => ({ ...s, status: 'done', url }))
  const fail     = (msg: string) => setState({ status: 'error', error: msg })

  const upload = async () => {
    if (!state.file) return
    setState(s => ({ ...s, status: 'uploading' }))
    try {
      const form = new FormData()
      form.append('file', state.file)
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/convert`, {
        method: 'POST', body: form
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.error || 'Upload failed')
      setState(s => ({
        ...s,
        status: 'processing',
        jobId: json.jobId
      }))
    } catch (e: any) {
      fail(e.message)
    }
  }

  return [state, { select, upload, complete, fail, reset }]
}
