/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ark: {
          bg: '#0B0F19',        // deep obsidian
          panel: '#111827',     // slate-900 equivalent
          border: '#1E2A3A',    // subtle border
          cyan: '#22D3EE',      // cyan-400
          cyanDim: '#0E7490',   // muted cyan for grid
          crimson: '#F43F5E',   // rose-500 for damage
          silver: '#94A3B8',    // slate-400 secondary text
          gold: '#F59E0B',      // amber for peso amounts
        }
      },
      backgroundImage: {
        'dot-grid': 'radial-gradient(circle, #1E2A3A 1px, transparent 1px)'
      },
      backgroundSize: {
        'dot-grid': '24px 24px'
      }
    },
  },
  plugins: [],
}