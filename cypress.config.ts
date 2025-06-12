import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    // Base URL for tests
    baseUrl: 'http://localhost:4173',
    
    // Test files location
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    
    // Support file
    supportFile: 'cypress/support/e2e.ts',
    
    // Fixtures
    fixturesFolder: 'cypress/fixtures',
    
    // Screenshots and videos
    screenshotsFolder: 'cypress/screenshots',
    videosFolder: 'cypress/videos',
    
    // Video settings
    video: true,
    videoCompression: 32,
    
    // Screenshot settings
    screenshotOnRunFailure: true,
    
    // Viewport
    viewportWidth: 1280,
    viewportHeight: 720,
    
    // Timeouts
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    pageLoadTimeout: 30000,
    
    // Test isolation
    testIsolation: true,
    
    // Environment variables
    env: {
      // API endpoints
      apiUrl: 'http://localhost:8000/api',
      
      // Test user credentials
      testUser: {
        email: 'test@techzediagnostico.com',
        password: 'Test123!@#'
      },
      
      // Database
      dbUrl: 'postgresql://test:test@localhost:5432/techze_test',
      
      // Feature flags
      enableAI: true,
      enablePWA: true,
      enableNotifications: true
    },
    
    // Browser settings
    chromeWebSecurity: false,
    modifyObstructiveCode: false,
    
    // Node events
    setupNodeEvents(on, config) {
      // Tasks for database setup/teardown
      on('task', {
        // Database helpers
        async seedDatabase() {
          // Implementation for seeding test data
          return null;
        },
        
        async clearDatabase() {
          // Implementation for clearing test data
          return null;
        },
        
        // API helpers
        async createTestUser(userData) {
          // Implementation for creating test users
          return userData;
        },
        
        async deleteTestUser(userId) {
          // Implementation for deleting test users
          return null;
        },
        
        // Log messages from tests
        log(message) {
          console.log(message);
          return null;
        }
      });
      
      return config;
    }
  },
  
  // Component testing configuration
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite'
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/component.ts'
  },
  
  // Global configuration
  retries: {
    runMode: 2,
    openMode: 0
  },
  
  // Experimental features
  experimentalStudio: true,
  experimentalWebKitSupport: true
}); 