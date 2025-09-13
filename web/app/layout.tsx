export const metadata = { title: "Skriptonika" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body style={{ margin:0, height:"100vh" }}>{children}</body>
    </html>
  );
}
