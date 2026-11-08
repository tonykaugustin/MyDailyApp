<template>
  <div class="habits-page">
    <div class="page-top-bar">
      <div>
        <h2 class="view-title">Habits & Daily Routines</h2>
        <p class="view-sub">Build lasting consistency with streak tracking, frequency rules, and daily rituals.</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <AppIcon name="plus" :size="16" />
        New Habit
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <span style="margin-left: 0.75rem; color: var(--text-secondary);">Loading habits...</span>
    </div>

    <div v-else-if="habits.length === 0" class="card empty-state">
      <div class="empty-icon"><AppIcon name="repeat" :size="28" /></div>
      <div class="empty-title">No habits created yet</div>
      <p class="empty-desc">Form your productivity rituals. Add habits for health, reading, hydration, or focus.</p>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">Add First Habit</button>
    </div>

    <div v-else class="habits-grid">
      <div
        v-for="habit in habits"
        :key="habit.id"
        class="card habit-card"
        :style="{ borderTopColor: habit.color || 'var(--success)' }"
      >
        <div class="habit-card-header">
          <div>
            <h3 class="habit-title">{{ habit.title }}</h3>
            <div class="habit-meta-tags">
              <span v-if="habit.category_details" class="badge" :style="{ backgroundColor: `${habit.category_details.color}22`, color: habit.category_details.color }">
                {{ habit.category_details.name }}
              </span>
              <span class="badge badge-neutral" style="text-transform: capitalize;">
                {{ habit.time_of_day }}
              </span>
              <span class="badge badge-neutral">
                {{ habit.frequency }}
              </span>
            </div>
          </div>

          <div style="display: flex; gap: 0.35rem;">
            <button class="icon-btn" style="width: 30px; height: 30px;" @click="openEditModal(habit)">
              <AppIcon name="edit" :size="13" />
            </button>
            <button class="icon-btn" style="width: 30px; height: 30px; color: var(--error);" @click="deleteHabit(habit)">
              <AppIcon name="trash" :size="13" />
            </button>
          </div>
        </div>

        <p v-if="habit.description" class="habit-desc">{{ habit.description }}</p>

        <!-- Streaks Display -->
        <div class="streaks-row">
          <div class="streak-box">
            <span class="streak-num">🔥 {{ habit.current_streak }}</span>
            <span class="streak-lbl">Current Streak</span>
          </div>
          <div class="streak-box">
            <span class="streak-num">🏆 {{ habit.best_streak }}</span>
            <span class="streak-lbl">Best Streak</span>
          </div>
        </div>

        <!-- 7-Day Interactive History Grid -->
        <div class="history-grid-box">
          <span class="history-title">Last 7 Days</span>
          <div class="days-pill-row">
            <div
              v-for="day in habit.weekly_history"
              :key="day.date"
              class="day-check-col"
              @click="toggleHabitDay(habit, day.date)"
            >
              <div
                class="day-circle"
                :class="{ active: day.completed }"
                :style="{ backgroundColor: day.completed ? (habit.color || 'var(--success)') : 'transparent' }"
              >
                <AppIcon v-if="day.completed" name="check" :size="12" />
              </div>
              <span class="day-lbl">{{ day.day_name }}</span>
            </div>
          </div>
        </div>

        <!-- Today 1-Click Action -->
        <button
          class="btn"
          :class="habit.is_completed_today ? 'btn-success' : 'btn-outline'"
          style="width: 100%; margin-top: auto;"
          @click="toggleHabitToday(habit)"
        >
          <AppIcon :name="habit.is_completed_today ? 'check' : 'plus'" :size="16" />
          {{ habit.is_completed_today ? 'Completed Today!' : 'Check In For Today' }}
        </button>
      </div>
    </div>

    <!-- CREATE / EDIT HABIT MODAL -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditing ? 'Edit Habit' : 'Create New Habit' }}</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="saveHabit" class="modal-body">
          <div class="form-group">
            <label class="form-label">Habit Title *</label>
            <input
              v-model="form.title"
              type="text"
              required
              class="form-input"
              placeholder="e.g. 2.5L Water Daily, Read 30 Mins, Morning Stretch"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Category</label>
              <select v-model="form.category" class="form-select">
                <option :value="null">No Category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Time of Day</label>
              <select v-model="form.time_of_day" class="form-select">
                <option value="morning">Morning</option>
                <option value="afternoon">Afternoon</option>
                <option value="evening">Evening</option>
                <option value="anytime">Anytime</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Frequency</label>
              <select v-model="form.frequency" class="form-select">
                <option value="daily">Every day</option>
                <option value="weekdays">Weekdays only</option>
                <option value="weekends">Weekends only</option>
                <option value="custom">Custom days</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Color Label</label>
              <input v-model="form.color" type="color" class="form-input" style="height: 38px; padding: 2px;" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Description / Motivation</label>
            <textarea
              v-model="form.description"
              class="form-textarea"
              placeholder="Why this habit matters, trigger cues..."
            ></textarea>
          </div>

          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Save Habit</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const api = useApi()

const habits = ref([])
const categories = ref([])
const isLoading = ref(true)

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const form = ref({
  title: '',
  description: '',
  category: null,
  frequency: 'daily',
  time_of_day: 'anytime',
  color: '#22C55E'
})

const fetchHabits = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/habits/')
    habits.value = res || []
  } catch (e) {
    console.error('Error fetching habits', e)
  } finally {
    isLoading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/categories/')
    categories.value = res || []
  } catch (e) {
    console.error(e)
  }
}

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = {
    title: '',
    description: '',
    category: categories.value[0]?.id || null,
    frequency: 'daily',
    time_of_day: 'anytime',
    color: '#22C55E'
  }
  showModal.value = true
}

const openEditModal = (h) => {
  isEditing.value = true
  editingId.value = h.id
  form.value = {
    title: h.title,
    description: h.description,
    category: h.category,
    frequency: h.frequency,
    time_of_day: h.time_of_day,
    color: h.color || '#22C55E'
  }
  showModal.value = true
}

const saveHabit = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/habits/${editingId.value}/`, form.value)
    } else {
      await api.post('/habits/', form.value)
    }
    showModal.value = false
    await fetchHabits()
  } catch (e) {
    alert('Error saving habit: ' + e.message)
  }
}

const deleteHabit = async (h) => {
  if (confirm(`Delete habit "${h.title}"?`)) {
    try {
      await api.delete(`/habits/${h.id}/`)
      await fetchHabits()
    } catch (e) {
      alert('Error deleting habit: ' + e.message)
    }
  }
}

const toggleHabitToday = async (habit) => {
  try {
    await api.post(`/habits/${habit.id}/toggle/`, {})
    await fetchHabits()
  } catch (e) {
    alert('Error toggling habit: ' + e.message)
  }
}

const toggleHabitDay = async (habit, dateStr) => {
  try {
    await api.post(`/habits/${habit.id}/toggle/`, { date: dateStr })
    await fetchHabits()
  } catch (e) {
    alert('Error toggling day: ' + e.message)
  }
}

onMounted(async () => {
  await fetchCategories()
  await fetchHabits()
})
</script>

<style scoped>
.habits-page {
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

.habits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
}

.habit-card {
  border-top: 4px solid var(--success);
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.habit-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.habit-title {
  font-size: 1.05rem;
  font-weight: 700;
}

.habit-meta-tags {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.35rem;
}

.habit-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.streaks-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.streak-box {
  background-color: var(--bg-elevated);
  padding: 0.6rem;
  border-radius: var(--radius-md);
  text-align: center;
  border: 1px solid var(--border-color);
}

.streak-num {
  display: block;
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
}

.streak-lbl {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.history-grid-box {
  background-color: var(--bg-elevated);
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.history-title {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.days-pill-row {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.day-check-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
}

.day-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1.5px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  transition: all var(--transition-fast);
}

.day-circle.active {
  border-color: transparent;
}

.day-lbl {
  font-size: 0.68rem;
  color: var(--text-muted);
}
</style>

