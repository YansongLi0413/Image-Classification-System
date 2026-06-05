<template>
  <div id="app-container">
    <AppNavbar />
    <main class="main-content">
      <router-view />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavbar from './components/AppNavbar.vue'
import AppFooter from './components/AppFooter.vue'
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
#app-container { min-height: 100vh; display: flex; flex-direction: column; }
.main-content { flex: 1; max-width: 1200px; width: 100%; margin: 0 auto; padding: 20px 16px 40px; }

@media (max-width: 768px) {
  .main-content { padding: 12px 8px 30px; }
}
</style>
