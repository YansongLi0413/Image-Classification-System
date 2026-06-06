<template>
  <header class="navbar" :class="{ 'navbar--scrolled': scrolled }">
    <div class="navbar__inner">
      <!-- 品牌区域 -->
      <router-link to="/" class="navbar__brand">
        <div class="brand-icon">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="8" fill="url(#brandGrad)"/>
            <path d="M7 20V8l7 7 7-7v12" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="brandGrad" x1="0" y1="0" x2="28" y2="28">
                <stop stop-color="#2a4a8a"/><stop offset="1" stop-color="#1a2744"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">墨瞳</span>
          <span class="brand-sub">AI_APP</span>
        </div>
      </router-link>

      <!-- 桌面端导航 -->
      <nav class="navbar__links hide-mobile">
        <router-link to="/" class="nav-link" active-class="nav-link--active">首页</router-link>
        <template v-if="auth.isLoggedIn">
          <router-link to="/predict" class="nav-link" active-class="nav-link--active">图片预测</router-link>
          <router-link to="/history" class="nav-link" active-class="nav-link--active">历史记录</router-link>
        </template>
      </nav>

      <!-- 桌面端用户区 -->
      <div class="navbar__actions hide-mobile">
        <template v-if="auth.isLoggedIn">
          <el-dropdown trigger="click" popper-class="user-dropdown">
            <button class="user-btn">
              <span class="user-avatar-circle">{{ auth.user?.username?.charAt(0)?.toUpperCase() }}</span>
              <span class="user-name">{{ auth.user?.username }}</span>
              <svg class="chevron" width="12" height="12" viewBox="0 0 12 12"><path d="M3 5l3 3 3-3" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <router-link to="/profile" class="dropdown-link">个人中心</router-link>
                </el-dropdown-item>
                <el-dropdown-item divided>
                  <span class="dropdown-link logout-link" @click="handleLogout">退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="btn-text">登录</router-link>
          <router-link to="/register" class="btn-primary-sm">注册</router-link>
        </template>
      </div>

      <!-- 移动端汉堡按钮 -->
      <button class="mobile-toggle show-mobile" @click="mobileOpen = !mobileOpen" :aria-label="mobileOpen ? '关闭菜单' : '打开菜单'">
        <span class="hamburger" :class="{ 'hamburger--open': mobileOpen }">
          <i></i><i></i><i></i>
        </span>
      </button>
    </div>

    <!-- 移动端全屏抽屉 -->
    <Transition name="drawer">
      <div v-if="mobileOpen" class="mobile-drawer">
        <div class="mobile-drawer__inner">
          <nav class="mobile-nav">
            <router-link to="/" class="mobile-nav__link" @click="mobileOpen = false">首页</router-link>
            <template v-if="auth.isLoggedIn">
              <router-link to="/predict" class="mobile-nav__link" @click="mobileOpen = false">图片预测</router-link>
              <router-link to="/history" class="mobile-nav__link" @click="mobileOpen = false">历史记录</router-link>
              <router-link to="/profile" class="mobile-nav__link" @click="mobileOpen = false">个人中心</router-link>
              <span class="mobile-nav__link mobile-nav__link--logout" @click="handleLogout">退出登录</span>
            </template>
            <template v-else>
              <router-link to="/login" class="mobile-nav__link" @click="mobileOpen = false">登录</router-link>
              <router-link to="/register" class="mobile-nav__link mobile-nav__link--highlight" @click="mobileOpen = false">注册</router-link>
            </template>
          </nav>
          <div class="mobile-drawer__footer">
            <p>墨瞳 AI_APP — 图像分类智能应用</p>
          </div>
        </div>
      </div>
    </Transition>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const scrolled = ref(false)
const mobileOpen = ref(false)

function handleLogout() {
  auth.logout()
  mobileOpen.value = false
  router.push('/')
}

function onScroll() { scrolled.value = window.scrollY > 20 }
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
/* ══════════ 导航栏容器 ══════════ */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 64px;
  background: rgba(250, 248, 245, 0.82);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border-bottom: 1px solid transparent;
  transition: all 0.35s var(--ease-out-expo);
}
.navbar--scrolled {
  background: rgba(255, 255, 255, 0.88);
  border-bottom-color: var(--color-border-light);
  box-shadow: 0 2px 20px rgba(13, 21, 38, 0.06);
}

.navbar__inner {
  max-width: var(--container-xl);
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 var(--space-6);
  gap: var(--space-6);
}

/* ══════════ 品牌标志 ══════════ */
.navbar__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}
.brand-icon svg { display: block; }
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}
.brand-name {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--ink-800);
  letter-spacing: 0.08em;
}
.brand-sub {
  font-size: 0.6rem;
  color: var(--gold-400);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-weight: 500;
}

/* ══════════ 桌面端导航链接 ══════════ */
.navbar__links {
  display: flex;
  gap: 4px;
  margin-left: var(--space-8);
}
.nav-link {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-out-quart);
  position: relative;
}
.nav-link:hover {
  color: var(--color-text);
  background: var(--warm-100);
}
.nav-link--active {
  color: var(--ink-700);
  background: var(--ink-50);
}

.navbar__actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* ══════════ 用户按钮 ══════════ */
.user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-text);
  transition: all var(--duration-fast) var(--ease-out-quart);
}
.user-btn:hover {
  border-color: var(--ink-300);
  box-shadow: var(--shadow-sm);
}
.user-avatar-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--ink-600), var(--ink-400));
  color: #fff;
  font-weight: 600;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.user-name {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chevron { color: var(--color-text-muted); }

/* ══════════ 按钮 ══════════ */
.btn-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  padding: 8px 16px;
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: color var(--duration-fast);
}
.btn-text:hover { color: var(--color-text); }

.btn-primary-sm {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, var(--ink-700), var(--ink-600));
  padding: 10px 20px;
  border-radius: var(--radius-md);
  text-decoration: none;
  box-shadow: var(--shadow-ink);
  transition: all var(--duration-normal) var(--ease-out-expo);
}
.btn-primary-sm:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-xl);
}

/* ══════════ 下拉菜单全局样式 ══════════ */
.dropdown-link {
  display: block;
  width: 100%;
  color: var(--color-text);
  text-decoration: none;
  font-size: var(--text-sm);
  cursor: pointer;
}
.logout-link {
  color: var(--danger);
}

/* ══════════ 移动端汉堡按钮 ══════════ */
.mobile-toggle {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  z-index: 1010;
}
.hamburger {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 22px;
}
.hamburger i {
  display: block;
  height: 2px;
  background: var(--ink-700);
  border-radius: 2px;
  transition: all 0.3s var(--ease-out-expo);
  transform-origin: center;
}
.hamburger i:nth-child(1) { width: 22px; }
.hamburger i:nth-child(2) { width: 16px; }
.hamburger i:nth-child(3) { width: 20px; }
.hamburger--open i:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
  width: 22px;
}
.hamburger--open i:nth-child(2) {
  opacity: 0;
  transform: scaleX(0);
}
.hamburger--open i:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
  width: 22px;
}

/* ══════════ 移动端全屏抽屉 ══════════ */
.mobile-drawer {
  position: fixed;
  inset: 0;
  background: var(--color-bg);
  z-index: 1005;
  display: flex;
  align-items: center;
  justify-content: center;
}
.mobile-drawer__inner {
  text-align: center;
  padding: var(--space-8);
}
.mobile-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mobile-nav__link {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--ink-800);
  text-decoration: none;
  padding: 12px 24px;
  border-radius: var(--radius-lg);
  transition: all var(--duration-fast) var(--ease-out-quart);
  cursor: pointer;
  display: block;
}
.mobile-nav__link:hover {
  background: var(--warm-100);
}
.mobile-nav__link--highlight {
  background: var(--ink-700);
  color: #fff;
}
.mobile-nav__link--highlight:hover {
  background: var(--ink-600);
}
.mobile-nav__link--logout {
  color: var(--danger);
}
.mobile-drawer__footer {
  margin-top: var(--space-10);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* 抽屉过渡动画 */
.drawer-enter-active {
  transition: opacity 0.35s var(--ease-out-expo);
}
.drawer-enter-active .mobile-nav__link {
  animation: slideUp 0.4s var(--ease-out-expo) both;
}
.drawer-enter-active .mobile-nav__link:nth-child(1) { animation-delay: 0.05s; }
.drawer-enter-active .mobile-nav__link:nth-child(2) { animation-delay: 0.1s; }
.drawer-enter-active .mobile-nav__link:nth-child(3) { animation-delay: 0.15s; }
.drawer-enter-active .mobile-nav__link:nth-child(4) { animation-delay: 0.2s; }
.drawer-enter-active .mobile-nav__link:nth-child(5) { animation-delay: 0.25s; }
.drawer-enter-active .mobile-nav__link:nth-child(6) { animation-delay: 0.3s; }
.drawer-leave-active {
  transition: opacity 0.25s var(--ease-out-quart);
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

@media (max-width: 1023px) {
  .navbar__inner {
    padding: 0 var(--space-4);
  }
}
</style>
