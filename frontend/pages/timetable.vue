<template>
  <div class="timetable-page">
    <!-- Header Controls & Views Switcher -->
    <div class="timetable-header">
      <div class="timetable-nav-controls">
        <div class="date-navigator">
          <button class="icon-btn" title="Previous period" @click="navigatePeriod(-1)">
            <AppIcon name="chevron-left" :size="18" />
          </button>
          <button class="btn btn-outline btn-sm" @click="goToToday">
            Today
          </button>
          <button class="icon-btn" title="Next period" @click="navigatePeriod(1)">
            <AppIcon name="chevron-right" :size="18" />
          </button>
          <span class="period-label">{{ currentPeriodLabel }}</span>
        </div>

        <!-- View Switcher (Daily, Weekly, Monthly, Agenda) -->
        <div class="tabs-nav">
          <button
            class="tab-btn"
            :class="{ active: currentView === 'daily' }"
            @click="currentView = 'daily'"
          >
            Daily
          </button>
          <button
            class="tab-btn"
            :class="{ active: currentView === 'weekly' }"
            @click="currentView = 'weekly'"
          >
            Weekly
          </button>
          <button
            class="tab-btn"
            :class="{ active: currentView === 'monthly' }"
            @click="currentView = 'monthly'"
          >
            Monthly
          </button>
          <button
            class="tab-btn"
            :class="{ active: currentView === 'agenda' }"
            @click="currentView = 'agenda'"
          >
            Agenda
          </button>
        </div>
      </div>

      <!-- Actions: Filter & New Activity -->
      <div class="timetable-actions">
        <!-- Category Filter -->
        <select v-model="filterCategory" class="form-select" style="width: auto; padding: 0.45rem 2rem 0.45rem 0.75rem; font-size: 0.85rem;">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>

        <button class="btn btn-primary btn-sm" @click="openCreateModal">
          <AppIcon name="plus" :size="16" />
          New Activity
        </button>
      </div>
    </div>

    <!-- Conflict Warning Banner (if any conflict detected in real-time) -->
    <div v-if="realtimeConflicts.length > 0" class="conflict-alert-banner">
      <AppIcon name="alert-circle" :size="20" />
      <div>
        <strong>Schedule Conflict Detected:</strong>
        <span v-for="(c, idx) in realtimeConflicts" :key="idx" style="margin-left: 0.5rem;">
          "{{ c.title }}" ({{ c.start_time }}-{{ c.end_time }})
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <span style="margin-left: 0.75rem; color: var(--text-secondary);">Loading timetable occurrences...</span>
    </div>

    <div v-else>
      <!-- 1. DAILY VIEW -->
      <div v-if="currentView === 'daily'" class="card daily-view-card">
        <div class="view-subhead">
          <h3>{{ formatLongDate(selectedDate) }}</h3>
          <span class="badge badge-primary">{{ occurrences.length }} activities</span>
        </div>

        <div v-if="occurrences.length === 0" class="empty-state">
          <div class="empty-icon"><AppIcon name="calendar" :size="28" /></div>
          <div class="empty-title">No activities on this date</div>
          <p class="empty-desc">Click "New Activity" above to schedule an activity or routine for this day.</p>
          <button class="btn btn-primary btn-sm" @click="openCreateModal">Add Activity</button>
        </div>

        <div v-else class="schedule-list">
          <div
            v-for="item in occurrences"
            :key="item.instance_id"
            class="schedule-card"
            :class="{ completed: item.status === 'completed', skipped: item.status === 'skipped' }"
            :style="{ borderLeftColor: item.color || 'var(--primary)' }"
          >
            <div class="schedule-time-block">
              <span class="schedule-time">{{ item.start_time }}</span>
              <span class="schedule-duration">{{ item.end_time }}</span>
            </div>
            <div class="schedule-info">
              <div class="schedule-title" :class="{ done: item.status === 'completed' }">
                <span>{{ item.title }}</span>
                <span v-if="item.is_recurring" class="badge badge-neutral" style="font-size: 0.65rem;">
                  <AppIcon name="repeat" :size="10" />
                  {{ item.recurrence }}
                </span>
                <span v-if="item.status === 'completed'" class="badge badge-success">Completed</span>
                <span v-if="item.status === 'skipped'" class="badge badge-neutral">Skipped</span>
              </div>
              <div class="schedule-meta">
                <span
                  v-if="item.category"
                  class="badge"
                  :style="{ backgroundColor: `${item.category.color}22`, color: item.category.color }"
                >
                  {{ item.category.name }}
                </span>
                <span :class="`priority-${item.priority}`" style="font-weight: 600; text-transform: capitalize;">
                  {{ item.priority }}
                </span>
                <span v-if="item.reminder_minutes > 0">
                  🔔 {{ item.reminder_minutes }}m reminder
                </span>
              </div>
              <p v-if="item.description" style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.25rem;">
                {{ item.description }}
              </p>
            </div>
            <div class="schedule-actions">
              <!-- Complete / Undo -->
              <button
                v-if="item.status !== 'completed'"
                class="btn btn-success btn-sm"
                @click="markComplete(item)"
              >
                <AppIcon name="check" :size="14" />
                Done
              </button>
              <button
                v-else
                class="btn btn-ghost btn-sm"
                @click="markUncomplete(item)"
              >
                Undo
              </button>

              <!-- Skip -->
              <button
                v-if="item.status === 'pending'"
                class="btn btn-outline btn-sm"
                title="Skip this occurrence"
                @click="markSkip(item)"
              >
                Skip
              </button>

              <!-- Reschedule -->
              <button
                class="icon-btn"
                style="width: 32px; height: 32px;"
                title="Reschedule"
                @click="openRescheduleModal(item)"
              >
                <AppIcon name="clock" :size="14" />
              </button>

              <!-- Duplicate -->
              <button
                class="icon-btn"
                style="width: 32px; height: 32px;"
                title="Duplicate activity"
                @click="duplicateActivity(item)"
              >
                <AppIcon name="copy" :size="14" />
              </button>

              <!-- Edit Activity Definition -->
              <button
                class="icon-btn"
                style="width: 32px; height: 32px;"
                title="Edit Activity"
                @click="openEditModal(item)"
              >
                <AppIcon name="edit" :size="14" />
              </button>

              <!-- Delete Activity -->
              <button
                class="icon-btn"
                style="width: 32px; height: 32px; color: var(--error);"
                title="Delete Activity"
                @click="deleteActivity(item)"
              >
                <AppIcon name="trash" :size="14" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. WEEKLY VIEW -->
      <div v-else-if="currentView === 'weekly'" class="card weekly-view-card">
        <div class="weekly-columns-grid">
          <div
            v-for="day in weekDaysList"
            :key="day.dateStr"
            class="week-col"
            :class="{ 'is-today': day.dateStr === todayStr }"
          >
            <div class="week-col-header">
              <span class="day-short">{{ day.dayName }}</span>
              <span class="day-number">{{ day.dayNum }}</span>
            </div>
            <div class="week-col-body">
              <div
                v-for="occ in dayOccurrences(day.dateStr)"
                :key="occ.instance_id"
                class="week-event-chip"
                :style="{ borderLeftColor: occ.color || 'var(--primary)' }"
                :class="{ completed: occ.status === 'completed', skipped: occ.status === 'skipped' }"
                @click="activeDetailItem = occ"
              >
                <div class="chip-time">{{ occ.start_time }}</div>
                <div class="chip-title">{{ occ.title }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. MONTHLY VIEW -->
      <div v-else-if="currentView === 'monthly'" class="card monthly-view-card">
        <div class="month-weekday-names">
          <div v-for="wd in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="wd" class="wd-name">
            {{ wd }}
          </div>
        </div>
        <div class="month-days-grid">
          <div
            v-for="cell in monthCells"
            :key="cell.dateStr"
            class="month-cell"
            :class="{
              'is-today': cell.dateStr === todayStr,
              'diff-month': !cell.isCurrentMonth
            }"
            @click="selectedDate = new Date(cell.dateStr); currentView = 'daily'"
          >
            <div class="cell-num">{{ cell.dayNum }}</div>
            <div class="cell-events">
              <div
                v-for="occ in dayOccurrences(cell.dateStr).slice(0, 3)"
                :key="occ.instance_id"
                class="cell-event-dot"
                :style="{ backgroundColor: occ.color || 'var(--primary)' }"
                :title="`${occ.start_time} ${occ.title}`"
              >
                <span>{{ occ.start_time }} {{ occ.title }}</span>
              </div>
              <div v-if="dayOccurrences(cell.dateStr).length > 3" class="cell-more">
                +{{ dayOccurrences(cell.dateStr).length - 3 }} more
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. AGENDA VIEW -->
      <div v-else-if="currentView === 'agenda'" class="card agenda-view-card">
        <div class="view-subhead">
          <h3>Upcoming 30-Day Agenda</h3>
          <span class="badge badge-primary">{{ occurrences.length }} occurrences</span>
        </div>

        <div v-if="agendaGrouped.length === 0" class="empty-state">
          <div class="empty-title">No upcoming activities found</div>
          <p class="empty-desc">Your agenda is clear for the next 30 days.</p>
        </div>

        <div v-else class="agenda-groups">
          <div v-for="grp in agendaGrouped" :key="grp.dateStr" class="agenda-date-group">
            <div class="agenda-date-header">
              <span class="agenda-date-title">{{ formatLongDate(new Date(grp.dateStr)) }}</span>
              <span v-if="grp.dateStr === todayStr" class="badge badge-success">Today</span>
            </div>
            <div class="schedule-list">
              <div
                v-for="item in grp.items"
                :key="item.instance_id"
                class="schedule-card"
                :class="{ completed: item.status === 'completed', skipped: item.status === 'skipped' }"
                :style="{ borderLeftColor: item.color || 'var(--primary)' }"
              >
                <div class="schedule-time-block">
                  <span class="schedule-time">{{ item.start_time }}</span>
                  <span class="schedule-duration">{{ item.end_time }}</span>
                </div>
                <div class="schedule-info">
                  <div class="schedule-title" :class="{ done: item.status === 'completed' }">
                    {{ item.title }}
                  </div>
                  <div class="schedule-meta">
                    <span v-if="item.category" class="badge" :style="{ backgroundColor: `${item.category.color}22`, color: item.category.color }">
                      {{ item.category.name }}
                    </span>
                    <span :class="`priority-${item.priority}`" style="text-transform: capitalize;">
                      {{ item.priority }}
                    </span>
                  </div>
                </div>
                <div class="schedule-actions">
                  <button v-if="item.status !== 'completed'" class="btn btn-success btn-sm" @click="markComplete(item)">
                    <AppIcon name="check" :size="13" />
                  </button>
                  <button class="icon-btn" style="width: 30px; height: 30px;" @click="activeDetailItem = item">
                    <AppIcon name="file-text" :size="14" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT ACTIVITY MODAL -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditing ? 'Edit Activity' : 'Create New Activity' }}</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>

        <form @submit.prevent="saveActivity" class="modal-body">
          <!-- Realtime Conflict Check Notice in Modal -->
          <div v-if="formConflictWarning" class="conflict-alert-banner" style="margin-bottom: 1rem;">
            <AppIcon name="alert-circle" :size="18" />
            <span>{{ formConflictWarning }}</span>
          </div>

          <!-- Title -->
          <div class="form-group">
            <label class="form-label">Activity Title *</label>
            <input
              v-model="form.title"
              type="text"
              required
              class="form-input"
              placeholder="e.g. Focus Work Session, Workout, German Practice"
            />
          </div>

          <!-- Category & Priority -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Category</label>
              <select v-model="form.category" class="form-select">
                <option :value="null">No Category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Priority</label>
              <select v-model="form.priority" class="form-select">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          <!-- Date & Time Range -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Date *</label>
              <input
                v-model="form.date"
                type="date"
                required
                class="form-input"
                @change="checkFormConflicts"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Start Time *</label>
              <input
                v-model="form.start_time"
                type="time"
                required
                class="form-input"
                @change="checkFormConflicts"
              />
            </div>
            <div class="form-group">
              <label class="form-label">End Time *</label>
              <input
                v-model="form.end_time"
                type="time"
                required
                class="form-input"
                @change="checkFormConflicts"
              />
            </div>
          </div>

          <!-- Recurrence Options -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Recurrence</label>
              <select v-model="form.recurrence" class="form-select">
                <option value="none">Does not repeat</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="selected_weekdays">Selected weekdays</option>
                <option value="monthly">Monthly</option>
                <option value="custom">Custom recurrence</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Reminder</label>
              <select v-model="form.reminder_minutes" class="form-select">
                <option :value="0">No reminder</option>
                <option :value="5">5 minutes before</option>
                <option :value="10">10 minutes before</option>
                <option :value="15">15 minutes before</option>
                <option :value="30">30 minutes before</option>
                <option :value="60">1 hour before</option>
              </select>
            </div>
          </div>

          <!-- Weekday Selection (if selected_weekdays or custom) -->
          <div
            v-if="form.recurrence === 'selected_weekdays' || form.recurrence === 'custom'"
            class="form-group"
          >
            <label class="form-label">Repeat On Weekdays</label>
            <div class="weekdays-selector">
              <button
                v-for="(dayName, dIdx) in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']"
                :key="dIdx"
                type="button"
                class="weekday-toggle-btn"
                :class="{ active: form.selected_weekdays.includes(dIdx) }"
                @click="toggleWeekday(dIdx)"
              >
                {{ dayName }}
              </button>
            </div>
          </div>

          <!-- Optional Recurrence End Date -->
          <div v-if="form.recurrence !== 'none'" class="form-group">
            <label class="form-label">Recurrence End Date (Optional)</label>
            <input v-model="form.end_date" type="date" class="form-input" />
          </div>

          <!-- Visual Color -->
          <div class="form-group">
            <label class="form-label">Visual Color Label</label>
            <div class="color-palette-row">
              <button
                v-for="color in presetColors"
                :key="color"
                type="button"
                class="color-circle"
                :style="{ backgroundColor: color }"
                :class="{ selected: form.color === color }"
                @click="form.color = color"
              ></button>
            </div>
          </div>

          <!-- Description -->
          <div class="form-group">
            <label class="form-label">Description & Notes</label>
            <textarea
              v-model="form.description"
              class="form-textarea"
              placeholder="Add activity objectives, locations, or notes..."
            ></textarea>
          </div>

          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Activity') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- RESCHEDULE MODAL -->
    <div v-if="showRescheduleModal" class="modal-backdrop" @click.self="showRescheduleModal = false">
      <div class="modal-card" style="max-width: 440px;">
        <div class="modal-header">
          <h3 class="modal-title">Reschedule Occurrence</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showRescheduleModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="submitReschedule" class="modal-body">
          <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 1rem;">
            Rescheduling: <strong>{{ reschedulingItem?.title }}</strong>
          </p>

          <div class="form-group">
            <label class="form-label">New Date</label>
            <input v-model="rescheduleForm.new_date" type="date" required class="form-input" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">New Start Time</label>
              <input v-model="rescheduleForm.new_start_time" type="time" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">New End Time</label>
              <input v-model="rescheduleForm.new_end_time" type="time" required class="form-input" />
            </div>
          </div>

          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showRescheduleModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Reschedule</button>
          </div>
        </form>
      </div>
    </div>

    <!-- DETAIL ITEM MODAL -->
    <div v-if="activeDetailItem" class="modal-backdrop" @click.self="activeDetailItem = null">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ activeDetailItem.title }}</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="activeDetailItem = null">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <div class="modal-body">
          <div style="display: flex; flex-direction: column; gap: 0.85rem;">
            <div>
              <span class="form-label">Date & Time</span>
              <p style="font-family: var(--font-mono); font-size: 0.95rem; color: var(--text-primary); margin-top: 0.2rem;">
                {{ activeDetailItem.occurrence_date }} • {{ activeDetailItem.start_time }} - {{ activeDetailItem.end_time }}
              </p>
            </div>

            <div v-if="activeDetailItem.category">
              <span class="form-label">Category</span>
              <div style="margin-top: 0.2rem;">
                <span class="badge" :style="{ backgroundColor: `${activeDetailItem.category.color}22`, color: activeDetailItem.category.color }">
                  {{ activeDetailItem.category.name }}
                </span>
              </div>
            </div>

            <div>
              <span class="form-label">Priority & Status</span>
              <div style="display: flex; gap: 0.5rem; margin-top: 0.2rem;">
                <span class="badge badge-neutral" style="text-transform: capitalize;">Priority: {{ activeDetailItem.priority }}</span>
                <span class="badge" :class="activeDetailItem.status === 'completed' ? 'badge-success' : 'badge-neutral'">Status: {{ activeDetailItem.status }}</span>
              </div>
            </div>

            <div v-if="activeDetailItem.description">
              <span class="form-label">Description</span>
              <p style="font-size: 0.88rem; color: var(--text-secondary); margin-top: 0.2rem; background: var(--bg-input); padding: 0.75rem; border-radius: var(--radius-md);">
                {{ activeDetailItem.description }}
              </p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary btn-sm" @click="activeDetailItem = null">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const api = useApi()

const currentView = ref('daily') // 'daily', 'weekly', 'monthly', 'agenda'
const selectedDate = ref(new Date())
const isLoading = ref(false)
const occurrences = ref([])
const categories = ref([])
const filterCategory = ref('')
const realtimeConflicts = ref([])
const formConflictWarning = ref('')

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const isSaving = ref(false)

const showRescheduleModal = ref(false)
const reschedulingItem = ref(null)
const rescheduleForm = ref({
  new_date: '',
  new_start_time: '',
  new_end_time: ''
})

const activeDetailItem = ref(null)

const presetColors = [
  '#7C6CFF', '#38BDF8', '#22C55E', '#F59E0B', '#EF4444',
  '#EC4899', '#8B5CF6', '#14B8A6', '#64748B'
]

const form = ref({
  title: '',
  description: '',
  category: null,
  date: new Date().toISOString().split('T')[0],
  start_time: '09:00',
  end_time: '10:00',
  priority: 'medium',
  reminder_minutes: 15,
  recurrence: 'none',
  selected_weekdays: [0, 1, 2, 3, 4],
  end_date: null,
  color: '#7C6CFF'
})

const todayStr = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const formatLongDate = (d) => {
  return d.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const currentPeriodLabel = computed(() => {
  const d = selectedDate.value
  if (currentView.value === 'daily') {
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
  } else if (currentView.value === 'weekly') {
    const start = getWeekStart(d)
    const end = new Date(start)
    end.setDate(end.getDate() + 6)
    return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} – ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  } else if (currentView.value === 'monthly') {
    return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  } else {
    return 'Upcoming 30 Days'
  }
})

const getWeekStart = (d) => {
  const date = new Date(d)
  const day = date.getDay()
  const diff = date.getDate() - day + (day === 0 ? -6 : 1) // Adjust for Monday start
  return new Date(date.setDate(diff))
}

const navigatePeriod = (delta) => {
  const d = new Date(selectedDate.value)
  if (currentView.value === 'daily') {
    d.setDate(d.getDate() + delta)
  } else if (currentView.value === 'weekly') {
    d.setDate(d.getDate() + (delta * 7))
  } else if (currentView.value === 'monthly') {
    d.setMonth(d.getMonth() + delta)
  }
  selectedDate.value = d
  fetchOccurrences()
}

const goToToday = () => {
  selectedDate.value = new Date()
  fetchOccurrences()
}

// Compute date ranges for the current view
const computedRange = computed(() => {
  const d = selectedDate.value
  let start = new Date(d)
  let end = new Date(d)

  if (currentView.value === 'daily') {
    // 1 day
  } else if (currentView.value === 'weekly') {
    start = getWeekStart(d)
    end = new Date(start)
    end.setDate(end.getDate() + 6)
  } else if (currentView.value === 'monthly') {
    start = new Date(d.getFullYear(), d.getMonth(), 1)
    end = new Date(d.getFullYear(), d.getMonth() + 1, 0)
    // expand to include full week cells
    const startWeek = getWeekStart(start)
    start = startWeek
    const endWeek = new Date(getWeekStart(end))
    endWeek.setDate(endWeek.getDate() + 6)
    end = endWeek
  } else if (currentView.value === 'agenda') {
    end = new Date(d)
    end.setDate(end.getDate() + 30)
  }

  return {
    start_date: start.toISOString().split('T')[0],
    end_date: end.toISOString().split('T')[0]
  }
})

// Fetch occurrences from API
const fetchOccurrences = async () => {
  isLoading.value = true
  try {
    const range = computedRange.value
    let url = `/timetable/activities/occurrences/?start_date=${range.start_date}&end_date=${range.end_date}`
    if (filterCategory.value) {
      url += `&category=${filterCategory.value}`
    }
    const res = await api.get(url)
    occurrences.value = res || []
  } catch (e) {
    console.error('Error fetching timetable occurrences', e)
  } finally {
    isLoading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/categories/')
    categories.value = res || []
  } catch (e) {
    console.error('Error fetching categories', e)
  }
}

// Filter occurrences for a specific day
const dayOccurrences = (dateStr) => {
  return occurrences.value.filter(o => o.occurrence_date === dateStr)
}

// Weekly days helper
const weekDaysList = computed(() => {
  const start = getWeekStart(selectedDate.value)
  const days = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(start)
    d.setDate(d.getDate() + i)
    days.push({
      dateStr: d.toISOString().split('T')[0],
      dayName: d.toLocaleDateString('en-US', { weekday: 'short' }),
      dayNum: d.getDate()
    })
  }
  return days
})

// Monthly cells helper
const monthCells = computed(() => {
  const range = computedRange.value
  const start = new Date(range.start_date)
  const end = new Date(range.end_date)
  const cells = []
  const currentMonthNum = selectedDate.value.getMonth()

  let curr = new Date(start)
  while (curr <= end) {
    cells.push({
      dateStr: curr.toISOString().split('T')[0],
      dayNum: curr.getDate(),
      isCurrentMonth: curr.getMonth() === currentMonthNum
    })
    curr.setDate(curr.getDate() + 1)
  }
  return cells
})

// Agenda grouped by date
const agendaGrouped = computed(() => {
  const groups = {}
  occurrences.value.forEach(occ => {
    if (!groups[occ.occurrence_date]) {
      groups[occ.occurrence_date] = []
    }
    groups[occ.occurrence_date].push(occ)
  })
  return Object.keys(groups).sort().map(d => ({
    dateStr: d,
    items: groups[d]
  }))
})

// Real-time conflict detection check in modal
const checkFormConflicts = async () => {
  if (!form.value.date || !form.value.start_time || !form.value.end_time) return
  if (form.value.start_time >= form.value.end_time) {
    formConflictWarning.value = 'End time must be after start time.'
    return
  }
  try {
    const res = await api.post('/timetable/activities/detect-conflicts/', {
      date: form.value.date,
      start_time: form.value.start_time,
      end_time: form.value.end_time,
      exclude_activity_id: isEditing.value ? editingId.value : null
    })
    if (res.has_conflicts) {
      formConflictWarning.value = `Time overlaps with: ${res.conflicts.map(c => c.title).join(', ')}`
    } else {
      formConflictWarning.value = ''
    }
  } catch (e) {
    // ignore
  }
}

const toggleWeekday = (idx) => {
  const list = form.value.selected_weekdays
  if (list.includes(idx)) {
    form.value.selected_weekdays = list.filter(x => x !== idx)
  } else {
    form.value.selected_weekdays = [...list, idx].sort()
  }
}

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  formConflictWarning.value = ''
  form.value = {
    title: '',
    description: '',
    category: categories.value[0]?.id || null,
    date: selectedDate.value.toISOString().split('T')[0],
    start_time: '09:00',
    end_time: '10:00',
    priority: 'medium',
    reminder_minutes: 15,
    recurrence: 'none',
    selected_weekdays: [0, 1, 2, 3, 4],
    end_date: null,
    color: '#7C6CFF'
  }
  showModal.value = true
}

const openEditModal = (item) => {
  isEditing.value = true
  editingId.value = item.activity_id
  formConflictWarning.value = ''
  form.value = {
    title: item.title,
    description: item.description,
    category: item.category_id,
    date: item.original_date || item.occurrence_date,
    start_time: item.start_time,
    end_time: item.end_time,
    priority: item.priority,
    reminder_minutes: item.reminder_minutes,
    recurrence: item.recurrence,
    selected_weekdays: item.selected_weekdays || [0, 1, 2, 3, 4],
    end_date: item.end_date,
    color: item.color || '#7C6CFF'
  }
  showModal.value = true
}

const saveActivity = async () => {
  if (form.value.start_time >= form.value.end_time) {
    alert('End time must be after start time.')
    return
  }
  isSaving.value = true
  try {
    if (isEditing.value) {
      await api.put(`/timetable/activities/${editingId.value}/`, form.value)
    } else {
      await api.post('/timetable/activities/', form.value)
    }
    showModal.value = false
    await fetchOccurrences()
  } catch (err) {
    alert('Error saving activity: ' + err.message)
  } finally {
    isSaving.value = false
  }
}

const deleteActivity = async (item) => {
  if (confirm(`Are you sure you want to delete the activity "${item.title}"?`)) {
    try {
      await api.delete(`/timetable/activities/${item.activity_id}/`)
      await fetchOccurrences()
    } catch (e) {
      alert('Error deleting activity: ' + e.message)
    }
  }
}

const duplicateActivity = async (item) => {
  try {
    await api.post(`/timetable/activities/${item.activity_id}/duplicate/`)
    await fetchOccurrences()
  } catch (e) {
    alert('Error duplicating activity: ' + e.message)
  }
}

// Complete / Skip / Reschedule actions
const markComplete = async (item) => {
  try {
    await api.post(`/timetable/activities/${item.activity_id}/complete/`, {
      date: item.occurrence_date
    })
    item.status = 'completed'
  } catch (e) {
    alert('Error marking complete: ' + e.message)
  }
}

const markUncomplete = async (item) => {
  try {
    await api.post(`/timetable/activities/${item.activity_id}/uncomplete/`, {
      date: item.occurrence_date
    })
    item.status = 'pending'
  } catch (e) {
    alert('Error undoing completion: ' + e.message)
  }
}

const markSkip = async (item) => {
  try {
    await api.post(`/timetable/activities/${item.activity_id}/skip/`, {
      date: item.occurrence_date
    })
    item.status = 'skipped'
  } catch (e) {
    alert('Error skipping activity: ' + e.message)
  }
}

const openRescheduleModal = (item) => {
  reschedulingItem.value = item
  rescheduleForm.value = {
    new_date: item.occurrence_date,
    new_start_time: item.start_time,
    new_end_time: item.end_time
  }
  showRescheduleModal.value = true
}

const submitReschedule = async () => {
  try {
    await api.post(`/timetable/activities/${reschedulingItem.value.activity_id}/reschedule/`, {
      date: reschedulingItem.value.occurrence_date,
      new_date: rescheduleForm.value.new_date,
      new_start_time: rescheduleForm.value.new_start_time,
      new_end_time: rescheduleForm.value.new_end_time
    })
    showRescheduleModal.value = false
    await fetchOccurrences()
  } catch (e) {
    alert('Error rescheduling activity: ' + e.message)
  }
}

watch([currentView, filterCategory], () => {
  fetchOccurrences()
})

onMounted(async () => {
  if (import.meta.client) {
    const token = localStorage.getItem('mydaily_access_token')
    if (!token) {
      navigateTo('/login')
      return
    }
    await fetchCategories()
    await fetchOccurrences()
  }
})
</script>

<style scoped>
.timetable-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.timetable-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.timetable-nav-controls {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.date-navigator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.period-label {
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--text-primary);
  margin-left: 0.5rem;
  white-space: nowrap;
}

.timetable-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.conflict-alert-banner {
  background-color: var(--warning-light);
  border: 1px solid var(--warning);
  color: var(--warning);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.88rem;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
}

.view-subhead {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

/* Weekly View Grid */
.weekly-columns-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.75rem;
  min-height: 480px;
}

.week-col {
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.week-col.is-today {
  border-color: var(--primary);
  background-color: var(--primary-light);
}

.week-col-header {
  padding: 0.6rem 0.5rem;
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.day-short {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
}

.day-number {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
}

.week-col-body {
  padding: 0.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  overflow-y: auto;
}

.week-event-chip {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--primary);
  border-radius: var(--radius-sm);
  padding: 0.4rem 0.5rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.week-event-chip:hover {
  transform: translateY(-1px);
  border-color: var(--border-light);
}

.week-event-chip.completed {
  opacity: 0.5;
}

.chip-time {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.68rem;
  color: var(--text-muted);
}

.chip-title {
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Monthly View Grid */
.month-weekday-names {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  padding-bottom: 0.65rem;
  border-bottom: 1px solid var(--border-color);
  font-weight: 700;
  font-size: 0.78rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.month-days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background-color: var(--border-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin-top: 0.75rem;
}

.month-cell {
  background-color: var(--bg-card);
  min-height: 95px;
  padding: 0.45rem;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.month-cell:hover {
  background-color: var(--bg-card-hover);
}

.month-cell.is-today {
  background-color: var(--primary-light);
}

.month-cell.diff-month {
  opacity: 0.35;
}

.cell-num {
  font-size: 0.8rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.cell-events {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  overflow: hidden;
}

.cell-event-dot {
  font-size: 0.68rem;
  padding: 1px 4px;
  border-radius: 3px;
  color: #FFFFFF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cell-more {
  font-size: 0.65rem;
  color: var(--text-muted);
  font-weight: 600;
}

/* Agenda View */
.agenda-groups {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.agenda-date-group {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.agenda-date-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.agenda-date-title {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
}

/* Weekday Selector */
.weekdays-selector {
  display: flex;
  gap: 0.4rem;
}

.weekday-toggle-btn {
  flex: 1;
  padding: 0.45rem;
  font-size: 0.78rem;
  font-weight: 700;
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.weekday-toggle-btn.active {
  background-color: var(--primary);
  color: #FFFFFF;
  border-color: var(--primary);
}

/* Color Circle */
.color-palette-row {
  display: flex;
  gap: 0.5rem;
}

.color-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.color-circle:hover {
  transform: scale(1.15);
}

.color-circle.selected {
  border-color: #FFFFFF;
  transform: scale(1.15);
}

@media (max-width: 768px) {
  .weekly-columns-grid {
    grid-template-columns: 1fr;
  }
}
</style>

