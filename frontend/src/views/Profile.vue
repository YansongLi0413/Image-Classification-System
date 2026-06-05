<template>
  <div class="profile-page">
    <h2>个人中心</h2>
    <el-row :gutter="24">
      <el-col :xs="24" :md="8">
        <el-card shadow="hover">
          <div class="user-avatar">
            <el-icon :size="64"><UserFilled /></el-icon>
            <h3>{{ auth.user?.username }}</h3>
            <p>{{ auth.user?.email }}</p>
            <el-tag :type="auth.user?.role === 'admin' ? 'danger' : 'primary'" size="small">
              {{ auth.user?.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="16">
        <el-card shadow="hover">
          <h3>修改密码</h3>
          <el-form :model="pwdForm" label-position="top" @submit.prevent="changePwd">
            <el-form-item label="原密码">
              <el-input v-model="pwdForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pwdForm.new_password" type="password" show-password />
            </el-form-item>
            <el-button type="primary" native-type="submit" :loading="pwdLoading">修改密码</el-button>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { authAPI } from '../api/client'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'

const auth = useAuthStore()
const pwdForm = ref({ old_password: '', new_password: '' })
const pwdLoading = ref(false)

async function changePwd() {
  pwdLoading.value = true
  try {
    await authAPI.post('/auth/change-password/', pwdForm.value)
    ElMessage.success('密码修改成功')
    pwdForm.value = { old_password: '', new_password: '' }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '修改失败')
  } finally { pwdLoading.value = false }
}
</script>

<style scoped>
.profile-page h2 { text-align: center; margin-bottom: 24px; }
.user-avatar { text-align: center; padding: 20px 0; }
.user-avatar h3 { margin: 12px 0 8px; }
.user-avatar p { color: #909399; margin-bottom: 12px; }
</style>
