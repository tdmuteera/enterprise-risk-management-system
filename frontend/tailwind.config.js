import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        risk: {
          critical: '#D32F2F',
          high: '#F57C00',
          medium: '#FBC02D',
          low: '#388E3C',
        },
        brand: {
          dark: '#152B52',
          mid: '#2E75B6',
          light: '#E8F1FA',
          accent: '#4A9FD9',
        },
        surface: {
          DEFAULT: '#F5F7FB',
          card: '#FFFFFF',
          muted: '#EEF2F8',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        display: ['Sora', 'system-ui', 'sans-serif'],
      },
      backgroundColor: {
        page: '#F0F3F9',
      },
      boxShadow: {
        shell: '0 1px 0 rgba(15, 23, 42, 0.06), 0 12px 40px -24px rgba(21, 43, 82, 0.35)',
        nav: '0 4px 24px -8px rgba(15, 23, 42, 0.12)',
        sidebar: '4px 0 32px -12px rgba(0, 0, 0, 0.25)',
      },
      backgroundImage: {
        'sidebar-gradient': 'linear-gradient(165deg, #152B52 0%, #0F2140 48%, #0A162E 100%)',
        'sidebar-shine': 'linear-gradient(180deg, rgba(74, 159, 217, 0.12) 0%, transparent 42%)',
      },
    },
  },
  plugins: [],
} satisfies Config
