<template>
  <div class="predict">
    <div class="section-header">
      <span class="section-label">图片预测</span>
      <h2>上传图片 · 智能识别</h2>
      <p class="section-desc">选择模型与数据集，上传图片，即刻获得 AI 预测结果</p>
    </div>

    <!-- ══════════ 配置栏 ══════════ -->
    <div class="config-bar">
      <div class="config-item">
        <label>数据集</label>
        <div class="segmented">
          <button
            :class="{ active: dataset === 'caltech101' }"
            @click="onDatasetChange('caltech101')"
          >Caltech-101<br/><small>物体识别</small></button>
          <button
            :class="{ active: dataset === 'oxford102' }"
            @click="onDatasetChange('oxford102')"
          >Oxford 102<br/><small>花卉识别</small></button>
        </div>
      </div>
      <div class="config-item">
        <label>模型</label>
        <div class="model-select">
          <button
            v-for="m in availableModels"
            :key="m.name"
            :class="{ active: model === m.name }"
            @click="model = m.name"
            class="model-chip"
          >
            {{ m.display_name }}
            <small>{{ (m.accuracy * 100).toFixed(0) }}%</small>
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════ 上传区域 ══════════ -->
    <div
      class="upload-zone"
      :class="{ 'upload-zone--has-image': previewUrl, 'upload-zone--dragover': dragover }"
      @dragover.prevent="dragover = true"
      @dragleave.prevent="dragover = false"
      @drop.prevent="onDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/jpg"
        @change="onFileChange"
        class="upload-zone__input"
      />
      <div v-if="!previewUrl" class="upload-zone__placeholder" @click="$refs.fileInput.click()">
        <div class="upload-icon-circle">
          <svg width="36" height="36" viewBox="0 0 36 36"><path d="M18 8v12M12 14h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><rect x="4" y="20" width="28" height="12" rx="3" stroke="currentColor" stroke-width="2" fill="none"/></svg>
        </div>
        <p class="upload-text">点击或拖拽图片到此处</p>
        <p class="upload-hint">支持 JPG / PNG 格式，最大 10MB</p>
      </div>
      <div v-else class="upload-zone__preview" @click="$refs.fileInput.click()">
        <img :src="previewUrl" alt="预览" />
        <button class="preview-remove" @click.stop="clearImage">
          <svg width="18" height="18" viewBox="0 0 18 18"><path d="M5 5l8 8M13 5l-8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
      </div>
    </div>

    <!-- ══════════ 预测按钮 ══════════ -->
    <button
      class="predict-btn"
      :disabled="!file || loading"
      @click="doPredict"
    >
      <span v-if="loading" class="spinner"></span>
      <span v-else-if="!file">请先上传图片</span>
      <span v-else>开始预测</span>
    </button>

    <!-- ══════════ 预测结果 ══════════ -->
    <Transition name="result">
      <div v-if="result" class="result">
        <div v-if="result.from_cache" class="result__cache-badge">
          <svg width="16" height="16" viewBox="0 0 16 16"><circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M5 8l2 2 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
          命中缓存（相同图片+相同模型）
        </div>

        <div class="result__main">
          <!-- Top-1 大卡片 -->
          <div class="result-top1">
            <div class="result-top1__label">预测类别</div>
            <div class="result-top1__name">{{ result.predicted_class }}</div>
            <div v-if="result.predicted_class_cn" class="result-top1__cn">{{ result.predicted_class_cn }}</div>
            <div class="confidence-ring">
              <svg viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="var(--warm-100)" stroke-width="8"/>
                <circle
                  cx="60" cy="60" r="50" fill="none"
                  :stroke="confidenceColor" stroke-width="8" stroke-linecap="round"
                  :stroke-dasharray="`${result.confidence * 314} 314`"
                  transform="rotate(-90 60 60)"
                  class="confidence-arc"
                />
              </svg>
              <div class="confidence-ring__text">
                <span class="confidence-value" :style="{ color: confidenceColor }">{{ (result.confidence * 100).toFixed(1) }}%</span>
                <span class="confidence-label">置信度</span>
              </div>
            </div>
            <span class="infer-time">推理耗时 {{ result.inference_time_ms }}ms</span>
          </div>

          <!-- Top-5 列表 -->
          <div class="result-top5">
            <h4>Top-5 预测结果</h4>
            <div
              v-for="(item, i) in result.top5_results"
              :key="item.class_id"
              class="top5-item"
              :class="{ 'top5-item--first': i === 0 }"
            >
              <span class="top5-rank">{{ i + 1 }}</span>
              <div class="top5-info">
                <span class="top5-name">{{ item.class_name }}</span>
                <span v-if="item.class_name_cn" class="top5-cn">{{ item.class_name_cn }}</span>
              </div>
              <div class="top5-bar-wrapper">
                <div class="top5-bar" :style="{ width: `${item.confidence * 100}%`, background: i === 0 ? 'var(--ink-700)' : 'var(--warm-300)' }"></div>
              </div>
              <span class="top5-conf">{{ (item.confidence * 100).toFixed(2) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { predictAPI } from '../api/client'
import { ElMessage } from 'element-plus'

const dataset = ref('caltech101')
const model = ref('efficientnet_b1')
const file = ref(null)
const previewUrl = ref('')
const loading = ref(false)
const result = ref(null)
const dragover = ref(false)
const fileInput = ref(null)

const allModels = ref([
  { name: 'custom_cnn', display_name: 'Custom CNN', dataset_name: 'caltech101', accuracy: 0.90, file_size_mb: 35 },
  { name: 'resnet50', display_name: 'ResNet-50', dataset_name: 'caltech101', accuracy: 0.93, file_size_mb: 94 },
  { name: 'efficientnet_b1', display_name: 'EfficientNet-B1', dataset_name: 'caltech101', accuracy: 0.95, file_size_mb: 28 },
  { name: 'vit_b16', display_name: 'ViT-B/16', dataset_name: 'caltech101', accuracy: 0.92, file_size_mb: 330 },
  { name: 'densenet121', display_name: 'DenseNet-121', dataset_name: 'caltech101', accuracy: 0.95, file_size_mb: 30 },
  { name: 'custom_cnn', display_name: 'Custom CNN', dataset_name: 'oxford102', accuracy: 0.90, file_size_mb: 35 },
  { name: 'resnet50', display_name: 'ResNet-50', dataset_name: 'oxford102', accuracy: 0.93, file_size_mb: 94 },
  { name: 'efficientnet_b1', display_name: 'EfficientNet-B1', dataset_name: 'oxford102', accuracy: 0.95, file_size_mb: 28 },
  { name: 'vit_b16', display_name: 'ViT-B/16', dataset_name: 'oxford102', accuracy: 0.92, file_size_mb: 330 },
  { name: 'densenet121', display_name: 'DenseNet-121', dataset_name: 'oxford102', accuracy: 0.95, file_size_mb: 30 },
])

const availableModels = computed(() => allModels.value.filter(m => m.dataset_name === dataset.value))

const confidenceColor = computed(() => {
  const c = result.value?.confidence
  if (!c) return 'var(--ink-700)'
  if (c >= 0.9) return 'var(--success)'
  if (c >= 0.7) return 'var(--warning)'
  return 'var(--danger)'
})

function onDatasetChange(ds) {
  dataset.value = ds
  const avail = availableModels.value
  if (avail.length > 0) model.value = avail[0].name
}

function onFileChange(e) {
  const f = e.target.files?.[0]
  if (f) { setFile(f) }
}

function onDrop(e) {
  dragover.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) { setFile(f) }
}

function setFile(f) {
  if (!f.type.startsWith('image/')) {
    return ElMessage.warning('请上传图片文件')
  }
  if (f.size > 10 * 1024 * 1024) {
    return ElMessage.warning('图片大小不能超过 10MB')
  }
  file.value = f
  previewUrl.value = URL.createObjectURL(f)
  result.value = null
}

function clearImage() {
  file.value = null
  previewUrl.value = ''
  result.value = null
  if (fileInput.value) fileInput.value.value = ''
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
    ElMessage.error(e.response?.data?.error || '预测失败，请稍后重试')
  } finally { loading.value = false }
}

// 加载模型列表
import { onMounted } from 'vue'
onMounted(async () => {
  try {
    const res = await predictAPI.get('/models/')
    if (res.data?.models?.length) {
      allModels.value = res.data.models
    }
  } catch {}
})
</script>

<style scoped>
/* ══════════ 分区标题 ══════════ */
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

/* ══════════ 配置栏 ══════════ */
.config-bar {
  display: flex;
  gap: var(--space-6);
  flex-wrap: wrap;
  margin-bottom: var(--space-6);
}
.config-item {
  flex: 1;
  min-width: 240px;
}
.config-item label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
}

/* 分段选择 */
.segmented {
  display: flex;
  gap: 2px;
  background: var(--warm-100);
  border-radius: var(--radius-md);
  padding: 3px;
}
.segmented button {
  flex: 1;
  border: none;
  background: transparent;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out-quart);
  text-align: center;
}
.segmented button small {
  display: block;
  font-size: 0.65rem;
  color: var(--color-text-muted);
  font-weight: 400;
}
.segmented button.active {
  background: var(--color-surface);
  color: var(--ink-700);
  box-shadow: var(--shadow-sm);
}
.segmented button.active small {
  color: var(--ink-500);
}

/* 模型芯片 */
.model-select {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.model-chip {
  display: flex;
  align-items: baseline;
  gap: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: 8px 14px;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out-quart);
}
.model-chip small {
  font-size: 0.65rem;
  color: var(--color-text-muted);
}
.model-chip:hover {
  border-color: var(--ink-400);
}
.model-chip.active {
  background: var(--ink-50);
  border-color: var(--ink-500);
  color: var(--ink-700);
}
.model-chip.active small {
  color: var(--ink-500);
}

/* ══════════ 上传区域 ══════════ */
.upload-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-xl);
  transition: all var(--duration-normal) var(--ease-out-quart);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  min-height: 220px;
}
.upload-zone:hover {
  border-color: var(--ink-400);
  background: var(--ink-50);
}
.upload-zone--dragover {
  border-color: var(--ink-500);
  background: var(--ink-50);
  box-shadow: 0 0 0 8px rgba(26, 39, 68, 0.04);
}
.upload-zone--has-image {
  border-style: solid;
  border-color: var(--color-border-light);
  min-height: auto;
}
.upload-zone__input {
  display: none;
}
.upload-zone__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12) var(--space-6);
}
.upload-icon-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--ink-50);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ink-400);
  margin-bottom: var(--space-4);
  transition: all var(--duration-normal) var(--ease-out-quart);
}
.upload-zone:hover .upload-icon-circle {
  background: var(--ink-100);
  color: var(--ink-600);
  transform: scale(1.05);
}
.upload-text {
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 4px;
}
.upload-hint {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* 预览 */
.upload-zone__preview {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}
.upload-zone__preview img {
  max-width: 100%;
  max-height: 360px;
  object-fit: contain;
  border-radius: var(--radius-md);
}
.preview-remove {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0,0,0,0.5);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(6px);
  transition: background var(--duration-fast);
}
.preview-remove:hover { background: rgba(0,0,0,0.7); }

/* ══════════ 预测按钮 ══════════ */
.predict-btn {
  display: block;
  width: 100%;
  margin-top: var(--space-6);
  padding: 16px;
  font-family: var(--font-body);
  font-size: var(--text-md);
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, var(--ink-700), var(--ink-600));
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  box-shadow: var(--shadow-ink);
  transition: all var(--duration-normal) var(--ease-out-expo);
}
.predict-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}
.predict-btn:disabled {
  background: var(--warm-200);
  color: var(--color-text-muted);
  cursor: not-allowed;
  box-shadow: none;
}
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ══════════ 结果 ══════════ */
.result {
  margin-top: var(--space-8);
  animation: slideUp 0.5s var(--ease-out-expo) both;
}
.result__cache-badge {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--info-light);
  border: 1px solid var(--info);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  color: var(--info);
  margin-bottom: var(--space-6);
}
.result__main {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: var(--space-8);
}

/* Top-1 卡片 */
.result-top1 {
  text-align: center;
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-8) var(--space-6);
}
.result-top1__label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
  margin-bottom: var(--space-3);
}
.result-top1__name {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 4px;
  word-break: break-word;
}
.result-top1__cn {
  font-size: var(--text-base);
  color: var(--gold-500);
  margin-bottom: var(--space-6);
}
.confidence-ring {
  position: relative;
  width: 140px;
  height: 140px;
  margin: 0 auto var(--space-3);
}
.confidence-ring svg { width: 140px; height: 140px; }
.confidence-arc {
  transition: stroke-dasharray 1s var(--ease-out-expo);
}
.confidence-ring__text {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.confidence-value {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}
.confidence-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
.infer-time {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* Top-5 列表 */
.result-top5 {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
}
.result-top5 h4 {
  font-size: var(--text-md);
  font-weight: 600;
  margin-bottom: var(--space-4);
}
.top5-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border-light);
}
.top5-item:last-child { border-bottom: none; }
.top5-item--first {
  background: var(--ink-50);
  margin: 0 -16px;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
  border-radius: var(--radius-md);
}
.top5-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--warm-100);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: 700;
  color: var(--color-text-muted);
  flex-shrink: 0;
}
.top5-item--first .top5-rank {
  background: var(--ink-700);
  color: #fff;
}
.top5-info {
  width: 160px;
  flex-shrink: 0;
}
.top5-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
}
.top5-cn {
  font-size: var(--text-xs);
  color: var(--gold-500);
}
.top5-bar-wrapper {
  flex: 1;
  height: 6px;
  background: var(--warm-100);
  border-radius: var(--radius-full);
  overflow: hidden;
}
.top5-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.8s var(--ease-out-expo);
}
.top5-conf {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
  width: 48px;
  text-align: right;
  flex-shrink: 0;
}

/* 结果过渡 */
.result-enter-active { animation: slideUp 0.5s var(--ease-out-expo) both; }
.result-leave-active { animation: fadeIn 0.2s var(--ease-out-quart) reverse both; }

@media (max-width: 768px) {
  .config-bar { flex-direction: column; gap: var(--space-4); }
  .model-select { flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 4px; }
  .model-chip { flex-shrink: 0; }
  .result__main { grid-template-columns: 1fr; }
  .result-top1 { order: -1; }
  .top5-info { width: 120px; }
}
</style>
