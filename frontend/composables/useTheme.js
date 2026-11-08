import { ref } from 'vue'

const currentTheme = ref('minimal')

export const useTheme = () => {
  const initTheme = () => {
    if (import.meta.client) {
      const stored = localStorage.getItem('mydaily_theme') || 'minimal'
      setTheme(stored)
    }
  }

  const setTheme = (theme) => {
    currentTheme.value = theme
    if (import.meta.client) {
      localStorage.setItem('mydaily_theme', theme)
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark')
      } else {
        document.documentElement.removeAttribute('data-theme')
      }
    }
  }

  const toggleTheme = () => {
    const next = currentTheme.value === 'dark' ? 'minimal' : 'dark'
    setTheme(next)
  }

  return {
    theme: currentTheme,
    initTheme,
    setTheme,
    toggleTheme
  }
}
