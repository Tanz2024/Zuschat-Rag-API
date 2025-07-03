import { ReactNode } from 'react'
import { ThemeContext, useThemeProvider } from '../hooks/useTheme'

interface ThemeProviderProps {
  children: ReactNode
}

export const ThemeProvider = ({ children }: ThemeProviderProps) => {
  const themeValue = useThemeProvider()

  return (
    <ThemeContext.Provider value={themeValue}>
      {children}
    </ThemeContext.Provider>
  )
}
