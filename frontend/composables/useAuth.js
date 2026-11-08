import { ref, computed } from 'vue'

const token = ref(null)
const refreshToken = ref(null)
const user = ref(null)
const isLoading = ref(false)
const isInitialized = ref(false)

export const useAuth = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://127.0.0.1:8000/api'

  const isAuthenticated = computed(() => !!token.value)

  const initAuth = async () => {
    if (isInitialized.value) return
    if (import.meta.client) {
      const storedToken = localStorage.getItem('mydaily_access_token')
      const storedRefresh = localStorage.getItem('mydaily_refresh_token')
      if (storedToken) {
        token.value = storedToken
        refreshToken.value = storedRefresh
        await fetchUser()
      }
      isInitialized.value = true
    }
  }

  const setTokens = (access, refresh) => {
    token.value = access
    refreshToken.value = refresh
    if (import.meta.client) {
      localStorage.setItem('mydaily_access_token', access)
      if (refresh) localStorage.setItem('mydaily_refresh_token', refresh)
    }
  }

  const login = async (username, password) => {
    isLoading.value = true
    try {
      const res = await fetch(`${apiBase}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || 'Invalid username or password')
      }
      const data = await res.json()
      setTokens(data.access, data.refresh)
      await fetchUser()
      return true
    } finally {
      isLoading.value = false
    }
  }

  const register = async (username, email, password, displayName) => {
    isLoading.value = true
    try {
      const res = await fetch(`${apiBase}/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          email,
          password,
          display_name: displayName
        })
      })
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        const firstErr = Object.values(errData)[0]
        throw new Error(Array.isArray(firstErr) ? firstErr[0] : 'Registration failed')
      }
      // Log in automatically after registration
      return await login(username, password)
    } finally {
      isLoading.value = false
    }
  }

  const fetchUser = async () => {
    if (!token.value) return null
    try {
      const res = await fetch(`${apiBase}/auth/me/`, {
        headers: { 'Authorization': `Bearer ${token.value}` }
      })
      if (res.ok) {
        user.value = await res.json()
        return user.value
      } else if (res.status === 401) {
        // Try refreshing token
        const refreshed = await refreshAccessToken()
        if (refreshed) {
          return await fetchUser()
        } else {
          logout()
        }
      }
    } catch (e) {
      console.error('Failed to fetch user', e)
    }
    return null
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) return false
    try {
      const res = await fetch(`${apiBase}/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken.value })
      })
      if (res.ok) {
        const data = await res.json()
        setTokens(data.access, data.refresh || refreshToken.value)
        return true
      }
    } catch (e) {
      console.error('Refresh token error', e)
    }
    return false
  }

  const logout = (redirect = true) => {
    token.value = null
    refreshToken.value = null
    user.value = null
    if (import.meta.client) {
      localStorage.removeItem('mydaily_access_token')
      localStorage.removeItem('mydaily_refresh_token')
    }
    if (redirect) {
      navigateTo('/login')
    }
  }

  const seedStarterData = async () => {
    if (!token.value) return
    try {
      const res = await fetch(`${apiBase}/auth/seed-data/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token.value}`
        }
      })
      return res.ok
    } catch (e) {
      console.error('Seed error', e)
      return false
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isLoading,
    isInitialized,
    initAuth,
    login,
    register,
    logout,
    fetchUser,
    refreshAccessToken,
    seedStarterData
  }
}

