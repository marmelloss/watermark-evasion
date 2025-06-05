import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()], // Enable React plugin for Vite

  resolve: {
    alias: {
      '@': '/src', // Maps @ to the src/ directory
    },
    extensions: ['.js', '.jsx'], // Support for .js and .jsx files
  },

  server: {
    port: 5173, // Port for the development server
    strictPort: true, // Prevent fallback to other ports
    host: true, // Listen on all network interfaces
    open: true, // Automatically open the browser
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Proxy API requests to this target
        changeOrigin: true,
        secure: false, // Allow self-signed certificates in development
        rewrite: (path) => path.replace(/^\/api/, ''), // Rewrite paths
        ws: true, // Enable WebSocket support
      },
    },
  },

  build: {
    outDir: 'dist', // Output directory for production build
    emptyOutDir: true, // Clear the output directory before building
    sourcemap: true, // Generate source maps for debugging
    minify: 'terser', // Use Terser for minification
    rollupOptions: {
      input: './index.html', // Entry point for the build
      output: {
        entryFileNames: 'assets/[name].[hash].js', // Format for entry chunks
        chunkFileNames: 'assets/[name].[hash].js', // Format for shared chunks
        assetFileNames: 'assets/[name].[hash].[ext]', // Format for assets
        manualChunks: {
          react: ['react', 'react-dom'], // Separate React into its own bundle
        },
      },
    },
  },
});
