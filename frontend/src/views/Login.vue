<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="hover">
      <h2>登录</h2>
      <el-form :model="form" label-position="top" @submit.prevent="doLogin">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" style="width:100%">登录</el-button>
      </el-form>
      <p class="switch-link">还没有账号？<el-link type="primary" href="/register">立即注册</el-link></p>
    </el-card>
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
const form = ref({ username: '', password: '' })

async function doLogin() {
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push('/predict')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '登录失败')
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { display: flex; justify-content: center; align-items: center; min-height: 60vh; }
.auth-card { width: 100%; max-width: 400px; padding: 20px; }
.auth-card h2 { text-align: center; margin-bottom: 24px; }
.switch-link { text-align: center; margin-top: 16px; color: #909399; }
</style>
