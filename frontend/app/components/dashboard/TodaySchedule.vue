<script setup>
const activities = [
  {
    time: "07:30 AM",
    title: "German vocabulary",
    description: "Learn 15–20 new words",
    category: "German",
    color: "purple",
  },
  {
    time: "08:15 AM",
    title: "German grammar",
    description: "Grammar and sentence formation",
    category: "German",
    color: "purple",
  },
  {
    time: "10:00 AM",
    title: "Automotive theory",
    description: "Engine fundamentals",
    category: "Automotive",
    color: "blue",
  },
  {
    time: "05:00 PM",
    title: "German listening",
    description: "Listening comprehension",
    category: "German",
    color: "purple",
  },
  {
    time: "08:00 PM",
    title: "ECU fundamentals",
    description: "Study automotive electronics",
    category: "Automotive",
    color: "blue",
  },
];
</script>

<template>
  <section class="card schedule-card">
    <div class="section-heading">
      <div>
        <h3 class="card-title">Today's schedule</h3>
        <p class="text-secondary">Your planned activities</p>
      </div>

      <NuxtLink to="/timetable" class="view-link">
        View all →
      </NuxtLink>
    </div>

    <div
      v-for="activity in activities"
      :key="activity.title"
      class="activity-item"
    >
      <span class="activity-time">{{ activity.time }}</span>

      <span
        class="activity-indicator"
        :class="activity.color"
      ></span>

      <div class="activity-details">
        <strong>{{ activity.title }}</strong>
        <p>{{ activity.description }}</p>
      </div>

      <span class="activity-category" :class="activity.color">
        {{ activity.category }}
      </span>
    </div>
  </section>
</template>

<style scoped>
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-heading p {
  font-size: 12px;
  margin-top: 4px;
}

.view-link {
  color: var(--primary-hover);
  font-size: 12px;
}

.activity-indicator.blue {
  background: var(--secondary);
}

.activity-indicator.purple {
  background: var(--primary);
}

.activity-details {
  flex: 1;
  min-width: 0;
}

.activity-details strong {
  font-size: 13px;
}

.activity-details p {
  color: var(--text-secondary);
  font-size: 11px;
  margin-top: 3px;
}

.activity-category {
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 6px;
  background: var(--bg-hover);
}

.activity-category.purple {
  color: var(--primary-hover);
}

.activity-category.blue {
  color: var(--secondary);
}

@media (max-width: 550px) {
  .activity-category {
    display: none;
  }

  .activity-time {
    min-width: 68px;
    font-size: 10px;
  }
}
</style>