<template>
  <div id="app-container">
    <AppNavbar />
    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <Transition :name="route.meta.transition || 'page-fade'" mode="out-in">
          <component :is="Component" :key="route.path" />
        </Transition>
      </router-view>
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavbar from './components/AppNavbar.vue'
import AppFooter from './components/AppFooter.vue'
</script>

<style>
/* ══════════ 根布局 ══════════ */
#app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  overflow-x: hidden;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--container-xl);
  margin: 0 auto;
  padding: 80px 20px 48px; /* 80px top 为固定导航栏留空间 */
}

@media (max-width: 768px) {
  .main-content {
    padding: 72px 14px 32px;
  }
}

/* ══════════ 页面过渡动画 ══════════ */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(18px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* 滑动过渡（用于认证页） */
.page-slide-enter-active,
.page-slide-leave-active {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateX(24px);
}

.page-slide-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}
</style>
