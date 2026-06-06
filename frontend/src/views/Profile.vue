<template>
  <div class="profile">
    <div class="section-header">
      <span class="section-label">个人中心</span>
      <h2>{{ userInfo?.username }}</h2>
      <p class="section-desc">管理您的账户信息与安全设置</p>
    </div>

    <div class="profile__grid">
      <!-- 左侧用户信息 -->
      <div class="profile-card user-card">
        <div class="user-card__avatar">
          <span>{{ (userInfo?.username || '?').charAt(0).toUpperCase() }}</span>
        </div>
        <h3>{{ userInfo?.username }}</h3>
        <p class="user-card__email">{{ userInfo?.email }}</p>
        <span class="user-card__role" :class="`role--${userInfo?.role}`">
          {{ userInfo?.role === 'admin' ? '管理员' : '普通用户' }}
        </span>
        <div class="user-card__meta">
          <div class="meta-item">
            <span class="meta-value">{{ userInfo?.predictions_count ?? 0 }}</span>
            <span class="meta-label">预测次数</span>
          </div>
          <div class="meta-item">
            <span class="meta-value">{{ userInfo?.date_joined ? new Date(userInfo.date_joined).toLocaleDateString('zh-CN') : '—' }}</span>
            <span class="meta-label">注册日期</span>
          </div>
        </div>
      </div>

      <!-- 右侧设置 -->
      <div class="profile-card settings-card">
        <div class="settings-section">
          <h4>修改密码</h4>
          <p class="settings-desc">请定期更换密码以确保账户安全</p>
          <form @submit.prevent="changePwd" class="settings-form">
            <div class="form-field">
              <label>原密码</label>
              <div class="input-wrapper">
                <input v-model="pwdForm.old_password" :type="showOld ? 'text' : 'password'" placeholder="输入原密码" required />
                <button type="button" class="pwd-toggle" @click="showOld = !showOld">
                  <svg width="16" height="16" viewBox="0 0 18 18"><path d="M2 9s3-5.5 7-5.5S16 9 16 9s-3 5.5-7 5.5S2 9 2 9z" stroke="currentColor" stroke-width="1.3" fill="none"/><circle cx="9" cy="9" r="2.5" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>
                </button>
              </div>
            </div>
            <div class="form-field">
              <label>新密码</label>
              <div class="input-wrapper">
                <input v-model="pwdForm.new_password" :type="showNew ? 'text' : 'password'" placeholder="至少6位新密码" required />
                <button type="button" class="pwd-toggle" @click="showNew = !showNew">
                  <svg width="16" height="16" viewBox="0 0 18 18"><path d="M2 9s3-5.5 7-5.5S16 9 16 9s-3 5.5-7 5.5S2 9 2 9z" stroke="currentColor" stroke-width="1.3" fill="none"/><circle cx="9" cy="9" r="2.5" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>
                </button>
              </div>
            </div>
            <button type="submit" class="save-btn" :disabled="pwdLoading">
              <span v-if="pwdLoading" class="spinner"></span>
              <span v-else>修改密码</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { authAPI } from '../api/client'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const pwdForm = ref({ old_password: '', new_password: '' })
const pwdLoading = ref(false)
const showOld = ref(false)
const showNew = ref(false)
const userInfo = ref(auth.user || {})

// 页面加载时从服务器获取最新用户信息（确保 predictions_count 等准确）
onMounted(async () => {
  try {
    const res = await authAPI.get('/auth/me/')
    userInfo.value = res.data
    // 同步更新 auth store 和 localStorage
    auth.user = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
  } catch {}
})

async function changePwd() {
  if (pwdForm.value.new_password.length < 6) {
    return ElMessage.warning('新密码至少6位')
  }
  pwdLoading.value = true
  try {
    await authAPI.post('/auth/change-password/', pwdForm.value)
    ElMessage.success('密码修改成功')
    pwdForm.value = { old_password: '', new_password: '' }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '修改失败，请检查原密码是否正确')
  } finally { pwdLoading.value = false }
}
</script>

<style scoped>
.section-header {
  text-align: center;
  margin-bottom: var(--space-10);
}
.section-label {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
  color: var(--gold-700);
  margin-bottom: var(--space-2);
}
.section-header h2 {
  font-size: var(--text-3xl);
  margin-bottom: var(--space-3);
}
.section-desc {
  font-size: var(--text-base);
  color: var(--color-text-muted);
}

.profile__grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: var(--space-8);
  max-width: 900px;
  margin: 0 auto;
}

/* ══════════ 卡片基础 ══════════ */
.profile-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
}

/* ══════════ 用户信息卡片 ══════════ */
.user-card {
  text-align: center;
  height: fit-content;
}
.user-card__avatar {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--ink-700), var(--ink-500));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-4);
  box-shadow: var(--shadow-ink);
}
.user-card__avatar span {
  font-family: var(--font-display);
  font-size: 2.25rem;
  font-weight: 700;
  color: #fff;
}
.user-card h3 {
  font-size: var(--text-xl);
  margin-bottom: 4px;
}
.user-card__email {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}
.user-card__role {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 4px 14px;
  border-radius: var(--radius-full);
  margin-bottom: var(--space-6);
}
.role--admin {
  background: var(--danger-light);
  color: var(--danger);
}
.role--user {
  background: var(--info-light);
  color: var(--info);
}

.user-card__meta {
  display: flex;
  justify-content: center;
  gap: var(--space-8);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border-light);
}
.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.meta-value {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--ink-700);
}
.meta-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* ══════════ 设置卡片 ══════════ */
.settings-section h4 {
  font-size: var(--text-lg);
  font-weight: 600;
  margin-bottom: 4px;
}
.settings-desc {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-6);
}

.settings-form {
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
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0 var(--space-4);
  transition: all var(--duration-fast) var(--ease-out-quart);
}
.input-wrapper:focus-within {
  border-color: var(--ink-500);
  box-shadow: 0 0 0 3px rgba(26, 39, 68, 0.06);
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
.save-btn {
  margin-top: var(--space-2);
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
.save-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-xl);
}
.save-btn:disabled {
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
  .profile__grid {
    grid-template-columns: 1fr;
    gap: var(--space-6);
  }
  .profile-card {
    padding: var(--space-6);
  }
}
</style>
