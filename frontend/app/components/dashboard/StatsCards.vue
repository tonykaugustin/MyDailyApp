<script setup>
const stats = [
  {
    title: "Tasks completed",
    value: "0 / 8",
    icon: "✓",
    description: "Today's activities",
    color: "green",
  },
  {
    title: "Study hours",
    value: "0h",
    icon: "◷",
    description: "Time invested today",
    color: "blue",
  },
  {
    title: "Daily progress",
    value: "0%",
    icon: "◉",
    description: "Completion rate",
    color: "purple",
  },
  {
    title: "Current streak",
    value: "0 days",
    icon: "🔥",
    description: "Keep going!",
    color: "orange",
  },
];
</script>

<template>
  <section class="stats-grid">
    <article
      v-for="stat in stats"
      :key="stat.title"
      class="card stat-card"
    >
      <div class="stat-top">
        <span>{{ stat.title }}</span>
        <span class="stat-icon" :class="stat.color">
          {{ stat.icon }}
        </span>
      </div>

      <h2 class="stat-value">{{ stat.value }}</h2>

      <p class="text-secondary">{{ stat.description }}</p>
    </article>
  </section>
</template>

<style scoped>
.stat-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--text-secondary);
  font-size: 12px;
}

.stat-icon {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 10px;
  background: var(--bg-hover);
  font-size: 17px;
}

.stat-icon.green { color: var(--success); }
.stat-icon.blue { color: var(--secondary); }
.stat-icon.purple { color: var(--primary-hover); }
.stat-icon.orange { color: var(--warning); }
</style>