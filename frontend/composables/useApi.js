export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://127.0.0.1:8000/api'
  const { token, refreshAccessToken, logout } = useAuth()

  const request = async (endpoint, options = {}) => {
    const url = endpoint.startsWith('http') ? endpoint : `${apiBase}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`
    
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }

    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`
    }

    let res = await fetch(url, {
      ...options,
      headers
    })

    // If 401 Unauthorized, attempt refresh once
    if (res.status === 401 && token.value) {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        headers['Authorization'] = `Bearer ${token.value}`
        res = await fetch(url, {
          ...options,
          headers
        })
      } else {
        logout()
        throw new Error('Session expired. Please log in again.')
      }
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      const errorMsg = errData.detail || errData.error || (typeof errData === 'object' ? JSON.stringify(errData) : 'API request failed')
      throw new Error(errorMsg)
    }

    // 204 No Content
    if (res.status === 204) return null
    return await res.json()
  }

  return {
    get: (endpoint, options) => request(endpoint, { ...options, method: 'GET' }),
    post: (endpoint, body, options) => request(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) }),
    patch: (endpoint, body, options) => request(endpoint, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
    put: (endpoint, body, options) => request(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) }),
    delete: (endpoint, options) => request(endpoint, { ...options, method: 'DELETE' }),
    apiBase
  }
}

