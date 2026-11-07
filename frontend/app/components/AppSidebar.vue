<script setup>
defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close"]);

const navigation = [
  {
    label: "OVERVIEW",
    items: [
      { name: "Dashboard", icon: "⌂", path: "/" },
      { name: "My Timetable", icon: "▦", path: "/timetable" },
      { name: "Tasks", icon: "✓", path: "/tasks" },
    ],
  },
  {
    label: "LEARNING",
    items: [
      { name: "German Learning", icon: "🇩🇪", path: "/german" },
      { name: "Automotive", icon: "🚗", path: "/automotive" },
    ],
  },
  {
    label: "MANAGEMENT",
    items: [
      { name: "Analytics", icon: "▥", path: "/analytics" },
      { name: "Notifications", icon: "♧", path: "/notifications" },
      { name: "Settings", icon: "⚙", path: "/settings" },
    ],
  },
];
</script>

<template>
  <aside class="sidebar" :class="{ open: isOpen }">
    <div class="brand">
      <div class="brand-icon">M</div>
      <span class="brand-name">MyDaily</span>

      <button
        class="sidebar-close"
        aria-label="Close navigation"
        @click="emit('close')"
      >
        ✕
      </button>
    </div>

    <nav>
      <div
        v-for="section in navigation"
        :key="section.label"
        class="nav-section"
      >
        <p class="nav-label">{{ section.label }}</p>

        <NuxtLink
          v-for="item in section.items"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="active"
          @click="emit('close')"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span>{{ item.name }}</span>
        </NuxtLink>
      </div>
    </nav>

    <div class="sidebar-bottom">
      <div class="sidebar-profile">
        <div class="profile-avatar">M</div>
        <div>
          <strong>My Profile</strong>
          <p>Personal workspace</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.nav-icon {
  width: 23px;
  text-align: center;
  font-size: 17px;
}

.sidebar-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}

.profile-avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  background: var(--primary);
  border-radius: 50%;
  font-weight: 700;
}

.sidebar-profile strong {
  font-size: 13px;
}

.sidebar-profile p {
  color: var(--text-muted);
  font-size: 11px;
}

.sidebar-close {
  display: none;
  margin-left: auto;
  background: transparent;
  color: var(--text-secondary);
}

@media (max-width: 900px) {
  .sidebar-close {
    display: block;
  }
}
</style>