<template>
  <div class="history">
    <div class="history__header">
      <div>
        <h2>预测历史</h2>
        <p class="history__count">共 {{ total }} 条记录</p>
      </div>
      <div class="history__filter">
        <select v-model="filterModel" @change="loadHistory">
          <option value="">全部模型</option>
          <option v-for="m in modelOptions" :key="m" :value="m">{{ m }}</option>
        </select>
      </div>
    </div>

    <!-- 桌面端表格 -->
    <div class="history-table hide-mobile" v-if="records.length > 0">
      <div class="table-header">
        <span class="th th--img">图片</span>
        <span class="th th--model">模型</span>
        <span class="th th--dataset">数据集</span>
        <span class="th th--class">预测类别</span>
        <span class="th th--conf">置信度</span>
        <span class="th th--time">推理耗时</span>
        <span class="th th--date">时间</span>
      </div>
      <div
        v-for="row in records"
        :key="row.id"
        class="table-row"
      >
        <span class="td td--img">
          <img :src="getImageUrl(row)" alt="" class="thumb" v-if="getImageUrl(row)" />
          <span v-else class="thumb-placeholder"></span>
        </span>
        <span class="td td--model">{{ row.model_name }}</span>
        <span class="td td--dataset">{{ row.dataset_name === 'caltech101' ? 'Caltech-101' : 'Oxford 102' }}</span>
        <span class="td td--class">
          {{ row.predicted_class }}
          <small v-if="row.top5_results?.[0]?.class_name_cn">（{{ row.top5_results[0].class_name_cn }}）</small>
        </span>
        <span class="td td--conf">
          <span class="conf-badge" :class="confClass(row.confidence)">{{ (row.confidence * 100).toFixed(1) }}%</span>
        </span>
        <span class="td td--time">{{ row.inference_time_ms }}ms</span>
        <span class="td td--date">{{ formatDate(row.created_at) }}</span>
      </div>
    </div>

    <!-- 移动端卡片 -->
    <div class="history-cards show-mobile" v-if="records.length > 0">
      <div
        v-for="row in records"
        :key="row.id"
        class="history-card"
      >
        <div class="history-card__top">
          <img :src="getImageUrl(row)" alt="" class="history-card__thumb" v-if="getImageUrl(row)" />
          <span v-else class="history-card__thumb history-card__thumb--empty"></span>
          <div class="history-card__info">
            <span class="history-card__class">{{ row.predicted_class }}</span>
            <small v-if="row.top5_results?.[0]?.class_name_cn" class="history-card__cn">{{ row.top5_results[0].class_name_cn }}</small>
          </div>
          <span class="conf-badge" :class="confClass(row.confidence)">{{ (row.confidence * 100).toFixed(1) }}%</span>
        </div>
        <div class="history-card__bottom">
          <span>{{ row.model_name }}</span>
          <span>·</span>
          <span>{{ row.dataset_name === 'caltech101' ? 'Caltech-101' : 'Oxford 102' }}</span>
          <span>·</span>
          <span>{{ row.inference_time_ms }}ms</span>
          <span>·</span>
          <span>{{ formatDate(row.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && records.length === 0" class="empty-state">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <rect x="8" y="12" width="48" height="44" rx="6" stroke="var(--warm-300)" stroke-width="2.5" fill="none"/>
        <circle cx="22" cy="26" r="4" stroke="var(--warm-300)" stroke-width="2" fill="none"/>
        <path d="M8 44l12-10 8 6 14-12 14 10" stroke="var(--warm-300)" stroke-width="2" stroke-linejoin="round" fill="none"/>
      </svg>
      <p>暂无预测记录</p>
      <span>上传图片开始你的第一次 AI 识别吧</span>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-state">
      <span class="spinner-lg"></span>
      <p>加载中...</p>
    </div>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="pagination">
      <button
        :disabled="page <= 1"
        @click="onPageChange(page - 1)"
        class="page-btn"
      >上一页</button>
      <span class="page-info">{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
      <button
        :disabled="page >= Math.ceil(total / pageSize)"
        @click="onPageChange(page + 1)"
        class="page-btn"
      >下一页</button>
    </div>
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
    const parts = row.image.original_path.replace(/\\/g, '/').split('/')
    return `/storage/images/original/${parts[parts.length - 1]}`
  }
  return ''
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function confClass(c) {
  if (c >= 0.9) return 'conf--high'
  if (c >= 0.7) return 'conf--mid'
  return 'conf--low'
}

async function loadHistory() {
  loading.value = true
  page.value = 1
  try {
    const res = await predictAPI.get('/history/', {
      params: { page: page.value, page_size: pageSize, model: filterModel.value }
    })
    records.value = res.data.records
    total.value = res.data.total
  } catch {} finally { loading.value = false }
}

async function onPageChange(p) {
  page.value = p
  loading.value = true
  try {
    const res = await predictAPI.get('/history/', {
      params: { page: p, page_size: pageSize, model: filterModel.value }
    })
    records.value = res.data.records
    total.value = res.data.total
  } catch {} finally { loading.value = false }
}

onMounted(loadHistory)
</script>

<style scoped>
.history__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}
.history__header h2 {
  font-size: var(--text-2xl);
  margin-bottom: 4px;
}
.history__count {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.history__filter select {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  padding: 8px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  outline: none;
  transition: border-color var(--duration-fast);
}
.history__filter select:focus {
  border-color: var(--ink-500);
}

/* ══════════ 桌面端表格 ══════════ */
.history-table {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  overflow: hidden;
}
.table-header {
  display: grid;
  grid-template-columns: 64px 1fr 1fr 2fr 100px 80px 130px;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--ink-50);
  border-bottom: 1px solid var(--color-border-light);
}
.th {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--ink-700);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
}
.table-row {
  display: grid;
  grid-template-columns: 64px 1fr 1fr 2fr 100px 80px 130px;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
  transition: background var(--duration-fast);
  align-items: center;
}
.table-row:last-child { border-bottom: none; }
.table-row:hover { background: var(--ink-50); }

.td {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
.td--class {
  font-weight: 500;
  color: var(--color-text);
}
.td--class small {
  font-weight: 400;
  color: var(--gold-500);
}
.thumb {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  object-fit: cover;
  display: block;
}
.thumb-placeholder {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  background: var(--warm-100);
  display: block;
}

/* 置信度标签 */
.conf-badge {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--radius-sm);
}
.conf--high {
  background: var(--success-light);
  color: var(--success);
}
.conf--mid {
  background: var(--warning-light);
  color: var(--warning);
}
.conf--low {
  background: var(--danger-light);
  color: var(--danger);
}

/* ══════════ 移动端卡片 ══════════ */
.history-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.history-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}
.history-card__top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}
.history-card__thumb {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  object-fit: cover;
  flex-shrink: 0;
}
.history-card__thumb--empty {
  background: var(--warm-100);
}
.history-card__info {
  flex: 1;
  min-width: 0;
}
.history-card__class {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.history-card__cn {
  color: var(--gold-500);
}
.history-card__bottom {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* ══════════ 空状态 ══════════ */
.empty-state {
  text-align: center;
  padding: var(--space-16) var(--space-4);
  color: var(--color-text-muted);
}
.empty-state svg { margin-bottom: var(--space-4); }
.empty-state p {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.empty-state span {
  font-size: var(--text-sm);
}

/* ══════════ 加载状态 ══════════ */
.loading-state {
  text-align: center;
  padding: var(--space-16) var(--space-4);
}
.spinner-lg {
  display: inline-block;
  width: 36px;
  height: 36px;
  border: 3px solid var(--warm-200);
  border-top-color: var(--ink-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-state p {
  margin-top: var(--space-3);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

/* ══════════ 分页 ══════════ */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  margin-top: var(--space-8);
}
.page-btn {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  padding: 8px 20px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out-quart);
}
.page-btn:hover:not(:disabled) {
  border-color: var(--ink-400);
  background: var(--ink-50);
}
.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.page-info {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

@media (max-width: 1023px) {
  .history__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
