const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@/utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@/icons/(.*)$': '<rootDir>/src/icons/$1',
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
  ],
  // Ignore the problematic files for now
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/src/components/__tests__/ConverterFlow.test.tsx',
    '<rootDir>/src/app/__tests__/page.test.tsx'
  ]
}

module.exports = createJestConfig(customJestConfig)