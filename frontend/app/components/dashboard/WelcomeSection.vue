<script setup>
const hour = new Date().getHours();

const greeting =
  hour < 12
    ? "Good morning"
    : hour < 17
      ? "Good afternoon"
      : "Good evening";

const today = new Intl.DateTimeFormat("en-IN", {
  weekday: "long",
  day: "numeric",
  month: "long",
  year: "numeric",
}).format(new Date());
</script>

<template>
  <section class="welcome-section">
    <div>
      <h1>{{ greeting }}! 👋</h1>
      <p>Let's make today productive.</p>
      <p class="welcome-date">{{ today }}</p>
    </div>

    <NuxtLink to="/timetable" class="primary-button">
      + View timetable
    </NuxtLink>
  </section>
</template>

<style scoped>
.welcome-date {
  font-size: 12px;
  margin-top: 8px;
  color: var(--text-muted);
}
</style>