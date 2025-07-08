import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta charSet="utf-8" />
        {/* Circular SVG Favicons */}
        <link rel="icon" href="/favicon-16.svg" sizes="16x16" type="image/svg+xml" />
        <link rel="icon" href="/favicon-32.svg" sizes="32x32" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.svg" sizes="180x180" />
        {/* Fallback for older browsers */}
        <link rel="shortcut icon" href="/assets/logos/zusslogo.jpg" type="image/jpeg" />
        <meta name="theme-color" content="#0057FF" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </Head>
      <body className="bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const savedTheme = localStorage.getItem('zus-theme');
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                const theme = savedTheme || (prefersDark ? 'dark' : 'light');
                if (theme === 'dark') {
                  document.documentElement.classList.add('dark');
                }
              } catch (e) {}
            `,
          }}
        />
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}
