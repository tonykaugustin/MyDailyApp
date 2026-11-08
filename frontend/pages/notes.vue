<template>
  <div class="notes-page">
    <div class="page-top-bar">
      <div>
        <h2 class="view-title">Personal Notes & Knowledge</h2>
        <p class="view-sub">Capture ideas, daily reflections, meeting summaries, and markdown notes.</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <AppIcon name="plus" :size="16" />
        New Note
      </button>
    </div>

    <!-- Search & Filter Bar -->
    <div class="card filter-bar-card">
      <div class="filter-row">
        <div class="search-input-box">
          <AppIcon name="search" :size="16" style="color: var(--text-muted);" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search notes by title or content..."
            class="bare-input"
          />
        </div>

        <select v-model="selectedCategory" class="form-select" style="width: auto;">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <span style="margin-left: 0.75rem; color: var(--text-secondary);">Loading notes...</span>
    </div>

    <div v-else-if="filteredNotes.length === 0" class="card empty-state">
      <div class="empty-icon"><AppIcon name="file-text" :size="28" /></div>
      <div class="empty-title">No notes found</div>
      <p class="empty-desc">Write your first note, journal entry, or knowledge piece.</p>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">Add Note</button>
    </div>

    <div v-else class="notes-masonry-grid">
      <div
        v-for="note in filteredNotes"
        :key="note.id"
        class="card note-card"
        :class="{ pinned: note.is_pinned }"
      >
        <div class="note-card-top">
          <h3 class="note-card-title">{{ note.title }}</h3>
          <div style="display: flex; gap: 0.25rem;">
            <button
              class="icon-btn"
              style="width: 28px; height: 28px;"
              :title="note.is_pinned ? 'Unpin note' : 'Pin note'"
              :style="{ color: note.is_pinned ? 'var(--warning)' : 'var(--text-muted)' }"
              @click="togglePin(note)"
            >
              ★
            </button>
            <button class="icon-btn" style="width: 28px; height: 28px;" @click="openEditModal(note)">
              <AppIcon name="edit" :size="13" />
            </button>
            <button class="icon-btn" style="width: 28px; height: 28px; color: var(--error);" @click="deleteNote(note)">
              <AppIcon name="trash" :size="13" />
            </button>
          </div>
        </div>

        <div v-if="note.category_details" style="margin-bottom: 0.4rem;">
          <span class="badge" :style="{ backgroundColor: `${note.category_details.color}22`, color: note.category_details.color }">
            {{ note.category_details.name }}
          </span>
        </div>

        <div class="note-content-preview">
          {{ note.content }}
        </div>

        <div class="note-card-footer">
          <span>Updated {{ note.updated_at ? note.updated_at.split('T')[0] : '' }}</span>
          <span v-if="note.is_pinned" class="badge badge-warning" style="font-size: 0.65rem;">Pinned</span>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT MODAL -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-card" style="max-width: 620px;">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditing ? 'Edit Note' : 'Create Note' }}</h3>
          <button class="icon-btn" style="width: 30px; height: 30px;" @click="showModal = false">
            <AppIcon name="x" :size="16" />
          </button>
        </div>
        <form @submit.prevent="saveNote" class="modal-body">
          <div class="form-group">
            <label class="form-label">Note Title *</label>
            <input v-model="form.title" type="text" required class="form-input" placeholder="Note headline or topic..." />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Category</label>
              <select v-model="form.category" class="form-select">
                <option :value="null">No Category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div class="form-group" style="justify-content: flex-end; padding-bottom: 0.5rem;">
              <label class="checkbox-label">
                <input type="checkbox" v-model="form.is_pinned" class="checkbox-input" />
                <span class="checkbox-custom">
                  <AppIcon v-if="form.is_pinned" name="check" :size="12" />
                </span>
                <span>Pin to top</span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Content (Markdown supported)</label>
            <textarea
              v-model="form.content"
              class="form-textarea"
              style="min-height: 200px; font-family: var(--font-mono); font-size: 0.88rem;"
              placeholder="Write your note, summary, or thoughts here..."
            ></textarea>
          </div>

          <div class="modal-footer" style="padding: 0; margin-top: 1rem; border-top: none;">
            <button type="button" class="btn btn-outline btn-sm" @click="showModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm">Save Note</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const api = useApi()

const notes = ref([])
const categories = ref([])
const isLoading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('')

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const form = ref({
  title: '',
  content: '',
  category: null,
  is_pinned: false
})

const fetchNotes = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/notes/')
    notes.value = res || []
  } catch (e) {
    console.error('Error fetching notes', e)
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

const filteredNotes = computed(() => {
  return notes.value.filter(n => {
    const matchesCat = !selectedCategory.value || n.category === selectedCategory.value
    const q = searchQuery.value.toLowerCase()
    const matchesQuery = !q || n.title.toLowerCase().includes(q) || n.content.toLowerCase().includes(q)
    return matchesCat && matchesQuery
  })
})

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = {
    title: '',
    content: '',
    category: categories.value[0]?.id || null,
    is_pinned: false
  }
  showModal.value = true
}

const openEditModal = (note) => {
  isEditing.value = true
  editingId.value = note.id
  form.value = {
    title: note.title,
    content: note.content,
    category: note.category,
    is_pinned: note.is_pinned
  }
  showModal.value = true
}

const saveNote = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/notes/${editingId.value}/`, form.value)
    } else {
      await api.post('/notes/', form.value)
    }
    showModal.value = false
    await fetchNotes()
  } catch (e) {
    alert('Error saving note: ' + e.message)
  }
}

const deleteNote = async (note) => {
  if (confirm(`Delete note "${note.title}"?`)) {
    try {
      await api.delete(`/notes/${note.id}/`)
      await fetchNotes()
    } catch (e) {
      alert('Error deleting note: ' + e.message)
    }
  }
}

const togglePin = async (note) => {
  try {
    const res = await api.post(`/notes/${note.id}/toggle-pin/`)
    note.is_pinned = res.is_pinned
    await fetchNotes()
  } catch (e) {
    alert('Error pinning note: ' + e.message)
  }
}

onMounted(async () => {
  await fetchCategories()
  await fetchNotes()
})
</script>

<style scoped>
.notes-page {
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

.search-input-box {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 0.45rem 0.85rem;
  flex: 1;
  max-width: 400px;
}

.bare-input {
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
  width: 100%;
}

.notes-masonry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.25rem;
}

.note-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 180px;
}

.note-card.pinned {
  border-color: var(--warning);
}

.note-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.note-card-title {
  font-size: 1.05rem;
  font-weight: 700;
}

.note-content-preview {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
  white-space: pre-wrap;
  flex: 1;
  max-height: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.note-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.72rem;
  color: var(--text-muted);
  border-top: 1px solid var(--border-color);
  padding-top: 0.65rem;
}
</style>

