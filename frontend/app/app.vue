<script setup>
import { ref } from "vue";

const sidebarOpen = ref(false);
</script>

<template>
  <div class="app-layout">
    <AppSidebar
      :is-open="sidebarOpen"
      @close="sidebarOpen = false"
    />

    <div
      v-if="sidebarOpen"
      class="sidebar-overlay"
      @click="sidebarOpen = false"
    ></div>

    <main class="main-content">
      <AppHeader @menu-click="sidebarOpen = !sidebarOpen" />

      <div class="page-content">
        <NuxtPage />
      </div>
    </main>
  </div>
</template>