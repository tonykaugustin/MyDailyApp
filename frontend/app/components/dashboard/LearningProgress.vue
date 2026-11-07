<script setup>
const courses = [
  {
    name: "German Language",
    level: "A1 → B2",
    progress: 5,
    description: "Goethe-Zertifikat preparation",
    color: "purple",
  },
  {
    name: "Automotive Technician",
    level: "Professional training",
    progress: 10,
    description: "Diagnostics and ECU tuning",
    color: "blue",
  },
];
</script>

<template>
  <section class="card learning-card">
    <h3 class="card-title">Learning progress</h3>
    <p class="text-secondary learning-subtitle">
      Your long-term goals
    </p>

    <div
      v-for="course in courses"
      :key="course.name"
      class="course-item"
    >
      <div class="course-heading">
        <div>
          <strong>{{ course.name }}</strong>
          <p>{{ course.description }}</p>
        </div>

        <span>{{ course.progress }}%</span>
      </div>

      <div class="progress-track">
        <div
          class="progress-fill"
          :class="course.color"
          :style="{ width: course.progress + '%' }"
        ></div>
      </div>

      <span class="course-level">{{ course.level }}</span>
    </div>
  </section>
</template>

<style scoped>
.learning-subtitle {
  font-size: 12px;
  margin-top: 4px;
}

.course-item {
  margin-top: 24px;
}

.course-heading {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
}

.course-heading p {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.course-heading > span {
  color: var(--primary-hover);
  font-weight: 700;
}

.progress-fill.blue {
  background: var(--secondary);
}

.progress-fill.purple {
  background: var(--primary);
}

.course-level {
  display: block;
  color: var(--text-muted);
  font-size: 10px;
  margin-top: 8px;
}
</style>