<template>
  <div class="app-shell" :data-theme="theme">
    <!-- Mobile Backdrop Overlay -->
    <div
      class="mobile-overlay"
      :class="{ active: isMobileOpen }"
      @click="isMobileOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      class="app-sidebar"
      :class="{
        collapsed: isCollapsed,
        'mobile-open': isMobileOpen
      }"
    >
      <!-- Sidebar Header -->
      <div class="sidebar-header">
        <NuxtLink to="/" class="brand-link" @click="isMobileOpen = false">
          <div class="brand-icon-box">
            <AppIcon name="zap" :size="20" />
          </div>
          <span v-if="!isCollapsed" class="brand-name">
            MyDaily
            <span class="brand-badge">PRO</span>
          </span>
        </NuxtLink>

        <!-- Desktop Collapse Button -->
        <button
          v-if="!isMobile"
          class="icon-btn"
          style="width: 32px; height: 32px;"
          :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
          @click="isCollapsed = !isCollapsed"
        >
          <AppIcon :name="isCollapsed ? 'chevron-right' : 'chevron-left'" :size="16" />
        </button>

        <!-- Mobile Close Button -->
        <button
          v-else
          class="icon-btn"
          style="width: 32px; height: 32px;"
          @click="isMobileOpen = false"
        >
          <AppIcon name="x" :size="16" />
        </button>
      </div>

      <!-- Navigation Modules List (11 strictly application-level modules) -->
      <nav class="sidebar-nav">
        <div v-if="!isCollapsed" class="nav-section-title">Productivity Modules</div>

        <NuxtLink
          v-for="item in navModules"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: currentPath === item.path }"
          :title="isCollapsed ? item.label : ''"
          @click="isMobileOpen = false"
        >
          <div class="nav-icon">
            <AppIcon :name="item.icon" :size="19" />
          </div>
          <span v-if="!isCollapsed">{{ item.label }}</span>
          <span
            v-if="!isCollapsed && item.path === '/notifications' && unreadNotifs > 0"
            class="nav-badge"
          >
            {{ unreadNotifs }}
          </span>
        </NuxtLink>
      </nav>

      <!-- Sidebar Footer / User Profile -->
      <div class="sidebar-footer">
        <NuxtLink to="/settings" class="user-snippet" :title="user?.username || 'User Profile'">
          <div class="user-avatar">
            {{ userInitials }}
          </div>
          <div v-if="!isCollapsed" class="user-meta">
            <div class="user-name">{{ userDisplayName }}</div>
            <div class="user-role">Personal Workspace</div>
          </div>
        </NuxtLink>

        <button
          class="btn btn-ghost"
          style="width: 100%; justify-content: flex-start; padding: 0.5rem 0.75rem;"
          :title="isCollapsed ? 'Log out' : ''"
          @click="handleLogout"
        >
          <AppIcon name="log-out" :size="18" />
          <span v-if="!isCollapsed" style="margin-left: 0.6rem;">Log Out</span>
        </button>
      </div>
    </aside>

    <!-- Main App Container -->
    <div
      class="app-main"
      :class="{ 'sidebar-collapsed': isCollapsed }"
    >
      <!-- Header -->
      <header class="app-header">
        <div class="header-left">
          <!-- Mobile Drawer Toggle -->
          <button
            class="icon-btn mobile-nav-toggle"
            @click="isMobileOpen = true"
          >
            <AppIcon name="menu" :size="20" />
          </button>

          <div class="header-date-title">
            <h1 class="page-title">{{ currentPageTitle }}</h1>
            <span class="current-date-text">{{ formattedCurrentDate }}</span>
          </div>
        </div>

        <div class="header-right">
          <!-- Theme Toggle -->
          <button
            class="icon-btn"
            :title="theme === 'dark' ? 'Switch to Minimal Theme' : 'Switch to Dark Theme'"
            @click="toggleTheme"
          >
            <AppIcon :name="theme === 'dark' ? 'sun' : 'moon'" :size="18" />
          </button>

          <!-- Notification Indicator -->
          <NuxtLink to="/notifications" class="icon-btn" title="Notifications">
            <AppIcon name="bell" :size="18" />
            <span v-if="unreadNotifs > 0" class="notif-dot"></span>
          </NuxtLink>

          <!-- Quick Seed Starter Data (Helpful for demo/onboarding) -->
          <button
            class="btn btn-outline btn-sm"
            style="display: flex; gap: 0.4rem; align-items: center;"
            title="Populate dynamic starter data"
            @click="handleSeedData"
          >
            <AppIcon name="refresh-cw" :size="14" />
            <span class="seed-btn-text">Reset Sample Data</span>
          </button>

          <!-- User Profile & Dropdown -->
          <div class="user-dropdown-container" style="position: relative;">
            <button
              class="icon-btn"
              style="overflow: hidden; padding: 0;"
              @click="isUserMenuOpen = !isUserMenuOpen"
            >
              <div class="user-avatar" style="width: 100%; height: 100%; font-size: 0.85rem;">
                {{ userInitials }}
              </div>
            </button>

            <!-- User Menu Dropdown -->
            <div
              v-if="isUserMenuOpen"
              class="card"
              style="position: absolute; right: 0; top: 48px; width: 220px; z-index: 60; padding: 0.5rem; box-shadow: var(--shadow-lg);"
            >
              <div style="padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--border-color); margin-bottom: 0.35rem;">
                <div style="font-weight: 700; font-size: 0.95rem;">{{ userDisplayName }}</div>
                <div style="font-size: 0.78rem; color: var(--text-muted);">{{ user?.email || user?.username }}</div>
              </div>
              <NuxtLink
                to="/settings"
                class="btn btn-ghost"
                style="width: 100%; justify-content: flex-start; padding: 0.5rem 0.8rem; font-size: 0.85rem;"
                @click="isUserMenuOpen = false"
              >
                <AppIcon name="settings" :size="16" />
                <span style="margin-left: 0.5rem;">Settings</span>
              </NuxtLink>
              <button
                class="btn btn-ghost"
                style="width: 100%; justify-content: flex-start; padding: 0.5rem 0.8rem; font-size: 0.85rem; color: var(--error);"
                @click="handleLogout"
              >
                <AppIcon name="log-out" :size="16" />
                <span style="margin-left: 0.5rem;">Log Out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Page Slot -->
      <main class="page-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const route = useRoute()
const { user, initAuth, logout, seedStarterData, isAuthenticated } = useAuth()
const { theme, initTheme, toggleTheme } = useTheme()
const api = useApi()

const isCollapsed = ref(false)
const isMobileOpen = ref(false)
const isMobile = ref(false)
const isUserMenuOpen = ref(false)
const unreadNotifs = ref(0)

// The 11 core application modules strictly defined by the specification
const navModules = [
  { path: '/', label: 'Dashboard', icon: 'layout-dashboard' },
  { path: '/timetable', label: 'Timetable', icon: 'calendar' },
  { path: '/tasks', label: 'Tasks', icon: 'check-square' },
  { path: '/learning', label: 'Learning', icon: 'book-open' },
  { path: '/study-sessions', label: 'Study Sessions', icon: 'clock' },
  { path: '/habits', label: 'Habits & Routines', icon: 'repeat' },
  { path: '/goals', label: 'Goals', icon: 'target' },
  { path: '/notes', label: 'Notes', icon: 'file-text' },
  { path: '/notifications', label: 'Notifications', icon: 'bell' },
  { path: '/analytics', label: 'Analytics', icon: 'bar-chart-2' },
  { path: '/settings', label: 'Settings', icon: 'settings' }
]

const currentPath = computed(() => route.path)

const currentPageTitle = computed(() => {
  const match = navModules.find(m => m.path === route.path)
  return match ? match.label : 'MyDaily'
})

const formattedCurrentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
})

const userDisplayName = computed(() => {
  if (!user.value) return 'Guest'
  return user.value.profile?.display_name || user.value.first_name || user.value.username
})

const userInitials = computed(() => {
  const name = userDisplayName.value
  return name.slice(0, 2).toUpperCase()
})

const checkScreenSize = () => {
  if (import.meta.client) {
    isMobile.value = window.innerWidth <= 768
  }
}

const fetchUnreadCount = async () => {
  try {
    const data = await api.get('/notifications/unread-count/')
    if (data && typeof data.unread_count === 'number') {
      unreadNotifs.value = data.unread_count
    }
  } catch (e) {
    // Silent fail for notifs
  }
}

const handleLogout = () => {
  isUserMenuOpen.value = false
  logout()
}

const handleSeedData = async () => {
  if (confirm('Do you want to reset and populate starter productivity categories, activities, tasks, habits, and goals?')) {
    await seedStarterData()
    window.location.reload()
  }
}

onMounted(async () => {
  initTheme()
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  await initAuth()
  if (user.value) {
    fetchUnreadCount()
  }
})
</script>

<style scoped>
@media (max-width: 640px) {
  .seed-btn-text {
    display: none;
  }
}
</style>

