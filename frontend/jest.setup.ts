// frontend/jest.setup.ts
import '@testing-library/jest-dom'

// Environment variables
process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8000'
process.env.NEXT_PUBLIC_POLL_INTERVAL = '1000'
process.env.NEXT_PUBLIC_POLL_TIMEOUT = '30000'

// Mock window.open
Object.defineProperty(window, 'open', {
  writable: true,
  value: jest.fn(),
})

// Mock fetch
global.fetch = jest.fn()

// Clean up mocks
beforeEach(() => {
  jest.clearAllMocks()
})