<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="brand-icon-box" style="width: 44px; height: 44px; margin: 0 auto 0.85rem;">
          <AppIcon name="zap" :size="24" />
        </div>
        <h1 class="auth-title">MyDaily</h1>
        <p class="auth-subtitle">Universal Productivity & Life Management</p>
      </div>

      <!-- Mode Switcher Tabs -->
      <div class="auth-tabs">
        <button
          class="auth-tab-btn"
          :class="{ active: isLoginMode }"
          @click="isLoginMode = true; errorMsg = ''"
        >
          Sign In
        </button>
        <button
          class="auth-tab-btn"
          :class="{ active: !isLoginMode }"
          @click="isLoginMode = false; errorMsg = ''"
        >
          Create Account
        </button>
      </div>

      <!-- Error Alert -->
      <div v-if="errorMsg" class="auth-error">
        <AppIcon name="alert-circle" :size="18" />
        <span>{{ errorMsg }}</span>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="auth-form">
        <div v-if="!isLoginMode" class="form-group">
          <label class="form-label">Full Name / Display Name</label>
          <input
            v-model="form.displayName"
            type="text"
            class="form-input"
            placeholder="e.g. Alex Morgan"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Username</label>
          <input
            v-model="form.username"
            type="text"
            required
            class="form-input"
            placeholder="Enter your username"
          />
        </div>

        <div v-if="!isLoginMode" class="form-group">
          <label class="form-label">Email Address</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="form-input"
            placeholder="name@example.com"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="6"
            class="form-input"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          class="btn btn-primary"
          style="width: 100%; padding: 0.7rem; margin-top: 0.5rem;"
          :disabled="isLoading"
        >
          <div v-if="isLoading" class="spinner" style="width: 18px; height: 18px; border-width: 2px;"></div>
          <span v-else>{{ isLoginMode ? 'Sign In to Workspace' : 'Create My Account' }}</span>
        </button>

        <!-- Demo Account Fast Fill -->
        <div class="demo-quick-fill">
          <button
            type="button"
            class="btn btn-outline btn-sm"
            style="width: 100%; border-style: dashed;"
            @click="fillDemoAccount"
          >
            <AppIcon name="zap" :size="14" />
            Quick Demo Login (demo / password123)
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

definePageMeta({
  layout: false,
  middleware: [
    function (to) {
      if (import.meta.client) {
        const token = localStorage.getItem('mydaily_access_token')
        if (token && to.query.logout !== 'true') {
          return navigateTo('/')
        }
      }
    }
  ]
})

const route = useRoute()
const { isAuthenticated, initAuth, login, register, logout, isLoading } = useAuth()

const isLoginMode = ref(route.query.mode !== 'register')
const errorMsg = ref('')

const form = ref({
  username: '',
  displayName: '',
  email: '',
  password: ''
})

const fillDemoAccount = () => {
  isLoginMode.value = true
  form.value.username = 'demo'
  form.value.password = 'password123'
}

const handleSubmit = async () => {
  errorMsg.value = ''
  try {
    if (isLoginMode.value) {
      await login(form.value.username, form.value.password)
    } else {
      await register(
        form.value.username,
        form.value.email,
        form.value.password,
        form.value.displayName
      )
    }
    navigateTo('/')
  } catch (err) {
    errorMsg.value = err.message || 'An error occurred during authentication.'
  }
}

onMounted(async () => {
  if (route.query.logout === 'true') {
    logout(false)
    return
  }
  await initAuth()
  if (isAuthenticated.value) {
    navigateTo('/')
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background-color: var(--bg-main);
}

.auth-card {
  width: 100%;
  max-width: 430px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 2.25rem;
  box-shadow: var(--shadow-md);
}

.auth-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.auth-title {
  font-size: 1.7rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.auth-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.2rem;
}

.auth-tabs {
  display: flex;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 0.25rem;
  margin-bottom: 1.25rem;
}

.auth-tab-btn {
  flex: 1;
  padding: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.auth-tab-btn.active {
  background-color: var(--bg-card);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.auth-error {
  background-color: var(--error-light);
  border: 1px solid var(--error);
  color: var(--error);
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.82rem;
}

.demo-quick-fill {
  margin-top: 1.15rem;
  padding-top: 1.15rem;
  border-top: 1px solid var(--border-color);
}
</style>
