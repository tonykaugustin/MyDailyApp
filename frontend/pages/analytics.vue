<template>
  <div class="analytics-page">
    <div class="page-top-bar">
      <div>
        <h2 class="view-title">Productivity Analytics</h2>
        <p class="view-sub">Visual insights into your daily execution, time investments, and category distribution.</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <span style="margin-left: 0.75rem; color: var(--text-secondary);">Loading analytics...</span>
    </div>

    <div v-else>
      <!-- Overall Metrics -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Tasks Completed</span>
            <div class="stat-icon" style="background: var(--success-light); color: var(--success);">
              <AppIcon name="check-square" :size="18" />
            </div>
          </div>
          <div class="stat-value">{{ data.total_tasks_completed }}</div>
          <div class="stat-subtext">All-time finished tasks</div>
        </div>

        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Achieved Goals</span>
            <div class="stat-icon" style="background: var(--secondary-light); color: var(--secondary);">
              <AppIcon name="award" :size="18" />
            </div>
          </div>
          <div class="stat-value">{{ data.achieved_goals }} / {{ data.total_goals }}</div>
          <div class="stat-subtext">Targets achieved</div>
        </div>

        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Active Habits</span>
            <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">
              <AppIcon name="repeat" :size="18" />
            </div>
          </div>
          <div class="stat-value">{{ data.active_habits_count }}</div>
          <div class="stat-subtext">Daily routines tracked</div>
        </div>
      </div>

      <!-- Category Time & Task Distribution -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div class="card-header">
          <div>
            <h3 class="card-title">
              <AppIcon name="folder" :size="20" style="color: var(--primary);" />
              Category Balance & Distribution
            </h3>
            <p class="card-subtitle">How your activities, tasks, and study hours are distributed across your life categories</p>
          </div>
        </div>

        <div v-if="!data.category_distribution || data.category_distribution.length === 0" class="empty-state">
          <p class="empty-desc">No category distribution data available yet.</p>
        </div>

        <div v-else class="categories-dist-table">
          <div
            v-for="cat in data.category_distribution"
            :key="cat.id"
            class="dist-row"
          >
            <div class="dist-cat-name">
              <div class="dist-dot" :style="{ backgroundColor: cat.color || 'var(--primary)' }"></div>
              <span style="font-weight: 700;">{{ cat.name }}</span>
            </div>

            <div class="dist-metrics">
              <div class="dist-metric-col">
                <span class="dist-m-val">{{ cat.activities_count }}</span>
                <span class="dist-m-lbl">Activities</span>
              </div>
              <div class="dist-metric-col">
                <span class="dist-m-val">{{ cat.tasks_count }}</span>
                <span class="dist-m-lbl">Tasks</span>
              </div>
              <div class="dist-metric-col">
                <span class="dist-m-val">{{ Math.round((cat.study_minutes || 0) / 60 * 10) / 10 }}h</span>
                <span class="dist-m-lbl">Study Time</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 30-Day Trend Chart -->
      <div class="card">
        <div class="card-header">
          <div>
            <h3 class="card-title">
              <AppIcon name="bar-chart-2" :size="20" style="color: var(--secondary);" />
              Past 30-Day Focus Trends
            </h3>
            <p class="card-subtitle">Minutes of focused study logged each day</p>
          </div>
        </div>

        <div class="trend-chart-container">
          <div
            v-for="day in data.study_30_days"
            :key="day.date"
            class="trend-col"
          >
            <div class="trend-bar-track">
              <div
                class="trend-bar-fill"
                :style="{
                  height: maxMinutes > 0 ? `${Math.min(100, Math.round((day.minutes / maxMinutes) * 100))}%` : '4%'
                }"
                :title="`${day.date}: ${day.minutes} minutes`"
              ></div>
            </div>
            <span class="trend-date-lbl">{{ day.date.slice(8) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const api = useApi()

const isLoading = ref(true)
const data = ref({
  total_tasks_completed: 0,
  achieved_goals: 0,
  total_goals: 0,
  active_habits_count: 0,
  category_distribution: [],
  study_30_days: []
})

const maxMinutes = computed(() => {
  if (!data.value.study_30_days) return 120
  const max = Math.max(...data.value.study_30_days.map(d => d.minutes), 0)
  return Math.max(max, 60)
})

const fetchAnalytics = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/analytics/overview/')
    if (res) data.value = res
  } catch (e) {
    console.error('Error fetching analytics', e)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await fetchAnalytics()
})
</script>

<style scoped>
.analytics-page {
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

.categories-dist-table {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dist-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  background-color: var(--bg-input);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  flex-wrap: wrap;
  gap: 1rem;
}

.dist-cat-name {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.95rem;
}

.dist-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dist-metrics {
  display: flex;
  gap: 2rem;
}

.dist-metric-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.dist-m-val {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.dist-m-lbl {
  font-size: 0.7rem;
  color: var(--text-muted);
}

/* 30-Day Trend Chart */
.trend-chart-container {
  display: flex;
  align-items: flex-end;
  height: 180px;
  gap: 6px;
  padding-top: 1rem;
  overflow-x: auto;
}

.trend-col {
  flex: 1;
  min-width: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.trend-bar-track {
  flex: 1;
  width: 100%;
  background-color: var(--bg-input);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.trend-bar-fill {
  width: 100%;
  background: var(--primary-gradient);
  border-radius: var(--radius-sm);
  transition: height 0.4s ease;
}

.trend-date-lbl {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-top: 0.4rem;
}
</style>

