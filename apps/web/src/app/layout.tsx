import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EstateGuard — Governed Control Plane for Mixed Git Estates",
  description:
    "Security posture, living architecture, and institutional knowledge across GitHub, GitLab, and Bitbucket.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
