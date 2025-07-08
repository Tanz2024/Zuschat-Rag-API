import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta charSet="utf-8" />
        {/* Enhanced Font Loading - Fixed from index.tsx warning */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
        
        {/* Circular SVG Favicons */}
        <link rel="icon" href="/favicon-16.svg" sizes="16x16" type="image/svg+xml" />
        <link rel="icon" href="/favicon-32.svg" sizes="32x32" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.svg" sizes="180x180" />
        {/* Fallback for older browsers */}
        <link rel="shortcut icon" href="/assets/logos/zusslogo.jpg" type="image/jpeg" />
        
        {/* Advanced Mobile & PWA Optimizations */}
        <meta name="theme-color" content="#0057FF" />
        <meta name="application-name" content="ZUS Coffee AI" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="ZUS AI" />
        <meta name="apple-touch-fullscreen" content="yes" />
        <meta name="HandheldFriendly" content="true" />
        <meta name="MobileOptimized" content="320" />
        <meta name="format-detection" content="telephone=no" />
        
        {/* Advanced Performance & Security */}
        <meta httpEquiv="X-DNS-Prefetch-Control" content="on" />
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-Frame-Options" content="DENY" />
        <meta httpEquiv="Referrer-Policy" content="strict-origin-when-cross-origin" />
        <meta name="robots" content="index,follow" />
        
        {/* Resource Hints for Better Performance */}
        <link rel="dns-prefetch" href="//fonts.googleapis.com" />
        <link rel="dns-prefetch" href="//fonts.gstatic.com" />
        
        {/* Advanced Viewport for Foldable & Modern Devices */}
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover, interactive-widget=resizes-content" />
        
        {/* Enhanced Font Loading */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
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
