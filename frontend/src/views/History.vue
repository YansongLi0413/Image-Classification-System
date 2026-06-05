<template>
  <div class="history-page">
    <h2>预测历史</h2>

    <el-row :gutter="16" class="filter-row">
      <el-col :xs="24" :sm="8">
        <el-select v-model="filterModel" placeholder="筛选模型" clearable @change="loadHistory">
          <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
        </el-select>
      </el-col>
    </el-row>

    <el-table :data="records" stripe v-loading="loading" class="history-table">
      <el-table-column label="图片" width="80">
        <template #default="{ row }">
          <el-image :src="getImageUrl(row)" style="width:50px;height:50px;border-radius:4px" fit="cover" />
        </template>
      </el-table-column>
      <el-table-column prop="model_name" label="模型" width="130" />
      <el-table-column prop="dataset_name" label="数据集" width="110">
        <template #default="{ row }">{{ row.dataset_name === 'caltech101' ? 'Caltech-101' : 'Oxford 102' }}</template>
      </el-table-column>
      <el-table-column prop="predicted_class" label="预测类别" min-width="150" />
      <el-table-column label="置信度" width="140">
        <template #default="{ row }">
          <el-progress :percentage="Math.round(row.confidence * 100)" :stroke-width="10"
                       :color="row.confidence >= 0.9 ? '#67c23a' : row.confidence >= 0.7 ? '#e6a23c' : '#f56c6c'"
                       :show-text="true"><span>{{ (row.confidence * 100).toFixed(1) }}%</span></el-progress>
        </template>
      </el-table-column>
      <el-table-column prop="inference_time_ms" label="耗时" width="80">
        <template #default="{ row }">{{ row.inference_time_ms }}ms</template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="170">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination v-if="total > pageSize" :current-page="page" :page-size="pageSize"
                   :total="total" layout="prev, pager, next" @current-change="onPageChange"
                   class="pagination" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { predictAPI } from '../api/client'

const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const filterModel = ref('')
const modelOptions = ['custom_cnn', 'resnet50', 'efficientnet_b1', 'vit_b16', 'densenet121']

function getImageUrl(row) {
  if (row.image?.original_path) {
    // original_path 是服务器上的绝对路径, 提取文件名拼接 URL
    const parts = row.image.original_path.replace(/\\/g, '/').split('/')
    const name = parts[parts.length - 1]
    return `/storage/images/original/${name}`
  }
  return ''
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN')
}

async function loadHistory() {
  loading.value = true
  try {
    const res = await predictAPI.get('/history/', {
      params: { page: page.value, page_size: pageSize, model: filterModel.value }
    })
    records.value = res.data.records
    total.value = res.data.total
  } catch {} finally { loading.value = false }
}

function onPageChange(p) { page.value = p; loadHistory() }

onMounted(loadHistory)
</script>

<style scoped>
.history-page h2 { text-align: center; margin-bottom: 24px; }
.filter-row { margin-bottom: 16px; }
.pagination { margin-top: 20px; justify-content: center; }

@media (max-width: 768px) {
  .history-table { font-size: 12px; }
}
</style>
