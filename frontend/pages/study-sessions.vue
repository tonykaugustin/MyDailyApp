<template>
  <div class="study-page">
    <div class="page-top-bar">
      <div>
        <h2 class="view-title">Study & Focus Sessions</h2>
        <p class="view-sub">Track deep focus blocks with Pomodoro timers, stopwatches, and logged sessions.</p>
      </div>
      <button class="btn btn-outline btn-sm" @click="showManualModal = true">
        <AppIcon name="plus" :size="15" />
        Log Past Session
      </button>
    </div>

    <div class="study-layout-grid">
      <!-- TIMER WIDGET (LEFT/MAIN) -->
      <div class="card timer-card">
        <!-- Timer Modes -->
        <div class="tabs-nav" style="margin: 0 auto 1.5rem;">
          <button
            class="tab-btn"
            :class="{ active: timerMode === 'pomodoro' }"
            @click="switchTimerMode('pomodoro')"
          >
            Pomodoro (25m)
          </button>
          <button
            class="tab-btn"
            :class="{ active: timerMode === 'short_break' }"
            @click="switchTimerMode('short_break')"
          >
            Short Break (5m)
          </button>
          <button
            class="tab-btn"
            :class="{ active: timerMode === 'stopwatch' }"
            @click="switchTimerMode('stopwatch')"
          >
            Stopwatch
          </button>
        </div>

        <!-- Timer Big Display -->
        <div class="timer-display-box">
          <div class="timer-clock-digits">{{ formattedTime }}</div>
          <div class="timer-mode-caption">
            {{ isRunning ? 'Session in progress...' : 'Ready to focus' }}
          </div>
        </div>

        <!-- Session Association Config -->
        <div class="timer-association-row">
          <div style="flex: 1;">
            <label class="form-label" style="font-size: 0.78rem;">Target Learning Track (Optional)</label>
            <select v-model="selectedTopicId" class="form-select" :disabled="isRunning">
              <option :value="null">No specific track</option>
              <option v-for="t in topics" :key="t.id" :value="t.id">{{ t.title }}</option>
            </select>
          </div>
          <div style="flex: 1;">
            <label class="form-label" style="font-size: 0.78rem;">Session Title</label>
            <input
              v-model="sessionTitle"
              type="text"
              class="form-input"
              placeholder="e.g. Chapter 4 Practice"
              :disabled="isRunning"
            />
          </div>
        </div>

        <!-- Controls -->
        <div class="timer-controls">
          <button
            v-if="!isRunning"
            class="btn btn-primary btn-lg"
            style="min-width: 150px;"
            @click="startTimer"
          >
            <AppIcon name="play" :size="20" />
            Start Focus
          </button>
          <button
            v-else
            class="btn btn-danger btn-lg"
            style="min-width: 150px;"
            @click="pauseTimer"
          >
            <AppIcon name="pause" :size="20" />
            Pause
          </button>

          <button class="icon-btn" style="width: 46px; height: 46px;" title="Reset Timer" @click="resetTimer">
            <AppIcon name="refresh-cw" :size="18" />
          </button>

          <button
            v-if="secondsElapsed > 60"
            class="btn btn-success btn-lg"
            @click="saveCurrentSession"
          >
            <AppIcon name="check" :size="18" />
            Save & Log ({{ Math.round(secondsElapsed / 60) }}m)
          </button>
        </div>
      </div>

      <!-- TODAY'S STUDY STATS & RECENT SESSIONS (RIGHT) -->
      <div class="study-side-col">
        <div class="card stat-banner-card">
          <div class="stat-card-top">
            <span class="stat-label">Today's Focus Time</span>
            <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">
              <AppIcon name="clock" :size="18" />
            </div>
          </div>
          <div class="stat-value" style="font-size: 2.2rem; color: var(--primary);">
            {{ todayStats.total_hours }}<span style="font-size: 1.2rem; margin-left: 2px;">h</span>
          </div>
          <div class="stat-subtext">{{ todayStats.total_minutes }} total minutes across {{ todayStats.sessions_count }} sessions</div>
        </div>

        <!-- Recent Sessions History -->
        <div class="card" style="flex: 1;">
          <div class="card-header">
            <h3 class="card-title">Recent Study Log</h3>
          </div>

          <div v-if="sessions.length === 0" class="empty-state" style="padding: 1.5rem 0;">
            <p class="empty-desc" style="font-size: 0.8rem;">No study sessions logged yet.</p>
          </div>

          <div v-else class="sessions-history-list">
            <div
              v-for="s in sessions.slice(0, 7)"
              :key="s.id"
              class="session-history-item"
            >
              <div style="flex: 1;">
                <div style="font-weight: 700; font-size: 0.88rem;">{{ s.title }}</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); display: flex; gap: 0.5rem; margin-top: 2px;">
                  <span v-if="s.topic_title" style="color: var(--secondary);">{{ s.topic_title }}</span>
                  <span>{{ s.created_at.split('T')[0] }}</span>
                </div>
              </div>
              <div class="session-badge-duration">
                {{ s.duration_minutes }}m
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MANUAL LOG MODAL -->
    <div v-if="showManualModal" class="modal-backdrop" @click.self="showManualModal = false">
      <div class="modal-card" style="max-width: 480px;">
        <div class="modal-header">
          <h3 class="modal-title">Manually Log Session</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showManualModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="submitManualSession" class="modal-body">
          <div class="form-group">
            <label class="form-label">Session Title</label>
            <input v-model="manualForm.title" type="text" required class="form-input" placeholder="e.g. Deep Practice Session" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Learning Track</label>
              <select v-model="manualForm.topic" class="form-select">
                <option :value="null">No track</option>
                <option v-for="t in topics" :key="t.id" :value="t.id">{{ t.title }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Duration (Minutes)</label>
              <input v-model.number="manualForm.duration_minutes" type="number" min="1" required class="form-input" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Notes & Insights</label>
            <textarea v-model="manualForm.notes" class="form-textarea" placeholder="Key topics covered or questions..."></textarea>
          </div>

          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showManualModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Log Session</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const api = useApi()

const timerMode = ref('pomodoro') // 'pomodoro', 'short_break', 'stopwatch'
const timeLeft = ref(25 * 60)
const secondsElapsed = ref(0)
const isRunning = ref(false)
let timerInterval = null

const sessionTitle = ref('Focus Session')
const selectedTopicId = ref(null)

const topics = ref([])
const sessions = ref([])
const todayStats = ref({ total_hours: 0, total_minutes: 0, sessions_count: 0 })

const showManualModal = ref(false)
const manualForm = ref({
  title: 'Focused Study',
  topic: null,
  duration_minutes: 30,
  notes: ''
})

const formattedTime = computed(() => {
  let totalSecs = timerMode.value === 'stopwatch' ? secondsElapsed.value : timeLeft.value
  const mins = Math.floor(totalSecs / 60)
  const secs = totalSecs % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

const switchTimerMode = (mode) => {
  pauseTimer()
  timerMode.value = mode
  secondsElapsed.value = 0
  if (mode === 'pomodoro') {
    timeLeft.value = 25 * 60
  } else if (mode === 'short_break') {
    timeLeft.value = 5 * 60
  } else {
    timeLeft.value = 0
  }
}

const startTimer = () => {
  isRunning.value = true
  timerInterval = setInterval(() => {
    secondsElapsed.value += 1
    if (timerMode.value === 'stopwatch') {
      // count up
    } else {
      if (timeLeft.value > 0) {
        timeLeft.value -= 1
      } else {
        pauseTimer()
        alert('Timer completed! Great work!')
        saveCurrentSession()
      }
    }
  }, 1000)
}

const pauseTimer = () => {
  isRunning.value = false
  if (timerInterval) clearInterval(timerInterval)
}

const resetTimer = () => {
  pauseTimer()
  switchTimerMode(timerMode.value)
}

const saveCurrentSession = async () => {
  const duration = Math.max(1, Math.round(secondsElapsed.value / 60))
  try {
    await api.post('/learning/sessions/', {
      title: sessionTitle.value || 'Focus Session',
      topic: selectedTopicId.value,
      session_type: timerMode.value === 'stopwatch' ? 'stopwatch' : 'pomodoro',
      duration_minutes: duration
    })
    resetTimer()
    await fetchSessions()
    await fetchTodayStats()
  } catch (e) {
    alert('Error saving session: ' + e.message)
  }
}

const submitManualSession = async () => {
  try {
    await api.post('/learning/sessions/', manualForm.value)
    showManualModal.value = false
    await fetchSessions()
    await fetchTodayStats()
  } catch (e) {
    alert('Error logging session: ' + e.message)
  }
}

const fetchTopics = async () => {
  try {
    const res = await api.get('/learning/topics/')
    topics.value = res || []
  } catch (e) {
    console.error(e)
  }
}

const fetchSessions = async () => {
  try {
    const res = await api.get('/learning/sessions/')
    sessions.value = res || []
  } catch (e) {
    console.error(e)
  }
}

const fetchTodayStats = async () => {
  try {
    const res = await api.get('/learning/sessions/today/')
    if (res) todayStats.value = res
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  await fetchTopics()
  await fetchSessions()
  await fetchTodayStats()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
.study-page {
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

.study-layout-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1.5rem;
}

.timer-card {
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.timer-display-box {
  margin: 1.5rem 0 2rem;
}

.timer-clock-digits {
  font-family: var(--font-mono);
  font-size: 5rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--text-primary);
  line-height: 1;
}

.timer-mode-caption {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin-top: 0.75rem;
  font-weight: 600;
}

.timer-association-row {
  width: 100%;
  max-width: 480px;
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  text-align: left;
}

.timer-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.study-side-col {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.sessions-history-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.session-history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.85rem;
  background-color: var(--bg-elevated);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.session-badge-duration {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 700;
  background-color: var(--primary-light);
  color: var(--primary);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

@media (max-width: 1024px) {
  .study-layout-grid {
    grid-template-columns: 1fr;
  }
}
</style>

