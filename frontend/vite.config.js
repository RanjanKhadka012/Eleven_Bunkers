/**
 * Vite Configuration
 * Defines build and development server settings for the React app
 */

import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  // Enable React plugin for JSX support and fast refresh
  plugins: [react()],
  
  server: {
    // Development server port
    port: 3000,
  }
})
