import '@testing-library/jest-dom'
import 'whatwg-fetch'

process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8000'
process.env.NEXT_PUBLIC_POLL_INTERVAL = '1000'
process.env.NEXT_PUBLIC_POLL_TIMEOUT = '30000'

Object.defineProperty(window, 'open', {
  writable: true,
  value: jest.fn(),
})

global.fetch = jest.fn()

global.FormData = class MockFormData {
  constructor() {
    this.data = new Map()
  }
  
  append(key, value) {
    this.data.set(key, value)
  }
  
  get(key) {
    return this.data.get(key)
  }
}

global.File = class MockFile {
  constructor(fileBits, fileName, options = {}) {
    this.name = fileName
    this.size = options.size || 1024 * 1024 * 2.5
    this.type = options.type || 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    this.lastModified = Date.now()
  }
}

global.DataTransfer = class MockDataTransfer {
  constructor() {
    this.items = {
      add: jest.fn(),
      length: 0
    }
    this.files = []
  }
}

global.DragEvent = class MockDragEvent extends Event {
  constructor(type, eventInitDict = {}) {
    super(type, eventInitDict)
    this.dataTransfer = eventInitDict.dataTransfer || new DataTransfer()
  }
}

beforeEach(() => {
  jest.clearAllMocks()
  if (global.fetch && typeof global.fetch.mockClear === 'function') {
    global.fetch.mockClear()
  }
})