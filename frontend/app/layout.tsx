import "./globals.css";
import type { Metadata } from "next";
import { Big_Shoulders_Display, IBM_Plex_Sans } from "next/font/google";

const display = Big_Shoulders_Display({
  subsets: ["latin"],
  weight: ["600", "700"],
  variable: "--font-display",
});

const body = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  title: "Smart Product Recommendation Assistant",
  description: "From 'I want to build a dining table' to a complete, quantity-accurate parts list.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
