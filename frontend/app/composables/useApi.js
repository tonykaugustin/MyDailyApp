export const useApi = () => {
  const config = useRuntimeConfig()

  const apiFetch = (endpoint, options = {}) => {
    return $fetch(`${config.public.apiBase}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
      },
    })
  }

  return {
    apiFetch,
  }
}