export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, background: "#0b1020", color: "#e8ecf3", fontFamily: "Arial, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
