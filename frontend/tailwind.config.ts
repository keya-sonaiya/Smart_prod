import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F3ECDC",
        surface: "#FBF7EE",
        ink: "#20261F",
        inksoft: "#5B6156",
        line: "#D9CDAE",
        pine: {
          DEFAULT: "#2B4C3F",
          dark: "#1D362D",
          soft: "#DCE6DE",
        },
        rust: {
          DEFAULT: "#B5551F",
          soft: "#F1D9C4",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        sans: ["var(--font-body)", "sans-serif"],
      },
      boxShadow: {
        ticket: "0 1px 0 rgba(32,38,31,0.05), 0 8px 24px -12px rgba(32,38,31,0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
