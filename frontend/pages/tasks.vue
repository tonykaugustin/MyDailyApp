<template>
  <div class="tasks-page">
    <!-- Header -->
    <div class="page-top-bar">
      <div>
        <h2 class="view-title">Tasks Management</h2>
        <p class="view-sub">Organize your action items, subtasks, priorities and deadlines.</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <AppIcon name="plus" :size="16" />
        New Task
      </button>
    </div>

    <!-- Filter & Search Controls -->
    <div class="card filter-bar-card">
      <div class="filter-row">
        <!-- Status Tabs -->
        <div class="tabs-nav">
          <button
            class="tab-btn"
            :class="{ active: statusFilter === '' }"
            @click="statusFilter = ''"
          >
            All Tasks
          </button>
          <button
            class="tab-btn"
            :class="{ active: statusFilter === 'todo' }"
            @click="statusFilter = 'todo'"
          >
            To Do
          </button>
          <button
            class="tab-btn"
            :class="{ active: statusFilter === 'in_progress' }"
            @click="statusFilter = 'in_progress'"
          >
            In Progress
          </button>
          <button
            class="tab-btn"
            :class="{ active: statusFilter === 'completed' }"
            @click="statusFilter = 'completed'"
          >
            Completed
          </button>
        </div>

        <div class="filter-dropdowns">
          <!-- Priority Filter -->
          <select v-model="priorityFilter" class="form-select" style="width: auto;">
            <option value="">All Priorities</option>
            <option value="urgent">Urgent</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <!-- Category Filter -->
          <select v-model="categoryFilter" class="form-select" style="width: auto;">
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <span style="margin-left: 0.75rem; color: var(--text-secondary);">Loading tasks...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredTasks.length === 0" class="card empty-state">
      <div class="empty-icon"><AppIcon name="check-square" :size="28" /></div>
      <div class="empty-title">No tasks found</div>
      <p class="empty-desc">There are no tasks matching your current filters. Add a new task to get started.</p>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <AppIcon name="plus" :size="14" />
        Create Task
      </button>
    </div>

    <!-- Tasks List -->
    <div v-else class="tasks-list">
      <div
        v-for="task in filteredTasks"
        :key="task.id"
        class="card task-item-card"
        :class="{ completed: task.status === 'completed' }"
      >
        <div class="task-main-row">
          <button
            class="task-toggle-btn"
            :class="{ checked: task.status === 'completed' }"
            @click="toggleTaskComplete(task)"
          >
            <AppIcon v-if="task.status === 'completed'" name="check" :size="15" />
          </button>

          <div class="task-details">
            <div class="task-title-line">
              <span class="task-heading" :class="{ strike: task.status === 'completed' }">
                {{ task.title }}
              </span>
              <span :class="`badge priority-${task.priority}`" style="font-size: 0.68rem; text-transform: uppercase;">
                {{ task.priority }}
              </span>
            </div>

            <div class="task-badges-row">
              <span
                v-if="task.category_details"
                class="badge"
                :style="{ backgroundColor: `${task.category_details.color}22`, color: task.category_details.color }"
              >
                {{ task.category_details.name }}
              </span>
              <span v-if="task.due_date" style="font-size: 0.75rem; color: var(--text-secondary); display: flex; align-items: center; gap: 3px;">
                <AppIcon name="calendar" :size="12" />
                Due {{ task.due_date }}
              </span>
              <span v-if="task.estimated_minutes" style="font-size: 0.75rem; color: var(--text-muted); display: flex; align-items: center; gap: 3px;">
                <AppIcon name="clock" :size="12" />
                {{ task.estimated_minutes }}m est
              </span>
              <button
                v-if="task.subtasks && task.subtasks.length > 0"
                class="subtask-expand-pill"
                @click="expandedTaskId = expandedTaskId === task.id ? null : task.id"
              >
                <span>{{ task.completed_subtasks_count }}/{{ task.subtasks_count }} subtasks</span>
                <AppIcon :name="expandedTaskId === task.id ? 'chevron-down' : 'chevron-right'" :size="12" />
              </button>
            </div>

            <p v-if="task.description" style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.4rem;">
              {{ task.description }}
            </p>
          </div>

          <div class="task-actions">
            <button class="icon-btn" style="width: 32px; height: 32px;" title="Edit Task" @click="openEditModal(task)">
              <AppIcon name="edit" :size="14" />
            </button>
            <button class="icon-btn" style="width: 32px; height: 32px; color: var(--error);" title="Delete Task" @click="deleteTask(task)">
              <AppIcon name="trash" :size="14" />
            </button>
          </div>
        </div>

        <!-- Subtasks Expanded Checklist -->
        <div v-if="expandedTaskId === task.id" class="subtasks-expanded-container">
          <div class="subtasks-list">
            <div
              v-for="sub in task.subtasks"
              :key="sub.id"
              class="subtask-row"
              :class="{ done: sub.is_completed }"
            >
              <button
                class="subtask-check"
                :class="{ active: sub.is_completed }"
                @click="toggleSubtask(sub)"
              >
                <AppIcon v-if="sub.is_completed" name="check" :size="12" />
              </button>
              <span class="subtask-text">{{ sub.title }}</span>
            </div>
          </div>

          <!-- Add Inline Subtask -->
          <div class="add-subtask-box">
            <input
              v-model="newSubtaskTitle"
              type="text"
              placeholder="Add new subtask item..."
              class="form-input"
              style="padding: 0.4rem 0.75rem; font-size: 0.82rem;"
              @keyup.enter="addSubtask(task)"
            />
            <button class="btn btn-primary btn-sm" @click="addSubtask(task)">Add</button>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT MODAL -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditing ? 'Edit Task' : 'Create Task' }}</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="saveTask" class="modal-body">
          <div class="form-group">
            <label class="form-label">Task Title *</label>
            <input
              v-model="form.title"
              type="text"
              required
              class="form-input"
              placeholder="e.g. Write architecture overview, complete reading chapter"
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
              <label class="form-label">Priority</label>
              <select v-model="form.priority" class="form-select">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Status</label>
              <select v-model="form.status" class="form-select">
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Due Date</label>
              <input v-model="form.due_date" type="date" class="form-input" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Due Time</label>
              <input v-model="form.due_time" type="time" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Estimated Minutes</label>
              <input v-model.number="form.estimated_minutes" type="number" min="0" class="form-input" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea
              v-model="form.description"
              class="form-textarea"
              placeholder="Task instructions, links, or criteria..."
            ></textarea>
          </div>

          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Task') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const api = useApi()

const tasks = ref([])
const categories = ref([])
const isLoading = ref(true)
const statusFilter = ref('')
const priorityFilter = ref('')
const categoryFilter = ref('')
const expandedTaskId = ref(null)
const newSubtaskTitle = ref('')

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const isSaving = ref(false)

const form = ref({
  title: '',
  description: '',
  category: null,
  priority: 'medium',
  status: 'todo',
  due_date: null,
  due_time: null,
  estimated_minutes: 30
})

const fetchTasks = async () => {
  isLoading.value = true
  try {
    let url = '/tasks/'
    const params = []
    if (statusFilter.value) params.push(`status=${statusFilter.value}`)
    if (priorityFilter.value) params.push(`priority=${priorityFilter.value}`)
    if (categoryFilter.value) params.push(`category=${categoryFilter.value}`)
    if (params.length) url += `?${params.join('&')}`

    const res = await api.get(url)
    tasks.value = res || []
  } catch (e) {
    console.error('Error fetching tasks', e)
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

const filteredTasks = computed(() => tasks.value)

const toggleTaskComplete = async (task) => {
  try {
    const res = await api.post(`/tasks/${task.id}/toggle-complete/`)
    task.status = res.status
  } catch (e) {
    alert('Error toggling task: ' + e.message)
  }
}

const toggleSubtask = async (sub) => {
  try {
    const res = await api.post(`/tasks/subtasks/${sub.id}/toggle/`)
    sub.is_completed = res.is_completed
    await fetchTasks()
  } catch (e) {
    alert('Error toggling subtask: ' + e.message)
  }
}

const addSubtask = async (task) => {
  if (!newSubtaskTitle.value.trim()) return
  try {
    await api.post(`/tasks/${task.id}/subtasks/`, { title: newSubtaskTitle.value.trim() })
    newSubtaskTitle.value = ''
    await fetchTasks()
  } catch (e) {
    alert('Error adding subtask: ' + e.message)
  }
}

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = {
    title: '',
    description: '',
    category: categories.value[0]?.id || null,
    priority: 'medium',
    status: 'todo',
    due_date: new Date().toISOString().split('T')[0],
    due_time: null,
    estimated_minutes: 30
  }
  showModal.value = true
}

const openEditModal = (task) => {
  isEditing.value = true
  editingId.value = task.id
  form.value = {
    title: task.title,
    description: task.description,
    category: task.category,
    priority: task.priority,
    status: task.status,
    due_date: task.due_date,
    due_time: task.due_time,
    estimated_minutes: task.estimated_minutes
  }
  showModal.value = true
}

const saveTask = async () => {
  isSaving.value = true
  try {
    if (isEditing.value) {
      await api.put(`/tasks/${editingId.value}/`, form.value)
    } else {
      await api.post('/tasks/', form.value)
    }
    showModal.value = false
    await fetchTasks()
  } catch (e) {
    alert('Error saving task: ' + e.message)
  } finally {
    isSaving.value = false
  }
}

const deleteTask = async (task) => {
  if (confirm(`Delete task "${task.title}"?`)) {
    try {
      await api.delete(`/tasks/${task.id}/`)
      await fetchTasks()
    } catch (e) {
      alert('Error deleting task: ' + e.message)
    }
  }
}

watch([statusFilter, priorityFilter, categoryFilter], () => {
  fetchTasks()
})

onMounted(async () => {
  await fetchCategories()
  await fetchTasks()
})
</script>

<style scoped>
.tasks-page {
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

.filter-bar-card {
  padding: 0.85rem 1.15rem;
}

.filter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-dropdowns {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.task-item-card {
  padding: 1rem 1.25rem;
  transition: all var(--transition-fast);
}

.task-item-card.completed {
  opacity: 0.6;
}

.task-main-row {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.task-toggle-btn {
  width: 22px;
  height: 22px;
  border-radius: var(--radius-sm);
  border: 2px solid var(--border-light);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  margin-top: 2px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.task-toggle-btn.checked {
  background-color: var(--success);
  border-color: var(--success);
}

.task-details {
  flex: 1;
}

.task-title-line {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.task-heading {
  font-size: 0.98rem;
  font-weight: 700;
  color: var(--text-primary);
}

.task-heading.strike {
  text-decoration: line-through;
}

.task-badges-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.35rem;
  flex-wrap: wrap;
}

.subtask-expand-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg-elevated);
  padding: 2px 7px;
  border-radius: var(--radius-full);
  cursor: pointer;
}

.subtask-expand-pill:hover {
  color: var(--text-primary);
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.subtasks-expanded-container {
  margin-top: 1rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-left: 2.25rem;
}

.subtasks-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.subtask-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.85rem;
  background-color: var(--bg-elevated);
  padding: 0.35rem 0.6rem;
  border-radius: var(--radius-sm);
}

.subtask-row.done .subtask-text {
  text-decoration: line-through;
  color: var(--text-muted);
}

.subtask-check {
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

.subtask-check.active {
  background-color: var(--primary);
  border-color: var(--primary);
}

.add-subtask-box {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.4rem;
}
</style>

