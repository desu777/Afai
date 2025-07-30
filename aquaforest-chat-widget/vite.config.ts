import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// ALEX ELITE CONDITIONAL CONFIG
export default defineConfig(({ command, mode }) => {
  console.log(`🚀 ALEX BUILD MODE: ${command} (${mode})`);
  
  // ALEX SMART CONDITIONAL LOGIC
  if (command === 'build') {
    console.log('🏗️  PRODUCTION BUILD - Hardcoding environment variables');
    return {
      plugins: [react()],
      resolve: {
        alias: {
          './globalThis-config.mjs': './globalThis-config.js'
        }
      },
      define: {
        'global': 'globalThis',
        'process.env.NODE_ENV': '"production"',
        'process.env.TEST_ENV': '"false"',
        'process.env': '{}', 
        '__DEV__': false,
      },
      build: {
        lib: {
          entry: resolve(__dirname, 'src/widget.tsx'),
          name: 'AquaforestChatWidget',
          fileName: 'aquaforest-chat-widget',
          formats: ['umd'] as const
        },
        rollupOptions: {
          external: ['react', 'react-dom'],
          output: {
            globals: {
              'react': 'React',
              'react-dom': 'ReactDOM'
            }
          }
        },
        cssCodeSplit: false,
        outDir: 'dist'
      }
    };
  } else {
    console.log('⚡ DEVELOPMENT MODE - Using dynamic environment variables');
    return {
      plugins: [react()],
      resolve: {
        alias: {
          './globalThis-config.mjs': './globalThis-config.js'
        }
      },
      define: {
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
        'process.env.TEST_ENV': JSON.stringify(process.env.TEST_ENV || 'false'),
        'global': 'globalThis',
        '__DEV__': mode === 'development',
      },
      build: {
        lib: {
          entry: resolve(__dirname, 'src/widget.tsx'),
          name: 'AquaforestChatWidget',
          fileName: 'aquaforest-chat-widget',
          formats: ['umd'] as const
        },
        rollupOptions: {
          external: ['react', 'react-dom'],
          output: {
            globals: {
              'react': 'React',
              'react-dom': 'ReactDOM'
            }
          }
        },
        cssCodeSplit: false,
        outDir: 'dist'
      }
    };
  }
});
