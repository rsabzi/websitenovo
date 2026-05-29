import "../styles/globals.css";

export const metadata = {
  title: "Neural City Architect",
  description: "Real-time multi-agent cyberpunk city simulation",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
