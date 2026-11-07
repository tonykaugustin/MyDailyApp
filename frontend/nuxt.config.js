export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",

  devtools: {
    enabled: true,
  },

  css: [
    "~/assets/css/variables.css",
    "~/assets/css/reset.css",
    "~/assets/css/global.css",
    "~/assets/css/layout.css",
    "~/assets/css/components.css",
    "~/assets/css/dashboard.css",
  ],

  runtimeConfig: {
    public: {
      apiBase: 'http://127.0.0.1:8000/api/v1'
    }
  },

  devServer: {
    port: 3000,
  },
});