import "./globals.css";

export const metadata = {
  title: "PowerPoint to PDF Converter - SlideSpeak",
  description: "Convert your PowerPoint File to PDF quickly and efficiently.",
};

const RootLayout = async ({ children }: { children: React.ReactNode }) => (
  <html lang="en">
    <body>{children}</body>
  </html>
);

export default RootLayout;
