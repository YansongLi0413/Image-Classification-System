<template>
  <div class="predict-page">
    <h2>图片预测</h2>

    <!-- 模型选择 -->
    <el-row :gutter="16" class="config-row">
      <el-col :xs="12" :sm="6">
        <el-select v-model="dataset" placeholder="数据集" @change="onDatasetChange">
          <el-option label="Caltech-101 (物体)" value="caltech101" />
          <el-option label="Oxford 102 (花卉)" value="oxford102" />
        </el-select>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-select v-model="model" placeholder="模型">
          <el-option v-for="m in availableModels" :key="m.name" :label="m.display_name" :value="m.name" />
        </el-select>
      </el-col>
      <el-col :xs="24" :sm="12" class="model-info" v-if="selectedInfo">
        <el-tag type="info" size="small">准确率: {{ (selectedInfo.accuracy * 100).toFixed(1) }}%</el-tag>
        <el-tag size="small">{{ selectedInfo.file_size_mb }} MB</el-tag>
      </el-col>
    </el-row>

    <!-- 上传区域 -->
    <el-upload class="upload-area" drag :auto-upload="false" :show-file-list="false"
               :on-change="onFileChange" accept="image/jpeg,image/png,image/jpg">
      <div v-if="!previewUrl">
        <el-icon :size="48"><UploadFilled /></el-icon>
        <p>点击或拖拽图片到此区域</p>
        <p class="hint">支持 JPG/PNG，最大 10MB</p>
      </div>
      <img v-else :src="previewUrl" class="preview-img" />
    </el-upload>

    <!-- 预测按钮 -->
    <el-button type="primary" size="large" :loading="loading" @click="doPredict"
               :disabled="!file" style="margin-top:20px;width:100%">
      {{ loading ? '正在预测...' : '开始预测' }}
    </el-button>

    <!-- 预测结果 -->
    <div v-if="result" class="result-section">
      <h3>预测结果</h3>
      <el-card v-if="result.from_cache" class="cache-notice" shadow="never">
        <el-icon><InfoFilled /></el-icon> 命中缓存（相同图片+相同模型）
      </el-card>

      <el-row :gutter="16">
        <el-col :xs="24" :md="8" class="result-main">
          <div class="predicted-label">预测类别</div>
          <div class="predicted-class">
            {{ result.predicted_class }}
            <span v-if="result.predicted_class_cn" class="cn-name">（{{ result.predicted_class_cn }}）</span>
          </div>
          <el-progress :percentage="Math.round(result.confidence * 100)" :color="confidenceColor" :stroke-width="18">
            <span>{{ (result.confidence * 100).toFixed(1) }}%</span>
          </el-progress>
          <p class="infer-time">推理耗时: {{ result.inference_time_ms }}ms</p>
        </el-col>
        <el-col :xs="24" :md="16">
          <h4>Top-5 预测结果</h4>
          <el-table :data="result.top5_results" stripe size="small" class="top5-table">
            <el-table-column prop="class_id" label="排名" width="60" type="index" />
            <el-table-column label="类别" min-width="180">
              <template #default="{ row }">
                {{ row.class_name }}
                <span v-if="row.class_name_cn" style="color:#909399">（{{ row.class_name_cn }}）</span>
              </template>
            </el-table-column>
            <el-table-column label="置信度" width="200">
              <template #default="{ row }">
                <el-progress :percentage="Math.round(row.confidence * 100)" :stroke-width="14" :show-text="true">
                  <span>{{ (row.confidence * 100).toFixed(2) }}%</span>
                </el-progress>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { predictAPI } from '../api/client'
import { UploadFilled, InfoFilled } from '@element-plus/icons-vue'

const auth = useAuthStore()
const dataset = ref('caltech101')
const model = ref('efficientnet_b1')
const file = ref(null)
const previewUrl = ref('')
const loading = ref(false)
const result = ref(null)
const allModels = ref([])

const availableModels = computed(() => allModels.value.filter(m => m.dataset_name === dataset.value))
const selectedInfo = computed(() => availableModels.value.find(m => m.name === model.value))

const confidenceColor = computed(() => {
  if (!result.value) return '#909399'
  const c = result.value.confidence
  if (c >= 0.9) return '#67c23a'
  if (c >= 0.7) return '#e6a23c'
  return '#f56c6c'
})

function onDatasetChange() {
  const avail = availableModels.value
  if (avail.length > 0) model.value = avail[0].name
}

function onFileChange(uploadFile) {
  file.value = uploadFile.raw
  previewUrl.value = URL.createObjectURL(uploadFile.raw)
  result.value = null
}

async function doPredict() {
  if (!file.value) return
  loading.value = true
  try {
    const form = new FormData()
    form.append('image', file.value)
    form.append('model', model.value)
    form.append('dataset', dataset.value)
    const res = await predictAPI.post('/predict/', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = res.data
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '预测失败')
  } finally {
    loading.value = false
  }
}

// 加载模型列表
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'
onMounted(async () => {
  try { const res = await predictAPI.get('/models/'); allModels.value = res.data.models } catch {}
})
</script>

<style scoped>
.predict-page h2 { text-align: center; margin-bottom: 24px; }
.config-row { margin-bottom: 20px; align-items: center; }
.model-info { display: flex; gap: 8px; align-items: center; margin-top: 8px; }
.upload-area { width: 100%; }
.upload-area :deep(.el-upload) { width: 100%; }
.upload-area :deep(.el-upload-dragger) { width: 100%; padding: 40px 20px; }
.preview-img { max-width: 100%; max-height: 300px; object-fit: contain; }
.hint { font-size: 12px; color: #c0c4cc; margin-top: 8px; }
.result-section { margin-top: 32px; }
.result-section h3 { margin-bottom: 16px; }
.result-main { text-align: center; }
.result-main .predicted-label { font-size: 14px; color: #909399; margin-bottom: 8px; }
.result-main .predicted-class { font-size: 22px; font-weight: 700; color: #303133; margin-bottom: 16px; }
.result-main .cn-name { font-size: 16px; font-weight: 400; color: #67c23a; }
.infer-time { color: #909399; font-size: 13px; margin-top: 12px; }
.cache-notice { background: #ecf5ff; border: 1px solid #d9ecff; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.top5-table { margin-top: 12px; }

@media (max-width: 768px) {
  .upload-area :deep(.el-upload-dragger) { padding: 20px 12px; }
}
</style>
