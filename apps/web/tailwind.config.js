/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"] ,
  theme: {
    extend: {
      colors: {
        cream: "#f6f1e8",
        charcoal: "#1f1f1f",
      },
      boxShadow: {
        card: "0 20px 40px rgba(15, 23, 42, 0.08)",
      },
    },
  },
  plugins: [],
};
