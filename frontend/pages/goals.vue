<template>
  <div class="goals-page">
    <div class="page-top-bar">
      <div>
        <h2 class="view-title">Goals & Targets</h2>
        <p class="view-sub">Track short, medium, and long-term milestones with quantitative metrics.</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <AppIcon name="plus" :size="16" />
        New Goal
      </button>
    </div>

    <!-- Timeframe Filters -->
    <div class="card filter-bar-card">
      <div class="tabs-nav">
        <button class="tab-btn" :class="{ active: timeframeFilter === '' }" @click="timeframeFilter = ''">
          All Timeframes
        </button>
        <button class="tab-btn" :class="{ active: timeframeFilter === 'short_term' }" @click="timeframeFilter = 'short_term'">
          Short-term (&lt; 3 mo)
        </button>
        <button class="tab-btn" :class="{ active: timeframeFilter === 'medium_term' }" @click="timeframeFilter = 'medium_term'">
          Medium-term (3-12 mo)
        </button>
        <button class="tab-btn" :class="{ active: timeframeFilter === 'long_term' }" @click="timeframeFilter = 'long_term'">
          Long-term (1+ yr)
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <span style="margin-left: 0.75rem; color: var(--text-secondary);">Loading goals...</span>
    </div>

    <div v-else-if="filteredGoals.length === 0" class="card empty-state">
      <div class="empty-icon"><AppIcon name="target" :size="28" /></div>
      <div class="empty-title">No goals found</div>
      <p class="empty-desc">Set ambitious, quantifiable targets for your life, career, or learning.</p>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">Create Goal</button>
    </div>

    <div v-else class="goals-grid">
      <div
        v-for="goal in filteredGoals"
        :key="goal.id"
        class="card goal-card"
        :class="{ achieved: goal.status === 'achieved' }"
      >
        <div class="goal-header">
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <h3 class="goal-title">{{ goal.title }}</h3>
              <span class="badge" :class="goal.status === 'achieved' ? 'badge-success' : 'badge-primary'">
                {{ goal.status }}
              </span>
            </div>
            <div class="goal-tags">
              <span v-if="goal.category_details" class="badge" :style="{ backgroundColor: `${goal.category_details.color}22`, color: goal.category_details.color }">
                {{ goal.category_details.name }}
              </span>
              <span v-if="goal.target_date" class="badge badge-neutral">
                Target: {{ goal.target_date }}
              </span>
            </div>
          </div>

          <div style="display: flex; gap: 0.35rem;">
            <button class="icon-btn" style="width: 30px; height: 30px;" @click="openEditModal(goal)">
              <AppIcon name="edit" :size="13" />
            </button>
            <button class="icon-btn" style="width: 30px; height: 30px; color: var(--error);" @click="deleteGoal(goal)">
              <AppIcon name="trash" :size="13" />
            </button>
          </div>
        </div>

        <p v-if="goal.description" class="goal-desc">{{ goal.description }}</p>

        <!-- Progress Track & Quick Updater -->
        <div class="progress-box">
          <div class="progress-info-row">
            <span><strong>{{ goal.current_value }}</strong> / {{ goal.target_value }} {{ goal.unit }}</span>
            <span style="font-weight: 700; color: var(--secondary);">{{ goal.progress_percentage }}%</span>
          </div>
          <div class="progress-track" style="height: 8px; margin-top: 0.35rem;">
            <div class="progress-fill" :style="{ width: `${goal.progress_percentage}%` }"></div>
          </div>

          <!-- Quick Progress Update Input -->
          <div class="quick-progress-row">
            <span style="font-size: 0.75rem; color: var(--text-muted);">Update value:</span>
            <input
              type="number"
              class="form-input"
              style="width: 80px; padding: 0.2rem 0.5rem; font-size: 0.8rem;"
              :value="goal.current_value"
              @change="updateProgress(goal, $event.target.value)"
            />
            <span style="font-size: 0.75rem; color: var(--text-muted);">{{ goal.unit }}</span>
          </div>
        </div>

        <!-- Milestones -->
        <div class="goal-milestones-section">
          <div class="milestone-title-row">
            <span class="sub-lbl">Milestones ({{ goal.milestones.length }})</span>
            <button class="btn btn-ghost btn-sm" style="padding: 2px 6px; font-size: 0.72rem;" @click="openAddMilestone(goal)">
              + Add
            </button>
          </div>
          <div class="milestones-sub-list">
            <div
              v-for="ms in goal.milestones"
              :key="ms.id"
              class="milestone-sub-row"
              :class="{ done: ms.is_completed }"
            >
              <button class="ms-check-btn" :class="{ active: ms.is_completed }" @click="toggleMilestone(ms)">
                <AppIcon v-if="ms.is_completed" name="check" :size="11" />
              </button>
              <span class="ms-title">{{ ms.title }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT GOAL MODAL -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditing ? 'Edit Goal' : 'Create Goal' }}</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="saveGoal" class="modal-body">
          <div class="form-group">
            <label class="form-label">Goal Title *</label>
            <input
              v-model="form.title"
              type="text"
              required
              class="form-input"
              placeholder="e.g. Master Cloud DevOps, Read 12 Books, Run 500km"
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
              <label class="form-label">Timeframe</label>
              <select v-model="form.timeframe" class="form-select">
                <option value="short_term">Short-term (&lt; 3 mo)</option>
                <option value="medium_term">Medium-term (3-12 mo)</option>
                <option value="long_term">Long-term (1+ yr)</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Target Value</label>
              <input v-model.number="form.target_value" type="number" step="any" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Current Value</label>
              <input v-model.number="form.current_value" type="number" step="any" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Unit</label>
              <input v-model="form.unit" type="text" class="form-input" placeholder="%, books, km, hrs" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Target Date</label>
              <input v-model="form.target_date" type="date" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Status</label>
              <select v-model="form.status" class="form-select">
                <option value="not_started">Not Started</option>
                <option value="in_progress">In Progress</option>
                <option value="achieved">Achieved</option>
                <option value="abandoned">Abandoned</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Description & Strategy</label>
            <textarea
              v-model="form.description"
              class="form-textarea"
              placeholder="Why this goal matters and your action strategy..."
            ></textarea>
          </div>

          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Save Goal</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ADD MILESTONE MODAL -->
    <div v-if="showMilestoneModal" class="modal-backdrop" @click.self="showMilestoneModal = false">
      <div class="modal-card" style="max-width: 440px;">
        <div class="modal-header">
          <h3 class="modal-title">Add Goal Milestone</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showMilestoneModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="submitMilestone" class="modal-body">
          <div class="form-group">
            <label class="form-label">Milestone Title</label>
            <input v-model="milestoneTitle" type="text" required class="form-input" placeholder="e.g. Complete chapter 5, reach 50km" />
          </div>
          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showMilestoneModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Add Milestone</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const api = useApi()

const goals = ref([])
const categories = ref([])
const isLoading = ref(true)
const timeframeFilter = ref('')

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const showMilestoneModal = ref(false)
const activeGoalForMilestone = ref(null)
const milestoneTitle = ref('')

const form = ref({
  title: '',
  description: '',
  category: null,
  timeframe: 'short_term',
  target_date: null,
  target_value: 100.0,
  current_value: 0.0,
  unit: '%',
  status: 'in_progress'
})

const fetchGoals = async () => {
  isLoading.value = true
  try {
    let url = '/goals/'
    if (timeframeFilter.value) url += `?timeframe=${timeframeFilter.value}`
    const res = await api.get(url)
    goals.value = res || []
  } catch (e) {
    console.error('Error fetching goals', e)
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

const filteredGoals = computed(() => goals.value)

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = {
    title: '',
    description: '',
    category: categories.value[0]?.id || null,
    timeframe: 'short_term',
    target_date: null,
    target_value: 100.0,
    current_value: 0.0,
    unit: '%',
    status: 'in_progress'
  }
  showModal.value = true
}

const openEditModal = (g) => {
  isEditing.value = true
  editingId.value = g.id
  form.value = {
    title: g.title,
    description: g.description,
    category: g.category,
    timeframe: g.timeframe,
    target_date: g.target_date,
    target_value: g.target_value,
    current_value: g.current_value,
    unit: g.unit,
    status: g.status
  }
  showModal.value = true
}

const saveGoal = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/goals/${editingId.value}/`, form.value)
    } else {
      await api.post('/goals/', form.value)
    }
    showModal.value = false
    await fetchGoals()
  } catch (e) {
    alert('Error saving goal: ' + e.message)
  }
}

const deleteGoal = async (g) => {
  if (confirm(`Delete goal "${g.title}"?`)) {
    try {
      await api.delete(`/goals/${g.id}/`)
      await fetchGoals()
    } catch (e) {
      alert('Error deleting goal: ' + e.message)
    }
  }
}

const updateProgress = async (goal, val) => {
  try {
    const res = await api.post(`/goals/${goal.id}/progress/`, { current_value: val })
    goal.current_value = res.current_value
    goal.progress_percentage = res.progress_percentage
    goal.status = res.status
  } catch (e) {
    alert('Error updating goal: ' + e.message)
  }
}

const openAddMilestone = (goal) => {
  activeGoalForMilestone.value = goal
  milestoneTitle.value = ''
  showMilestoneModal.value = true
}

const submitMilestone = async () => {
  try {
    await api.post(`/goals/${activeGoalForMilestone.value.id}/milestones/`, { title: milestoneTitle.value })
    showMilestoneModal.value = false
    await fetchGoals()
  } catch (e) {
    alert('Error adding milestone: ' + e.message)
  }
}

const toggleMilestone = async (ms) => {
  try {
    const res = await api.post(`/goals/milestones/${ms.id}/toggle/`)
    ms.is_completed = res.is_completed
  } catch (e) {
    alert('Error toggling milestone: ' + e.message)
  }
}

watch(timeframeFilter, () => {
  fetchGoals()
})

onMounted(async () => {
  await fetchCategories()
  await fetchGoals()
})
</script>

<style scoped>
.goals-page {
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

.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
}

.goal-card {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.goal-card.achieved {
  border-color: var(--success);
}

.goal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.goal-title {
  font-size: 1.05rem;
  font-weight: 700;
}

.goal-tags {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.35rem;
}

.goal-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.progress-box {
  background-color: var(--bg-elevated);
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.progress-info-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
}

.quick-progress-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.6rem;
}

.goal-milestones-section {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.milestone-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sub-lbl {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
}

.milestones-sub-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.milestone-sub-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  padding: 0.3rem 0.5rem;
  background-color: var(--bg-elevated);
  border-radius: var(--radius-sm);
}

.milestone-sub-row.done .ms-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.ms-check-btn {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border-light);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
}

.ms-check-btn.active {
  background-color: var(--primary);
  border-color: var(--primary);
}

.ms-title {
  flex: 1;
}
</style>

