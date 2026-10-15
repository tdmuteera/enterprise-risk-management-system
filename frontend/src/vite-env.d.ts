/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** When true, API base is same origin (desktop / Electron bundle). */
  readonly VITE_USE_RELATIVE_API?: string
  readonly VITE_API_BASE_URL?: string
  readonly VITE_APP_TITLE?: string
  readonly VITE_APP_VERSION?: string
  readonly VITE_PORT?: string
  /** @deprecated use VITE_API_BASE_URL; base should include /api/v1 via app logic */
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
