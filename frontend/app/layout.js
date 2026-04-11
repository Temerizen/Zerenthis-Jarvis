export default function RootLayout({ children }) {
  return (
    <html>
      <body style={{ background: "#0a0a0a", color: "white", fontFamily: "Arial, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
