<template>
  <div class="home">
    <section class="hero">
      <h1>图像分类智能应用</h1>
      <p>基于 PyTorch 深度学习，支持 Caltech-101 和 Oxford 102 Flower 两大数据集<br/>5 种模型架构：Custom CNN · ResNet-50 · EfficientNet-B1 · ViT-B/16 · DenseNet-121</p>
      <el-button type="primary" size="large" @click="$router.push('/predict')" v-if="auth.isLoggedIn">开始预测</el-button>
      <el-button type="primary" size="large" @click="$router.push('/login')" v-else>登录使用</el-button>
    </section>

    <section class="features">
      <h2>系统特性</h2>
      <el-row :gutter="24">
        <el-col :xs="24" :sm="12" :md="8" v-for="f in features" :key="f.title">
          <el-card shadow="hover" class="feature-card">
            <el-icon :size="40" :color="f.color"><component :is="f.icon" /></el-icon>
            <h3>{{ f.title }}</h3>
            <p>{{ f.desc }}</p>
          </el-card>
        </el-col>
      </el-row>
    </section>

    <section class="models">
      <h2>模型列表</h2>
      <el-table :data="models" stripe class="model-table">
        <el-table-column prop="display_name" label="模型" width="180" />
        <el-table-column prop="dataset_name" label="数据集" width="140">
          <template #default="{ row }">{{ row.dataset_name === 'caltech101' ? 'Caltech-101' : 'Oxford 102' }}</template>
        </el-table-column>
        <el-table-column prop="accuracy" label="准确率" width="120">
          <template #default="{ row }">{{ (row.accuracy * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="file_size_mb" label="模型大小" width="120">
          <template #default="{ row }">{{ row.file_size_mb }} MB</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.accuracy >= 0.9 ? 'success' : 'warning'" size="small">
              {{ row.accuracy >= 0.95 ? '优秀' : row.accuracy >= 0.9 ? '达标' : '基准' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { predictAPI } from '../api/client'
import { Upload, DataAnalysis, Monitor, ChatDotRound, Picture, Cpu } from '@element-plus/icons-vue'

const auth = useAuthStore()
const models = ref([])

const features = [
  { title: '图片上传', desc: '支持 JPG/PNG 拖拽上传，最大 10MB', icon: Upload, color: '#409eff' },
  { title: '智能预测', desc: '5 种模型实时推理，Top-5 结果展示', icon: Cpu, color: '#67c23a' },
  { title: '历史记录', desc: '完整记录每次预测，支持回溯查看', icon: DataAnalysis, color: '#e6a23c' },
  { title: '模型对比', desc: '多模型准确率对比分析，可视化图表', icon: Monitor, color: '#f56c6c' },
  { title: '图片识别', desc: '101 类物体 + 102 种花卉细粒度分类', icon: Picture, color: '#909399' },
  { title: '用户管理', desc: '注册/登录，个人预测历史独立存储', icon: ChatDotRound, color: '#8e44ad' },
]

onMounted(async () => {
  try { const res = await predictAPI.get('/models/'); models.value = res.data.models } catch {}
})
</script>

<style scoped>
.hero { text-align: center; padding: 60px 20px 40px; background: linear-gradient(135deg, #409eff20, #67c23a20); border-radius: 12px; margin-bottom: 40px; }
.hero h1 { font-size: 36px; color: #303133; margin-bottom: 16px; }
.hero p { font-size: 16px; color: #606266; line-height: 1.8; margin-bottom: 24px; }
.features { margin-bottom: 40px; }
.features h2, .models h2 { text-align: center; font-size: 28px; margin-bottom: 24px; color: #303133; }
.feature-card { text-align: center; padding: 20px 0; height: 100%; }
.feature-card h3 { margin: 12px 0 8px; }
.feature-card p { color: #909399; font-size: 14px; }
.model-table { max-width: 700px; margin: 0 auto; }

@media (max-width: 768px) {
  .hero { padding: 40px 16px 24px; }
  .hero h1 { font-size: 24px; }
  .hero p { font-size: 14px; }
  .model-table { font-size: 12px; }
}
</style>
