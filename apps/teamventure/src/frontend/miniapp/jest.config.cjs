module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  transform: {},
  collectCoverageFrom: [
    'utils/**/*.js',
    'pages/**/*.js',
    'components/**/*.js',
    '!**/node_modules/**',
    '!**/miniprogram_npm/**'
  ],
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './utils/': {
      branches: 90,
      functions: 95,
      lines: 95,
      statements: 95
    }
  },
  coverageReporters: ['text', 'text-summary', 'html', 'lcov'],
  setupFiles: ['<rootDir>/tests/setup.js']
}
