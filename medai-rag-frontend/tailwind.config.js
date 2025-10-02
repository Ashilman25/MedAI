/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html","./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        medical: { blue: "#3B82F6", green: "#10B981", warn: "#F59E0B", danger: "#EF4444" }
      },
      boxShadow: { card: "0 8px 30px rgba(0,0,0,0.06)" },
      borderRadius: { '2xl': '1.25rem' }
    }
  },
  plugins: [require('@tailwindcss/forms')]
}
