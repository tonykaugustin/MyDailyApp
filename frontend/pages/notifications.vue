<template>
  <div class="notifications-page">
    <div class="page-top-bar">
      <div>
        <h2 class="view-title">Notifications & Reminders</h2>
        <p class="view-sub">Stay alerted for upcoming schedule events, daily habit reminders, and system updates.</p>
      </div>
      <div style="display: flex; gap: 0.75rem;">
        <button v-if="unreadCount > 0" class="btn btn-outline btn-sm" @click="markAllRead">
          Mark All Read
        </button>
        <button class="btn btn-primary btn-sm" @click="requestPushPermission">
          <AppIcon name="bell" :size="15" />
          {{ pushSubscribed ? 'Push Notifications Enabled' : 'Enable Web Push' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <span style="margin-left: 0.75rem; color: var(--text-secondary);">Loading notifications...</span>
    </div>

    <div v-else-if="notifications.length === 0" class="card empty-state">
      <div class="empty-icon"><AppIcon name="bell" :size="28" /></div>
      <div class="empty-title">All caught up!</div>
      <p class="empty-desc">You have no unread notifications or upcoming alerts.</p>
    </div>

    <div v-else class="notifications-list">
      <div
        v-for="n in notifications"
        :key="n.id"
        class="card notif-card"
        :class="{ unread: !n.is_read }"
      >
        <div class="notif-icon-box" :class="`type-${n.type}`">
          <AppIcon :name="getNotifIcon(n.type)" :size="18" />
        </div>

        <div class="notif-content">
          <div class="notif-title-row">
            <h4 class="notif-title">{{ n.title }}</h4>
            <span class="notif-time">{{ n.created_at ? n.created_at.split('T')[0] : '' }}</span>
          </div>
          <p class="notif-message">{{ n.message }}</p>
          <NuxtLink v-if="n.link" :to="n.link" class="notif-link">
            View Details →
          </NuxtLink>
        </div>

        <button
          v-if="!n.is_read"
          class="icon-btn"
          style="width: 32px; height: 32px;"
          title="Mark as read"
          @click="markRead(n)"
        >
          <AppIcon name="check" :size="14" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const api = useApi()

const notifications = ref([])
const isLoading = ref(true)
const pushSubscribed = ref(false)

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.is_read).length
})

const getNotifIcon = (type) => {
  const map = {
    reminder: 'bell',
    system: 'zap',
    goal: 'target',
    streak: 'repeat',
    alert: 'alert-circle'
  }
  return map[type] || 'bell'
}

const fetchNotifications = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/notifications/')
    notifications.value = res || []
  } catch (e) {
    console.error('Error fetching notifications', e)
  } finally {
    isLoading.value = false
  }
}

const markRead = async (n) => {
  try {
    await api.post(`/notifications/${n.id}/mark-read/`)
    n.is_read = true
  } catch (e) {
    alert('Error marking read: ' + e.message)
  }
}

const markAllRead = async () => {
  try {
    await api.post('/notifications/mark-all-read/')
    notifications.value.forEach(n => n.is_read = true)
  } catch (e) {
    alert('Error marking all read: ' + e.message)
  }
}

const requestPushPermission = async () => {
  if (!('Notification' in window)) {
    alert('Web Push is not supported in this browser.')
    return
  }
  const perm = await Notification.requestPermission()
  if (perm === 'granted') {
    pushSubscribed.value = true
    alert('Push notifications enabled for MyDaily!')
  }
}

onMounted(async () => {
  await fetchNotifications()
})
</script>

<style scoped>
.notifications-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.page-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.view-title {
  font-size: 1.4rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.view-sub {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.notif-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.25rem;
  transition: all var(--transition-fast);
}

.notif-card.unread {
  border-left: 4px solid var(--primary);
  background-color: var(--bg-card-hover);
}

.notif-icon-box {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notif-icon-box.type-reminder { background: var(--primary-light); color: var(--primary); }
.notif-icon-box.type-system { background: var(--secondary-light); color: var(--secondary); }
.notif-icon-box.type-goal { background: var(--success-light); color: var(--success); }
.notif-icon-box.type-streak { background: var(--warning-light); color: var(--warning); }
.notif-icon-box.type-alert { background: var(--error-light); color: var(--error); }

.notif-content {
  flex: 1;
}

.notif-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.2rem;
}

.notif-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
}

.notif-time {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.notif-message {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.notif-link {
  display: inline-block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
  margin-top: 0.4rem;
}
</style>

