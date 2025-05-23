import './globals.css';

export const metadata = {
  title: 'PowerPoint optimizer - SlideSpeak',
  description: 'Reduce the size of your PowerPoint file without losing quality.',
};

const RootLayout = async ({ children }: { children: React.ReactNode }) => (
  <html lang="en">
    <body>{children}</body>
  </html>
);

export default RootLayout;
