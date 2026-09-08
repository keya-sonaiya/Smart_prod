import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Smart Product Recommendation Assistant",
  description: "AI-powered guidance from 'I want to do something' to 'here is everything you need.'",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
