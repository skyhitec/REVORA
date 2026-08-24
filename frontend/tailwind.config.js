/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        fintech: {
          dark: "#0b0f19",
          card: "#131b2e",
          border: "#1e293b",
          accent: "#10b981",
          gold: "#f59e0b",
          rose: "#f43f5e",
          violet: "#8b5cf6",
          blue: "#3b82f6",
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
