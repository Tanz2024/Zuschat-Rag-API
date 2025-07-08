import type { AppProps } from 'next/app'
import Head from 'next/head'
import '../styles/globals.css'
import { ThemeProvider } from '../components/ThemeProvider'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="ZUS Coffee AI Assistant - Get instant answers about ZUS Coffee outlets, products, and services" />
        <title>ZUS Coffee AI Assistant</title>
      </Head>
      <ThemeProvider>
        <Component {...pageProps} />
      </ThemeProvider>
    </>
  )
}
