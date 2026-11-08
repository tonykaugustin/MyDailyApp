<template>
  <div class="dashboard-page">
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner" style="width: 40px; height: 40px; border-width: 3px;"></div>
      <p style="margin-top: 1rem; color: var(--text-secondary);">Loading your productivity dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMsg" class="card" style="border-color: var(--error); margin-bottom: 2rem;">
      <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--error);">
        <AppIcon name="alert-circle" :size="24" />
        <div>
          <h3 style="font-size: 1.1rem; font-weight: 700;">Could not load dashboard data</h3>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.2rem;">{{ errorMsg }}</p>
        </div>
      </div>
      <button class="btn btn-primary btn-sm" style="margin-top: 1rem;" @click="fetchDashboard">
        Retry
      </button>
    </div>

    <div v-else>
      <!-- Dashboard Top Controls & Customizer -->
      <div class="dashboard-banner">
        <div>
          <h2 class="welcome-heading">Welcome back, {{ userDisplayName }} 👋</h2>
          <p class="welcome-sub">Here is your dynamic productivity overview for today.</p>
        </div>
        <div class="banner-actions">
          <button class="btn btn-outline btn-sm" @click="showWidgetSettings = !showWidgetSettings">
            <AppIcon name="settings" :size="15" />
            Customize Widgets
          </button>
          <NuxtLink to="/timetable" class="btn btn-primary btn-sm">
            <AppIcon name="calendar" :size="15" />
            Open Timetable
          </NuxtLink>
        </div>
      </div>

      <!-- Widget Customization Drawer / Panel -->
      <div v-if="showWidgetSettings" class="card widget-settings-card">
        <div class="card-header" style="margin-bottom: 0.75rem;">
          <span class="card-title" style="font-size: 0.95rem;">
            <AppIcon name="settings" :size="16" />
            Dashboard Widget Preferences
          </span>
          <button class="btn btn-ghost btn-sm" @click="showWidgetSettings = false">Done</button>
        </div>
        <div class="widget-toggle-grid">
          <label class="checkbox-label" v-for="(val, key) in widgetVisibility" :key="key">
            <input type="checkbox" v-model="widgetVisibility[key]" class="checkbox-input" />
            <span class="checkbox-custom">
              <AppIcon v-if="widgetVisibility[key]" name="check" :size="12" />
            </span>
            <span>{{ formatWidgetName(key) }}</span>
          </label>
        </div>
      </div>

      <!-- 1. STATISTICS CARDS (Calculated strictly from database) -->
      <div v-if="widgetVisibility.stats" class="stats-grid">
        <!-- 1. Total activities today -->
        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Total Activities</span>
            <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">
              <AppIcon name="calendar" :size="18" />
            </div>
          </div>
          <div class="stat-value">{{ data.stats.total_activities_today }}</div>
          <div class="stat-subtext">Scheduled for today</div>
        </div>

        <!-- 2. Completed activities -->
        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Completed</span>
            <div class="stat-icon" style="background: var(--success-light); color: var(--success);">
              <AppIcon name="check-square" :size="18" />
            </div>
          </div>
          <div class="stat-value" style="color: var(--success);">
            {{ data.stats.completed_activities_today }}
          </div>
          <div class="stat-subtext">Activities finished today</div>
        </div>

        <!-- 3. Pending activities -->
        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Pending Activities</span>
            <div class="stat-icon" style="background: var(--warning-light); color: var(--warning);">
              <AppIcon name="clock" :size="18" />
            </div>
          </div>
          <div class="stat-value" style="color: var(--warning);">
            {{ data.stats.pending_activities_today }}
          </div>
          <div class="stat-subtext">Remaining on timetable</div>
        </div>

        <!-- 4. Pending tasks -->
        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Pending Tasks</span>
            <div class="stat-icon" style="background: var(--secondary-light); color: var(--secondary);">
              <AppIcon name="check-square" :size="18" />
            </div>
          </div>
          <div class="stat-value">{{ data.stats.pending_tasks_today }}</div>
          <div class="stat-subtext">{{ data.stats.total_pending_tasks }} total in backlog</div>
        </div>

        <!-- 5. Completed tasks -->
        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Tasks Done</span>
            <div class="stat-icon" style="background: var(--success-light); color: var(--success);">
              <AppIcon name="check" :size="18" />
            </div>
          </div>
          <div class="stat-value">{{ data.stats.completed_tasks_today }}</div>
          <div class="stat-subtext">Completed today</div>
        </div>

        <!-- 6. Total study time -->
        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Study Time</span>
            <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">
              <AppIcon name="book-open" :size="18" />
            </div>
          </div>
          <div class="stat-value">{{ data.stats.total_study_hours_today }}<span style="font-size: 1.1rem; font-weight: 600; margin-left: 2px;">h</span></div>
          <div class="stat-subtext">{{ data.stats.total_study_minutes_today }} minutes logged today</div>
        </div>

        <!-- 7. Daily completion percentage -->
        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Day Progress</span>
            <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">
              <AppIcon name="activity" :size="18" />
            </div>
          </div>
          <div class="stat-value">{{ data.stats.daily_completion_percentage }}%</div>
          <div class="progress-track" style="margin-top: 0.5rem;">
            <div class="progress-fill" :style="{ width: `${data.stats.daily_completion_percentage}%` }"></div>
          </div>
        </div>

        <!-- 8. Active goals -->
        <div class="stat-card">
          <div class="stat-card-top">
            <span class="stat-label">Active Goals</span>
            <div class="stat-icon" style="background: var(--secondary-light); color: var(--secondary);">
              <AppIcon name="target" :size="18" />
            </div>
          </div>
          <div class="stat-value">{{ data.stats.active_goals_count }}</div>
          <div class="stat-subtext">Goals in active progress</div>
        </div>
      </div>

      <!-- Main Dashboard Grid Layout -->
      <div class="dashboard-grid">
        <!-- LEFT COLUMN: Today's Schedule & Today's Tasks -->
        <div class="grid-main-col">
          <!-- 2. TODAY'S SCHEDULE -->
          <div v-if="widgetVisibility.schedule" class="card section-card">
            <div class="card-header">
              <div>
                <h3 class="card-title">
                  <AppIcon name="calendar" :size="20" style="color: var(--primary);" />
                  Today's Schedule
                </h3>
                <p class="card-subtitle">Timetable occurrences and daily activities</p>
              </div>
              <NuxtLink to="/timetable" class="btn btn-ghost btn-sm">
                View Timetable →
              </NuxtLink>
            </div>

            <!-- Empty Schedule -->
            <div v-if="!data.today_schedule || data.today_schedule.length === 0" class="empty-state">
              <div class="empty-icon">
                <AppIcon name="calendar" :size="28" />
              </div>
              <div class="empty-title">No activities scheduled for today</div>
              <p class="empty-desc">Create activities in the timetable module to schedule your daily routine.</p>
              <NuxtLink to="/timetable" class="btn btn-primary btn-sm">
                <AppIcon name="plus" :size="14" />
                Add Activity
              </NuxtLink>
            </div>

            <!-- Schedule Items List -->
            <div v-else class="schedule-list">
              <div
                v-for="item in data.today_schedule"
                :key="item.instance_id"
                class="schedule-card"
                :class="{
                  completed: item.status === 'completed',
                  skipped: item.status === 'skipped'
                }"
                :style="{ borderLeftColor: item.color || 'var(--primary)' }"
              >
                <!-- Time Block -->
                <div class="schedule-time-block">
                  <span class="schedule-time">{{ item.start_time }}</span>
                  <span class="schedule-duration">until {{ item.end_time }}</span>
                </div>

                <!-- Info Block -->
                <div class="schedule-info">
                  <div class="schedule-title" :class="{ done: item.status === 'completed' }">
                    <span>{{ item.title }}</span>
                    <span v-if="item.is_recurring" class="badge badge-neutral" style="font-size: 0.65rem;">
                      <AppIcon name="repeat" :size="10" />
                      {{ item.recurrence }}
                    </span>
                  </div>
                  <div class="schedule-meta">
                    <span
                      v-if="item.category"
                      class="badge"
                      :style="{
                        backgroundColor: `${item.category.color}22`,
                        color: item.category.color
                      }"
                    >
                      {{ item.category.name }}
                    </span>
                    <span :class="`priority-${item.priority}`" style="font-weight: 600; text-transform: capitalize;">
                      {{ item.priority }} priority
                    </span>
                    <span v-if="item.reminder_minutes > 0" style="display: flex; align-items: center; gap: 2px;">
                      <AppIcon name="bell" :size="12" />
                      {{ item.reminder_minutes }}m before
                    </span>
                  </div>
                  <p v-if="item.description" style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.35rem;">
                    {{ item.description }}
                  </p>
                </div>

                <!-- Actions -->
                <div class="schedule-actions">
                  <!-- Mark Complete / Uncomplete -->
                  <button
                    v-if="item.status !== 'completed'"
                    class="btn btn-success btn-sm"
                    title="Mark complete"
                    @click="handleCompleteActivity(item)"
                  >
                    <AppIcon name="check" :size="14" />
                    Complete
                  </button>
                  <button
                    v-else
                    class="btn btn-ghost btn-sm"
                    title="Undo completion"
                    @click="handleUncompleteActivity(item)"
                  >
                    <AppIcon name="refresh-cw" :size="13" />
                    Undo
                  </button>

                  <!-- Skip -->
                  <button
                    v-if="item.status === 'pending'"
                    class="btn btn-outline btn-sm"
                    title="Skip for today"
                    @click="handleSkipActivity(item)"
                  >
                    <AppIcon name="skip-forward" :size="13" />
                    Skip
                  </button>

                  <!-- Details Modal Trigger -->
                  <button
                    class="icon-btn"
                    style="width: 32px; height: 32px;"
                    title="View details"
                    @click="activeDetailItem = item"
                  >
                    <AppIcon name="file-text" :size="15" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. TODAY'S TASKS -->
          <div v-if="widgetVisibility.tasks" class="card section-card">
            <div class="card-header">
              <div>
                <h3 class="card-title">
                  <AppIcon name="check-square" :size="20" style="color: var(--secondary);" />
                  Today's Tasks
                </h3>
                <p class="card-subtitle">Due today and urgent action items</p>
              </div>
              <NuxtLink to="/tasks" class="btn btn-ghost btn-sm">
                All Tasks →
              </NuxtLink>
            </div>

            <div v-if="!data.today_tasks || data.today_tasks.length === 0" class="empty-state" style="padding: 1.75rem 1rem;">
              <div class="empty-title" style="font-size: 0.95rem;">No tasks due today</div>
              <p class="empty-desc" style="font-size: 0.8rem;">Add tasks with due dates or explore the backlog.</p>
              <NuxtLink to="/tasks" class="btn btn-outline btn-sm">Go to Tasks</NuxtLink>
            </div>

            <div v-else class="tasks-mini-list">
              <div
                v-for="task in data.today_tasks"
                :key="task.id"
                class="task-row"
                :class="{ completed: task.status === 'completed' }"
              >
                <button class="task-checkbox" @click="handleToggleTask(task)">
                  <AppIcon v-if="task.status === 'completed'" name="check" :size="14" />
                </button>
                <div class="task-text-block">
                  <span class="task-title" :class="{ done: task.status === 'completed' }">
                    {{ task.title }}
                  </span>
                  <div class="task-tags-row">
                    <span v-if="task.category_details" class="task-cat-badge">
                      {{ task.category_details.name }}
                    </span>
                    <span :class="`priority-${task.priority}`" style="font-size: 0.72rem; font-weight: 600;">
                      {{ task.priority }}
                    </span>
                    <span v-if="task.subtasks_count > 0" style="font-size: 0.72rem; color: var(--text-muted);">
                      {{ task.completed_subtasks_count }}/{{ task.subtasks_count }} subtasks
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 4. WEEKLY PRODUCTIVITY SUMMARY -->
          <div v-if="widgetVisibility.weekly" class="card section-card">
            <div class="card-header">
              <div>
                <h3 class="card-title">
                  <AppIcon name="bar-chart-2" :size="20" style="color: var(--primary);" />
                  Weekly Productivity Summary
                </h3>
                <p class="card-subtitle">Performance breakdown over the past 7 days</p>
              </div>
            </div>

            <div class="weekly-bars-container">
              <div
                v-for="day in data.weekly_summary"
                :key="day.date"
                class="weekly-day-col"
              >
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    :style="{
                      height: day.activities_total > 0
                        ? `${Math.min(100, Math.round((day.activities_completed / day.activities_total) * 100))}%`
                        : '8%'
                    }"
                    :title="`${day.day_name}: ${day.activities_completed}/${day.activities_total} activities completed`"
                  ></div>
                </div>
                <div class="day-label">{{ day.day_name }}</div>
                <div class="day-stats-pill">
                  {{ day.activities_completed }} done
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN: Habits, Active Goals, Learning Progress & Reminders -->
        <div class="grid-side-col">
          <!-- 5. HABITS TODAY -->
          <div v-if="widgetVisibility.habits" class="card section-card">
            <div class="card-header">
              <div>
                <h3 class="card-title">
                  <AppIcon name="repeat" :size="19" style="color: var(--success);" />
                  Habit Streaks
                </h3>
                <p class="card-subtitle">Daily rituals & consistency</p>
              </div>
              <NuxtLink to="/habits" class="btn btn-ghost btn-sm">All →</NuxtLink>
            </div>

            <div v-if="!data.habits || data.habits.length === 0" class="empty-state" style="padding: 1.5rem 1rem;">
              <p class="empty-desc" style="font-size: 0.8rem;">No habits set up yet.</p>
              <NuxtLink to="/habits" class="btn btn-outline btn-sm">Add Habit</NuxtLink>
            </div>

            <div v-else class="habits-mini-list">
              <div
                v-for="habit in data.habits"
                :key="habit.id"
                class="habit-mini-item"
              >
                <div class="habit-info">
                  <div class="habit-name">{{ habit.title }}</div>
                  <div class="habit-streak-badge">
                    🔥 {{ habit.current_streak }} day streak
                  </div>
                </div>
                <button
                  class="btn btn-sm"
                  :class="habit.is_completed_today ? 'btn-success' : 'btn-outline'"
                  @click="handleToggleHabit(habit)"
                >
                  <AppIcon :name="habit.is_completed_today ? 'check' : 'plus'" :size="14" />
                  {{ habit.is_completed_today ? 'Done' : 'Check' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 6. ACTIVE GOALS -->
          <div v-if="widgetVisibility.goals" class="card section-card">
            <div class="card-header">
              <div>
                <h3 class="card-title">
                  <AppIcon name="target" :size="19" style="color: var(--secondary);" />
                  Active Goals
                </h3>
                <p class="card-subtitle">Targets in progress</p>
              </div>
              <NuxtLink to="/goals" class="btn btn-ghost btn-sm">All →</NuxtLink>
            </div>

            <div v-if="!data.active_goals || data.active_goals.length === 0" class="empty-state" style="padding: 1.5rem 1rem;">
              <p class="empty-desc" style="font-size: 0.8rem;">No active goals found.</p>
              <NuxtLink to="/goals" class="btn btn-outline btn-sm">Create Goal</NuxtLink>
            </div>

            <div v-else class="goals-mini-list">
              <div v-for="goal in data.active_goals" :key="goal.id" class="goal-mini-item">
                <div class="goal-top">
                  <span class="goal-title">{{ goal.title }}</span>
                  <span class="goal-percent">{{ goal.progress_percentage }}%</span>
                </div>
                <div class="progress-track" style="margin-top: 0.4rem; height: 6px;">
                  <div class="progress-fill" :style="{ width: `${goal.progress_percentage}%` }"></div>
                </div>
                <div class="goal-meta">
                  <span>{{ goal.current_value }} / {{ goal.target_value }} {{ goal.unit }}</span>
                  <span v-if="goal.target_date">Due {{ goal.target_date }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 7. LEARNING PROGRESS -->
          <div v-if="widgetVisibility.learning" class="card section-card">
            <div class="card-header">
              <div>
                <h3 class="card-title">
                  <AppIcon name="book-open" :size="19" style="color: var(--primary);" />
                  Learning Topics
                </h3>
                <p class="card-subtitle">Dynamic skill acquisition</p>
              </div>
              <NuxtLink to="/learning" class="btn btn-ghost btn-sm">Track →</NuxtLink>
            </div>

            <div v-if="!data.learning_progress || data.learning_progress.length === 0" class="empty-state" style="padding: 1.5rem 1rem;">
              <p class="empty-desc" style="font-size: 0.8rem;">No learning topics active.</p>
              <NuxtLink to="/learning" class="btn btn-outline btn-sm">Add Learning Goal</NuxtLink>
            </div>

            <div v-else class="learning-mini-list">
              <div v-for="topic in data.learning_progress" :key="topic.id" class="learning-mini-item">
                <div class="topic-header">
                  <span class="topic-title">{{ topic.title }}</span>
                  <span class="topic-hours">{{ topic.logged_hours }} / {{ topic.target_hours }}h</span>
                </div>
                <div class="progress-track" style="margin-top: 0.4rem; height: 6px;">
                  <div
                    class="progress-fill"
                    :style="{
                      width: `${topic.progress_percentage}%`,
                      backgroundColor: topic.color || 'var(--primary)'
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 8. UPCOMING REMINDERS -->
          <div v-if="widgetVisibility.reminders" class="card section-card">
            <div class="card-header">
              <div>
                <h3 class="card-title">
                  <AppIcon name="bell" :size="18" style="color: var(--warning);" />
                  Upcoming Reminders
                </h3>
              </div>
            </div>

            <div v-if="!data.upcoming_reminders || data.upcoming_reminders.length === 0" style="padding: 1rem 0; font-size: 0.82rem; color: var(--text-muted); text-align: center;">
              No reminders scheduled for today
            </div>

            <div v-else class="reminders-list">
              <div v-for="r in data.upcoming_reminders" :key="r.id" class="reminder-item">
                <div class="reminder-time-dot" :style="{ backgroundColor: r.color || 'var(--warning)' }"></div>
                <div style="flex: 1;">
                  <div style="font-weight: 600; font-size: 0.86rem;">{{ r.title }}</div>
                  <div style="font-size: 0.75rem; color: var(--text-muted);">
                    At {{ r.time }} ({{ r.reminder_minutes }}m notification)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ACTIVITY DETAILS MODAL -->
    <div v-if="activeDetailItem" class="modal-backdrop" @click.self="activeDetailItem = null">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ activeDetailItem.title }}</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="activeDetailItem = null">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <div class="modal-body">
          <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div>
              <span class="form-label">Time & Date</span>
              <p style="font-family: var(--font-mono); font-size: 1rem; color: var(--text-primary); margin-top: 0.2rem;">
                {{ activeDetailItem.occurrence_date }} • {{ activeDetailItem.start_time }} - {{ activeDetailItem.end_time }}
              </p>
            </div>

            <div v-if="activeDetailItem.category">
              <span class="form-label">Category</span>
              <div style="margin-top: 0.25rem;">
                <span
                  class="badge"
                  :style="{
                    backgroundColor: `${activeDetailItem.category.color}22`,
                    color: activeDetailItem.category.color
                  }"
                >
                  {{ activeDetailItem.category.name }}
                </span>
              </div>
            </div>

            <div>
              <span class="form-label">Priority & Recurrence</span>
              <div style="display: flex; gap: 0.5rem; margin-top: 0.25rem;">
                <span class="badge badge-neutral" style="text-transform: capitalize;">
                  Priority: {{ activeDetailItem.priority }}
                </span>
                <span class="badge badge-neutral">
                  Recurrence: {{ activeDetailItem.recurrence }}
                </span>
              </div>
            </div>

            <div>
              <span class="form-label">Description</span>
              <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.2rem; background: var(--bg-input); padding: 0.85rem; border-radius: var(--radius-md);">
                {{ activeDetailItem.description || 'No description provided.' }}
              </p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <NuxtLink to="/timetable" class="btn btn-outline btn-sm">Edit in Timetable</NuxtLink>
          <button class="btn btn-primary btn-sm" @click="activeDetailItem = null">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const { user, isAuthenticated } = useAuth()
const api = useApi()

const isLoading = ref(true)
const errorMsg = ref('')
const data = ref({
  stats: {
    total_activities_today: 0,
    completed_activities_today: 0,
    pending_activities_today: 0,
    pending_tasks_today: 0,
    total_pending_tasks: 0,
    completed_tasks_today: 0,
    total_study_minutes_today: 0,
    total_study_hours_today: 0,
    daily_completion_percentage: 0,
    active_goals_count: 0
  },
  today_schedule: [],
  today_tasks: [],
  active_goals: [],
  learning_progress: [],
  habits: [],
  upcoming_reminders: [],
  weekly_summary: []
})

const showWidgetSettings = ref(false)
const activeDetailItem = ref(null)

const widgetVisibility = reactive({
  stats: true,
  schedule: true,
  tasks: true,
  weekly: true,
  habits: true,
  goals: true,
  learning: true,
  reminders: true
})

const formatWidgetName = (key) => {
  const map = {
    stats: 'Statistics Cards',
    schedule: "Today's Schedule",
    tasks: "Today's Tasks",
    weekly: 'Weekly Summary Chart',
    habits: 'Habit Streaks',
    goals: 'Active Goals',
    learning: 'Learning Progress',
    reminders: 'Upcoming Reminders'
  }
  return map[key] || key
}

const userDisplayName = computed(() => {
  return user.value?.profile?.display_name || user.value?.first_name || user.value?.username || 'Productivity Champ'
})

const fetchDashboard = async () => {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const res = await api.get('/analytics/dashboard/')
    if (res) {
      data.value = res
    }
  } catch (err) {
    console.error('Failed to load dashboard', err)
    errorMsg.value = err.message || 'Could not load dashboard data from backend.'
  } finally {
    isLoading.value = false
  }
}

// Complete activity action
const handleCompleteActivity = async (item) => {
  try {
    await api.post(`/timetable/activities/${item.activity_id}/complete/`, {
      date: item.occurrence_date
    })
    item.status = 'completed'
    // Recalculate stats locally or refresh
    data.value.stats.completed_activities_today += 1
    data.value.stats.pending_activities_today = Math.max(0, data.value.stats.pending_activities_today - 1)
  } catch (e) {
    alert('Error marking activity complete: ' + e.message)
  }
}

// Uncomplete activity action
const handleUncompleteActivity = async (item) => {
  try {
    await api.post(`/timetable/activities/${item.activity_id}/uncomplete/`, {
      date: item.occurrence_date
    })
    item.status = 'pending'
    data.value.stats.completed_activities_today = Math.max(0, data.value.stats.completed_activities_today - 1)
    data.value.stats.pending_activities_today += 1
  } catch (e) {
    alert('Error unmarking activity: ' + e.message)
  }
}

// Skip activity action
const handleSkipActivity = async (item) => {
  try {
    await api.post(`/timetable/activities/${item.activity_id}/skip/`, {
      date: item.occurrence_date
    })
    item.status = 'skipped'
    data.value.stats.pending_activities_today = Math.max(0, data.value.stats.pending_activities_today - 1)
  } catch (e) {
    alert('Error skipping activity: ' + e.message)
  }
}

// Toggle Task
const handleToggleTask = async (task) => {
  try {
    const res = await api.post(`/tasks/${task.id}/toggle-complete/`)
    task.status = res.status
    if (task.status === 'completed') {
      data.value.stats.completed_tasks_today += 1
      data.value.stats.pending_tasks_today = Math.max(0, data.value.stats.pending_tasks_today - 1)
    } else {
      data.value.stats.completed_tasks_today = Math.max(0, data.value.stats.completed_tasks_today - 1)
      data.value.stats.pending_tasks_today += 1
    }
  } catch (e) {
    alert('Error updating task: ' + e.message)
  }
}

// Toggle Habit
const handleToggleHabit = async (habit) => {
  try {
    const res = await api.post(`/habits/${habit.id}/toggle/`, {})
    habit.is_completed_today = res.completed
    habit.current_streak = res.current_streak
  } catch (e) {
    alert('Error updating habit: ' + e.message)
  }
}

onMounted(() => {
  if (import.meta.client) {
    const token = localStorage.getItem('mydaily_access_token')
    if (!token) {
      navigateTo('/login')
      return
    }
    fetchDashboard()
  }
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 1rem;
}

.dashboard-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.welcome-heading {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.welcome-sub {
  font-size: 0.88rem;
  color: var(--text-secondary);
  margin-top: 0.2rem;
}

.banner-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.widget-settings-card {
  margin-bottom: 1.5rem;
  animation: fadeIn 0.2s ease;
}

.widget-toggle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

/* Grid Layout */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 1.5rem;
}

.grid-main-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.grid-side-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-card {
  display: flex;
  flex-direction: column;
}

/* Tasks Mini List */
.tasks-mini-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.task-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-md);
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}

.task-row:hover {
  background-color: var(--bg-card-hover);
}

.task-row.completed {
  opacity: 0.55;
}

.task-checkbox {
  width: 20px;
  height: 20px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border-light);
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  cursor: pointer;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.task-row.completed .task-checkbox {
  background-color: var(--success);
  border-color: var(--success);
}

.task-text-block {
  flex: 1;
  overflow: hidden;
}

.task-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
  display: block;
}

.task-title.done {
  text-decoration: line-through;
}

.task-tags-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 0.2rem;
}

.task-cat-badge {
  font-size: 0.7rem;
  color: var(--primary);
}

/* Weekly Chart */
.weekly-bars-container {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem;
  height: 140px;
  padding-top: 1rem;
}

.weekly-day-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar-track {
  flex: 1;
  width: 28px;
  background-color: var(--bg-elevated);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.bar-fill {
  width: 100%;
  background: var(--primary-gradient);
  border-radius: var(--radius-sm);
  transition: height 0.4s ease;
}

.day-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.day-stats-pill {
  font-size: 0.68rem;
  color: var(--text-muted);
}

/* Habits Mini */
.habits-mini-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.habit-mini-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.habit-name {
  font-size: 0.88rem;
  font-weight: 600;
}

.habit-streak-badge {
  font-size: 0.74rem;
  color: var(--warning);
  font-weight: 600;
  margin-top: 0.15rem;
}

/* Goals Mini */
.goals-mini-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.goal-mini-item {
  padding: 0.75rem;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.goal-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.goal-title {
  font-size: 0.86rem;
  font-weight: 600;
}

.goal-percent {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--secondary);
}

.goal-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 0.4rem;
}

/* Learning Mini */
.learning-mini-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.learning-mini-item {
  padding: 0.75rem;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.topic-title {
  font-size: 0.86rem;
  font-weight: 600;
}

.topic-hours {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

/* Reminders List */
.reminders-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.reminder-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  background-color: var(--bg-elevated);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.reminder-time-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>

