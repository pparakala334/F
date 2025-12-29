/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"] ,
  theme: {
    extend: {
      colors: {
        surface: "#0b0f1a",
        accent: "#7c5cff",
      },
      boxShadow: {
        card: "0 20px 40px rgba(15, 23, 42, 0.08)",
      },
    },
  },
  plugins: [],
};
