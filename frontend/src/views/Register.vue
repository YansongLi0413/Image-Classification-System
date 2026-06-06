<template>
  <div class="auth">
    <!-- 左侧品牌展示区 -->
    <div class="auth__brand">
      <div class="auth__brand-bg">
        <div class="brand-glow"></div>
        <div class="brand-grid"></div>
      </div>
      <div class="auth__brand-content">
        <router-link to="/" class="brand-logo">
          <svg width="36" height="36" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="8" fill="#fff" opacity="0.2"/>
            <path d="M7 20V8l7 7 7-7v12" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>墨瞳 AI_APP</span>
        </router-link>
        <h1>加入我们</h1>
        <p>创建您的账户，开启 AI 图像识别之旅</p>
        <div class="brand-features">
          <div class="brand-feature">
            <svg width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M6 10l3 3 5-5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>永久免费使用</span>
          </div>
          <div class="brand-feature">
            <svg width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M6 10l3 3 5-5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>独立数据存储</span>
          </div>
          <div class="brand-feature">
            <svg width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M6 10l3 3 5-5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>预测历史追踪</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="auth__form-side">
      <div class="auth__form-inner">
        <div class="form-header">
          <h2>注册</h2>
          <p>已有账号？<router-link to="/login">立即登录</router-link></p>
        </div>

        <form class="auth-form" @submit.prevent="doRegister">
          <div class="form-field">
            <label>用户名</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="6" r="4" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M3 16c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>
              <input v-model="form.username" type="text" placeholder="至少3位字符" required />
            </div>
          </div>

          <div class="form-field">
            <label>邮箱</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 18 18"><rect x="2" y="4" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M2 5l7 5 7-5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>
              <input v-model="form.email" type="email" placeholder="example@email.com" required />
            </div>
          </div>

          <div class="form-field">
            <label>密码</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 18 18"><rect x="3" y="7" width="12" height="9" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M6 7V5a3 3 0 016 0v2" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="至少6位密码" required />
              <button type="button" class="pwd-toggle" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" width="18" height="18" viewBox="0 0 18 18"><path d="M2 9s3-5.5 7-5.5S16 9 16 9s-3 5.5-7 5.5S2 9 2 9z" stroke="currentColor" stroke-width="1.3" fill="none"/><circle cx="9" cy="9" r="2.5" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>
                <svg v-else width="18" height="18" viewBox="0 0 18 18"><path d="M7 7l4 4M11 7l-4 4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><path d="M2 9s3-5.5 7-5.5S16 9 16 9s-3 5.5-7 5.5S2 9 2 9z" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>
              </button>
            </div>
          </div>

          <div class="form-field">
            <label>确认密码</label>
            <div class="input-wrapper">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 18 18"><rect x="3" y="7" width="12" height="9" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M6 7V5a3 3 0 016 0v2" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>
              <input v-model="form.password2" type="password" placeholder="再次输入密码" required />
            </div>
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>注册</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const showPwd = ref(false)
const form = ref({ username: '', email: '', password: '', password2: '' })

async function doRegister() {
  if (form.value.password !== form.value.password2) {
    return ElMessage.error('两次密码不一致')
  }
  if (form.value.password.length < 6) {
    return ElMessage.warning('密码至少6位')
  }
  loading.value = true
  try {
    await auth.register(form.value.username, form.value.email, form.value.password)
    ElMessage.success('注册成功')
    router.push('/predict')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '注册失败')
  } finally { loading.value = false }
}
</script>

<style scoped>
/* 复用 Login 的布局样式 */
.auth {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: calc(100vh - 64px - 80px);
  margin: -24px -20px;
  overflow: hidden;
}
.auth__brand {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(165deg, var(--ink-900), var(--ink-700), var(--ink-800));
  overflow: hidden;
}
.auth__brand-bg {
  position: absolute;
  inset: 0;
}
.brand-glow {
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(201, 169, 110, 0.15), transparent);
  top: -100px;
  right: -100px;
  border-radius: 50%;
}
.brand-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.5;
}
.auth__brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: var(--space-10);
  max-width: 420px;
}
.brand-logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  margin-bottom: var(--space-10);
}
.brand-logo span {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.06em;
}
.auth__brand-content h1 {
  font-size: var(--text-3xl);
  color: #fff;
  margin-bottom: var(--space-3);
}
.auth__brand-content > p {
  font-size: var(--text-base);
  color: var(--warm-300);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-10);
}
.brand-features {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  text-align: left;
}
.brand-feature {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--warm-200);
  font-size: var(--text-sm);
}
.brand-feature svg { flex-shrink: 0; color: var(--gold-400); }

.auth__form-side {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  padding: var(--space-8);
}
.auth__form-inner {
  width: 100%;
  max-width: 400px;
}
.form-header {
  text-align: center;
  margin-bottom: var(--space-8);
}
.form-header h2 {
  font-size: var(--text-3xl);
  margin-bottom: var(--space-2);
}
.form-header p {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}
.form-header a {
  color: var(--ink-600);
  font-weight: 600;
  text-decoration: none;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-field label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
}
.input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0 var(--space-4);
  transition: all var(--duration-fast) var(--ease-out-quart);
}
.input-wrapper:focus-within {
  border-color: var(--ink-500);
  box-shadow: 0 0 0 3px rgba(26, 39, 68, 0.06);
}
.input-icon {
  color: var(--color-text-muted);
  flex-shrink: 0;
}
.input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 12px 0;
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--color-text);
}
.input-wrapper input::placeholder {
  color: var(--warm-400);
}
.pwd-toggle {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-muted);
  padding: 4px;
  display: flex;
}

.submit-btn {
  margin-top: var(--space-2);
  width: 100%;
  padding: 14px;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, var(--ink-700), var(--ink-600));
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  box-shadow: var(--shadow-ink);
  transition: all var(--duration-normal) var(--ease-out-expo);
  display: flex;
  align-items: center;
  justify-content: center;
}
.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-xl);
}
.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .auth {
    grid-template-columns: 1fr;
    margin: -12px -10px;
  }
  .auth__brand { display: none; }
  .auth__form-side { padding: var(--space-6) var(--space-4); }
  .form-header h2 { font-size: var(--text-2xl); }
}
</style>
