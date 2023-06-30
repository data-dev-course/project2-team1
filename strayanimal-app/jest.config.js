/** @type {import('jest').Config} */
const config = {
    rootDir: "./strayanimal",
    transform: {
        "^.+\\.(js|jsx)?$": "babel-jest",
    },
    testEnvironment: "jsdom",
    collectCoverage: true,
    collectCoverageFrom: ['<rootDir>/src/**/*.{js,jsx}'],
    coverageDirectory: 'coverage',
    testMatch: [
        "<rootDir>/**/*.test.(js|jsx)",
        "<rootDir>/(tests/unit/**/*.spec.(js|jsx)|**/__tests__/*.(js|jsx))",
    ],
    moduleNameMapper: {
        '\\.(css|less)$': '<rootDir>/jest/__mocks__/styleMock.js',
    },
    setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
};
export default config;