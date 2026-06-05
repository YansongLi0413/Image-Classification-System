<template>
  <el-menu :default-active="currentRoute" mode="horizontal" :ellipsis="false"
           class="navbar" @select="handleSelect">
    <div class="nav-brand">
      <el-icon :size="28"><PictureFilled /></el-icon>
      <span class="brand-text">AI_APP</span>
    </div>
    <div class="nav-spacer" />
    <el-menu-item index="/">首页</el-menu-item>
    <el-menu-item index="/predict" v-if="auth.isLoggedIn">图片预测</el-menu-item>
    <el-menu-item index="/history" v-if="auth.isLoggedIn">历史记录</el-menu-item>
    <el-sub-menu index="user" v-if="auth.isLoggedIn" class="user-menu">
      <template #title>
        <el-icon><User /></el-icon>
        <span>{{ auth.user?.username || '用户' }}</span>
      </template>
      <el-menu-item index="/profile">个人中心</el-menu-item>
      <el-menu-item index="logout" @click="auth.logout(); $router.push('/')">退出登录</el-menu-item>
    </el-sub-menu>
    <el-menu-item index="/login" v-if="!auth.isLoggedIn">登录</el-menu-item>
    <el-button type="primary" size="small" v-if="!auth.isLoggedIn"
               style="margin-left:8px" @click="$router.push('/register')">注册</el-button>
    <!-- 移动端菜单 -->
    <el-popover placement="bottom-end" :width="200" trigger="click" v-if="isMobile">
      <template #reference>
        <el-button class="mobile-toggle" :icon="Menu" circle />
      </template>
      <div class="mobile-menu">
        <el-link href="/" :underline="false">首页</el-link>
        <el-link href="/predict" :underline="false">图片预测</el-link>
        <el-link href="/history" :underline="false">历史记录</el-link>
        <el-link href="/profile" :underline="false">个人中心</el-link>
      </div>
    </el-popover>
  </el-menu>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { PictureFilled, User, Menu } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const currentRoute = computed(() => route.path)
const isMobile = ref(false)

function handleSelect(index) {
  if (index === 'logout') return auth.logout()
  if (index && index !== 'user') router.push(index)
}

function checkMobile() { isMobile.value = window.innerWidth < 768 }
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => window.removeEventListener('resize', checkMobile))
</script>

<style scoped>
.navbar { display: flex; align-items: center; padding: 0 20px; height: 60px; border-bottom: 1px solid #e6e6e6; }
.nav-brand { display: flex; align-items: center; gap: 8px; color: #409eff; margin-right: 20px; }
.brand-text { font-size: 20px; font-weight: 700; }
.nav-spacer { flex: 1; }
.user-menu { margin-left: auto; }
.mobile-toggle { display: none; }
.mobile-menu { display: flex; flex-direction: column; gap: 12px; padding: 8px; }
.mobile-menu a { font-size: 16px; padding: 8px; }

@media (max-width: 768px) {
  .navbar { padding: 0 12px; }
  .nav-brand .brand-text { font-size: 16px; }
  .el-menu-item, .user-menu { display: none !important; }
  .mobile-toggle { display: inline-flex; }
}
</style>
