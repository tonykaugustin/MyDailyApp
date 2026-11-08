<template>
  <div class="settings-page">
    <div class="page-top-bar">
      <div>
        <h2 class="view-title">Settings & Customization</h2>
        <p class="view-sub">Customize your productivity system, dynamic categories, personal preferences, and profile.</p>
      </div>
    </div>

    <div class="settings-grid">
      <!-- 1. DYNAMIC CATEGORIES MANAGER -->
      <div class="card" style="grid-column: 1 / -1;">
        <div class="card-header">
          <div>
            <h3 class="card-title">
              <AppIcon name="folder" :size="20" style="color: var(--primary);" />
              Dynamic Categories System
            </h3>
            <p class="card-subtitle">
              Manage your personal life areas, subjects and workspaces. No subjects are hardcoded; you have complete control.
            </p>
          </div>
          <button class="btn btn-primary btn-sm" @click="openCreateCategoryModal">
            <AppIcon name="plus" :size="15" />
            Add Category
          </button>
        </div>

        <div class="categories-list-grid">
          <div
            v-for="cat in categories"
            :key="cat.id"
            class="category-badge-card"
            :style="{ borderLeftColor: cat.color || 'var(--primary)' }"
          >
            <div class="cat-card-main">
              <div class="cat-color-dot" :style="{ backgroundColor: cat.color || 'var(--primary)' }"></div>
              <div>
                <h4 class="cat-name">{{ cat.name }}</h4>
                <div class="cat-stats-row">
                  <span>{{ cat.activities_count }} activities</span>
                  <span>•</span>
                  <span>{{ cat.tasks_count }} tasks</span>
                </div>
              </div>
            </div>

            <div class="cat-actions">
              <button class="icon-btn" style="width: 28px; height: 28px;" @click="openEditCategoryModal(cat)">
                <AppIcon name="edit" :size="13" />
              </button>
              <button class="icon-btn" style="width: 28px; height: 28px; color: var(--error);" @click="deleteCategory(cat)">
                <AppIcon name="trash" :size="13" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. USER PROFILE SETTINGS -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <AppIcon name="user" :size="18" style="color: var(--secondary);" />
            Profile Information
          </h3>
        </div>
        <form @submit.prevent="saveProfile" class="profile-form">
          <div class="form-group">
            <label class="form-label">Display Name</label>
            <input v-model="profileForm.display_name" type="text" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Email Address</label>
            <input v-model="profileForm.email" type="email" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Daily Study Goal (Hours)</label>
            <input v-model.number="profileForm.daily_study_goal_hours" type="number" min="0.5" step="0.5" class="form-input" />
          </div>

          <button type="submit" class="btn btn-primary btn-sm" :disabled="isSavingProfile">
            {{ isSavingProfile ? 'Saving...' : 'Save Profile Changes' }}
          </button>
        </form>
      </div>

      <!-- 3. APPEARANCE & THEME SETTINGS -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <AppIcon name="settings" :size="18" style="color: var(--warning);" />
            Appearance & Workspace
          </h3>
        </div>

        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
          <div>
            <label class="form-label">Color Theme</label>
            <div class="theme-selection-row">
              <button
                class="theme-select-card"
                :class="{ active: theme === 'minimal' || theme === 'light' }"
                @click="setTheme('minimal')"
              >
                <div class="theme-preview minimal-prev"></div>
                <span>Minimalist (Default)</span>
              </button>

              <button
                class="theme-select-card"
                :class="{ active: theme === 'dark' }"
                @click="setTheme('dark')"
              >
                <div class="theme-preview dark-prev"></div>
                <span>Dark Theme</span>
              </button>
            </div>
          </div>

          <div style="border-top: 1px solid var(--border-color); padding-top: 1rem;">
            <label class="form-label">Starter Productivity Data</label>
            <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
              Re-populate dynamic categories, sample activities, habits, tasks, and goals.
            </p>
            <button class="btn btn-outline btn-sm" @click="handleResetStarterData">
              <AppIcon name="refresh-cw" :size="14" />
              Reset Starter Data
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT CATEGORY MODAL -->
    <div v-if="showCatModal" class="modal-backdrop" @click.self="showCatModal = false">
      <div class="modal-card" style="max-width: 440px;">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditingCat ? 'Edit Category' : 'Create Custom Category' }}</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showCatModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="saveCategory" class="modal-body">
          <div class="form-group">
            <label class="form-label">Category Name *</label>
            <input
              v-model="catForm.name"
              type="text"
              required
              class="form-input"
              placeholder="e.g. Health & Fitness, Deep Work, Programming, Spanish"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Type</label>
              <select v-model="catForm.type" class="form-select">
                <option value="general">General</option>
                <option value="work">Work & Career</option>
                <option value="study">Learning & Study</option>
                <option value="health">Health & Fitness</option>
                <option value="personal">Personal & Life</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Accent Color</label>
              <input v-model="catForm.color" type="color" class="form-input" style="height: 38px; padding: 2px;" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea v-model="catForm.description" class="form-textarea" placeholder="Category purpose or scope..."></textarea>
          </div>

          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showCatModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Save Category</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const api = useApi()
const { user, fetchUser, seedStarterData } = useAuth()
const { theme, setTheme } = useTheme()

const categories = ref([])
const isSavingProfile = ref(false)

const profileForm = ref({
  display_name: '',
  email: '',
  daily_study_goal_hours: 2.0
})

const showCatModal = ref(false)
const isEditingCat = ref(false)
const editingCatId = ref(null)
const catForm = ref({
  name: '',
  description: '',
  color: '#7C6CFF',
  type: 'general'
})

const fetchCategories = async () => {
  try {
    const res = await api.get('/categories/')
    categories.value = res || []
  } catch (e) {
    console.error(e)
  }
}

const loadProfile = () => {
  if (user.value) {
    profileForm.value = {
      display_name: user.value.profile?.display_name || user.value.first_name || '',
      email: user.value.email || '',
      daily_study_goal_hours: user.value.profile?.daily_study_goal_hours || 2.0
    }
  }
}

const saveProfile = async () => {
  isSavingProfile.value = true
  try {
    await api.patch('/auth/me/', profileForm.value)
    await fetchUser()
    alert('Profile updated successfully!')
  } catch (e) {
    alert('Error updating profile: ' + e.message)
  } finally {
    isSavingProfile.value = false
  }
}

const openCreateCategoryModal = () => {
  isEditingCat.value = false
  editingCatId.value = null
  catForm.value = {
    name: '',
    description: '',
    color: '#7C6CFF',
    type: 'general'
  }
  showCatModal.value = true
}

const openEditCategoryModal = (cat) => {
  isEditingCat.value = true
  editingCatId.value = cat.id
  catForm.value = {
    name: cat.name,
    description: cat.description,
    color: cat.color || '#7C6CFF',
    type: cat.type || 'general'
  }
  showCatModal.value = true
}

const saveCategory = async () => {
  try {
    if (isEditingCat.value) {
      await api.put(`/categories/${editingCatId.value}/`, catForm.value)
    } else {
      await api.post('/categories/', catForm.value)
    }
    showCatModal.value = false
    await fetchCategories()
  } catch (e) {
    alert('Error saving category: ' + e.message)
  }
}

const deleteCategory = async (cat) => {
  if (confirm(`Delete category "${cat.name}"?`)) {
    try {
      await api.delete(`/categories/${cat.id}/`)
      await fetchCategories()
    } catch (e) {
      alert('Error deleting category: ' + e.message)
    }
  }
}

const handleResetStarterData = async () => {
  if (confirm('Reset and load starter dynamic productivity records?')) {
    await seedStarterData()
    await fetchCategories()
    alert('Starter data loaded!')
  }
}

onMounted(async () => {
  await fetchCategories()
  loadProfile()
})
</script>

<style scoped>
.settings-page {
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

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.categories-list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.category-badge-card {
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-left: 4px solid var(--primary);
  border-radius: var(--radius-md);
  padding: 0.85rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cat-card-main {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.cat-color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cat-name {
  font-size: 0.95rem;
  font-weight: 700;
}

.cat-stats-row {
  display: flex;
  gap: 0.4rem;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.cat-actions {
  display: flex;
  gap: 0.3rem;
}

.theme-selection-row {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.theme-select-card {
  flex: 1;
  padding: 0.75rem;
  background-color: var(--bg-input);
  border: 1.5px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.theme-select-card.active {
  border-color: var(--primary);
  color: var(--text-primary);
  background-color: var(--bg-card);
}

.theme-preview {
  width: 100%;
  height: 48px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-light);
}

.theme-preview.minimal-prev {
  background: #FFFFFF;
  border-color: #E2E8F0;
}

.theme-preview.dark-prev {
  background: #0B0F19;
}

@media (max-width: 1024px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>

