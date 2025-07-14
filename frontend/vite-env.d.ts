/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_TEST_ENV: string
  readonly VITE_TEST_ACCESS: string
  readonly VITE_ADMIN_ACCESS: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
} 