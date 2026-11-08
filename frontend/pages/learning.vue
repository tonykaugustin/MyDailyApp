<template>
  <div class="learning-page">
    <div class="page-top-bar">
      <div>
        <h2 class="view-title">Dynamic Learning Tracks</h2>
        <p class="view-sub">Track self-directed learning, target hours, milestones and resources across any subject.</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <AppIcon name="plus" :size="16" />
        New Learning Track
      </button>
    </div>

    <!-- Topics Grid -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <span style="margin-left: 0.75rem; color: var(--text-secondary);">Loading learning tracks...</span>
    </div>

    <div v-else-if="topics.length === 0" class="card empty-state">
      <div class="empty-icon"><AppIcon name="book-open" :size="28" /></div>
      <div class="empty-title">No learning tracks found</div>
      <p class="empty-desc">Create your first custom learning track to organize courses, books, target hours and study milestones.</p>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <AppIcon name="plus" :size="14" />
        Add Track
      </button>
    </div>

    <div v-else class="topics-grid">
      <div
        v-for="topic in topics"
        :key="topic.id"
        class="card topic-card"
        :style="{ borderTopColor: topic.color || 'var(--primary)' }"
      >
        <div class="topic-card-top">
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <h3 class="topic-title">{{ topic.title }}</h3>
              <span class="badge" :class="topic.status === 'active' ? 'badge-primary' : 'badge-neutral'">
                {{ topic.status }}
              </span>
            </div>
            <span v-if="topic.category_details" class="topic-cat">
              {{ topic.category_details.name }}
            </span>
          </div>

          <div style="display: flex; gap: 0.35rem;">
            <button class="icon-btn" style="width: 30px; height: 30px;" @click="openEditModal(topic)">
              <AppIcon name="edit" :size="13" />
            </button>
            <button class="icon-btn" style="width: 30px; height: 30px; color: var(--error);" @click="deleteTopic(topic)">
              <AppIcon name="trash" :size="13" />
            </button>
          </div>
        </div>

        <p v-if="topic.description" class="topic-description">
          {{ topic.description }}
        </p>

        <!-- Progress Stats -->
        <div class="topic-progress-box">
          <div class="progress-labels">
            <span><strong>{{ topic.logged_hours }}h</strong> completed</span>
            <span>Target: <strong>{{ topic.target_hours }}h</strong></span>
          </div>
          <div class="progress-track" style="height: 8px; margin-top: 0.35rem;">
            <div
              class="progress-fill"
              :style="{ width: `${topic.progress_percentage}%`, backgroundColor: topic.color || 'var(--primary)' }"
            ></div>
          </div>
          <div style="text-align: right; font-size: 0.72rem; color: var(--text-muted); margin-top: 0.25rem;">
            {{ topic.progress_percentage }}% of goal reached
          </div>
        </div>

        <!-- Milestones Section -->
        <div class="topic-section">
          <div class="section-title-row">
            <span class="sub-heading">Milestones ({{ topic.milestones.length }})</span>
            <button class="btn btn-ghost btn-sm" style="padding: 2px 6px; font-size: 0.72rem;" @click="openAddMilestone(topic)">
              + Add
            </button>
          </div>
          <div v-if="topic.milestones.length === 0" class="sub-empty">No milestones set</div>
          <div v-else class="sub-items-list">
            <div
              v-for="ms in topic.milestones"
              :key="ms.id"
              class="sub-item-row"
              :class="{ done: ms.is_completed }"
            >
              <button class="sub-check-btn" :class="{ active: ms.is_completed }" @click="toggleMilestone(ms)">
                <AppIcon v-if="ms.is_completed" name="check" :size="11" />
              </button>
              <span class="sub-item-title">{{ ms.title }}</span>
              <span v-if="ms.target_date" class="sub-item-date">{{ ms.target_date }}</span>
            </div>
          </div>
        </div>

        <!-- Resources Section -->
        <div class="topic-section">
          <div class="section-title-row">
            <span class="sub-heading">Resources ({{ topic.resources.length }})</span>
            <button class="btn btn-ghost btn-sm" style="padding: 2px 6px; font-size: 0.72rem;" @click="openAddResource(topic)">
              + Add
            </button>
          </div>
          <div v-if="topic.resources.length === 0" class="sub-empty">No resources listed</div>
          <div v-else class="sub-items-list">
            <div
              v-for="res in topic.resources"
              :key="res.id"
              class="sub-item-row"
              :class="{ done: res.is_completed }"
            >
              <button class="sub-check-btn" :class="{ active: res.is_completed }" @click="toggleResource(res)">
                <AppIcon v-if="res.is_completed" name="check" :size="11" />
              </button>
              <span class="sub-item-title">{{ res.title }}</span>
              <span class="badge badge-neutral" style="font-size: 0.65rem;">{{ res.type }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT TOPIC MODAL -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditing ? 'Edit Track' : 'Create Learning Track' }}</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="saveTopic" class="modal-body">
          <div class="form-group">
            <label class="form-label">Subject / Learning Track Title *</label>
            <input
              v-model="form.title"
              type="text"
              required
              class="form-input"
              placeholder="e.g. Distributed Architecture, Spanish Fluency, Piano Jazz"
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
              <label class="form-label">Target Hours</label>
              <input v-model.number="form.target_hours" type="number" min="1" step="0.5" class="form-input" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Status</label>
              <select v-model="form.status" class="form-select">
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Track Accent Color</label>
              <input v-model="form.color" type="color" class="form-input" style="height: 38px; padding: 2px;" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Description & Syllabus</label>
            <textarea
              v-model="form.description"
              class="form-textarea"
              placeholder="Track overview, focus areas and study notes..."
            ></textarea>
          </div>

          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ADD MILESTONE MODAL -->
    <div v-if="showMilestoneModal" class="modal-backdrop" @click.self="showMilestoneModal = false">
      <div class="modal-card" style="max-width: 440px;">
        <div class="modal-header">
          <h3 class="modal-title">Add Milestone</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showMilestoneModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="submitMilestone" class="modal-body">
          <div class="form-group">
            <label class="form-label">Milestone Title</label>
            <input v-model="milestoneForm.title" type="text" required class="form-input" placeholder="e.g. Pass exam, build prototype" />
          </div>
          <div class="form-group">
            <label class="form-label">Target Completion Date</label>
            <input v-model="milestoneForm.target_date" type="date" class="form-input" />
          </div>
          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showMilestoneModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Add Milestone</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ADD RESOURCE MODAL -->
    <div v-if="showResourceModal" class="modal-backdrop" @click.self="showResourceModal = false">
      <div class="modal-card" style="max-width: 440px;">
        <div class="modal-header">
          <h3 class="modal-title">Add Learning Resource</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showResourceModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="submitResource" class="modal-body">
          <div class="form-group">
            <label class="form-label">Resource Title</label>
            <input v-model="resourceForm.title" type="text" required class="form-input" placeholder="e.g. Official Docs, Course Name" />
          </div>
          <div class="form-group">
            <label class="form-label">Resource Type</label>
            <select v-model="resourceForm.type" class="form-select">
              <option value="course">Course</option>
              <option value="book">Book</option>
              <option value="video">Video</option>
              <option value="article">Article</option>
              <option value="practice">Practice / Project</option>
              <option value="notes">Notes</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">URL (Optional)</label>
            <input v-model="resourceForm.url" type="url" class="form-input" placeholder="https://..." />
          </div>
          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showResourceModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Add Resource</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const api = useApi()

const topics = ref([])
const categories = ref([])
const isLoading = ref(true)

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const showMilestoneModal = ref(false)
const activeTopicForMilestone = ref(null)
const milestoneForm = ref({ title: '', target_date: null })

const showResourceModal = ref(false)
const activeTopicForResource = ref(null)
const resourceForm = ref({ title: '', type: 'course', url: '' })

const form = ref({
  title: '',
  description: '',
  category: null,
  target_hours: 50.0,
  color: '#38BDF8',
  status: 'active'
})

const fetchTopics = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/learning/topics/')
    topics.value = res || []
  } catch (e) {
    console.error('Error fetching learning topics', e)
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

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = {
    title: '',
    description: '',
    category: categories.value[0]?.id || null,
    target_hours: 50.0,
    color: '#38BDF8',
    status: 'active'
  }
  showModal.value = true
}

const openEditModal = (t) => {
  isEditing.value = true
  editingId.value = t.id
  form.value = {
    title: t.title,
    description: t.description,
    category: t.category,
    target_hours: t.target_hours,
    color: t.color || '#38BDF8',
    status: t.status
  }
  showModal.value = true
}

const saveTopic = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/learning/topics/${editingId.value}/`, form.value)
    } else {
      await api.post('/learning/topics/', form.value)
    }
    showModal.value = false
    await fetchTopics()
  } catch (e) {
    alert('Error saving learning topic: ' + e.message)
  }
}

const deleteTopic = async (t) => {
  if (confirm(`Delete learning track "${t.title}"?`)) {
    try {
      await api.delete(`/learning/topics/${t.id}/`)
      await fetchTopics()
    } catch (e) {
      alert('Error deleting topic: ' + e.message)
    }
  }
}

// Milestone actions
const openAddMilestone = (topic) => {
  activeTopicForMilestone.value = topic
  milestoneForm.value = { title: '', target_date: null }
  showMilestoneModal.value = true
}

const submitMilestone = async () => {
  try {
    await api.post(`/learning/topics/${activeTopicForMilestone.value.id}/milestones/`, milestoneForm.value)
    showMilestoneModal.value = false
    await fetchTopics()
  } catch (e) {
    alert('Error adding milestone: ' + e.message)
  }
}

const toggleMilestone = async (ms) => {
  try {
    const res = await api.post(`/learning/milestones/${ms.id}/toggle/`)
    ms.is_completed = res.is_completed
  } catch (e) {
    alert('Error toggling milestone: ' + e.message)
  }
}

// Resource actions
const openAddResource = (topic) => {
  activeTopicForResource.value = topic
  resourceForm.value = { title: '', type: 'course', url: '' }
  showResourceModal.value = true
}

const submitResource = async () => {
  try {
    await api.post(`/learning/topics/${activeTopicForResource.value.id}/resources/`, resourceForm.value)
    showResourceModal.value = false
    await fetchTopics()
  } catch (e) {
    alert('Error adding resource: ' + e.message)
  }
}

const toggleResource = async (resItem) => {
  try {
    const res = await api.post(`/learning/resources/${resItem.id}/toggle/`)
    resItem.is_completed = res.is_completed
  } catch (e) {
    alert('Error toggling resource: ' + e.message)
  }
}

onMounted(async () => {
  await fetchCategories()
  await fetchTopics()
})
</script>

<style scoped>
.learning-page {
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

.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
}

.topic-card {
  border-top: 4px solid var(--primary);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.topic-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.topic-title {
  font-size: 1.05rem;
  font-weight: 700;
}

.topic-cat {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.topic-description {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.topic-progress-box {
  background-color: var(--bg-elevated);
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.topic-section {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sub-heading {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.sub-empty {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
  padding: 0.25rem 0;
}

.sub-items-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.sub-item-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  padding: 0.35rem 0.5rem;
  background-color: var(--bg-elevated);
  border-radius: var(--radius-sm);
}

.sub-item-row.done .sub-item-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.sub-check-btn {
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

.sub-check-btn.active {
  background-color: var(--primary);
  border-color: var(--primary);
}

.sub-item-title {
  flex: 1;
}

.sub-item-date {
  font-size: 0.7rem;
  color: var(--text-muted);
}
</style>

