<script setup>
const emit = defineEmits(["menu-click"]);

const currentDate = new Intl.DateTimeFormat("en-IN", {
  weekday: "long",
  day: "numeric",
  month: "long",
}).format(new Date());
</script>

<template>
  <header class="topbar">
    <div class="header-left">
      <button
        class="icon-button mobile-menu"
        aria-label="Open navigation"
        @click="emit('menu-click')"
      >
        ☰
      </button>

      <div class="header-date">
        <span>{{ currentDate }}</span>
      </div>
    </div>

    <div class="header-actions">
      <NuxtLink
        to="/notifications"
        class="icon-button notification-button"
        aria-label="Notifications"
      >
        ♧
      </NuxtLink>

      <div class="header-avatar">M</div>
    </div>
  </header>
</template>

<style scoped>
.header-left,
.header-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-date {
  color: var(--text-secondary);
  font-size: 13px;
}

.header-avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--primary);
  font-weight: 700;
}
</style>