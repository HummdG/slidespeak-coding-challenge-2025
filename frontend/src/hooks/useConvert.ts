export type Status = 'idle' | 'ready' | 'uploading' | 'processing' | 'done' | 'error'
export interface ConvertState { status: Status; jobId?: string; url?: string; error?: string }
export function useConvert() { /* returns [state, actions] */ }
