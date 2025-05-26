import "./globals.css";

export const metadata = {
  title: "PowerPoint to PDF Converter - SlideSpeak",
  description: "Convert your PowerPoint File to PDF quickly and efficiently.",
};

async function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
export default RootLayout;
