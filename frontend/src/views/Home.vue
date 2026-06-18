<template>
  <div class="home">
    <!-- ══════════ Hero ══════════ -->
    <section class="hero">
      <div class="hero__bg">
        <div class="hero-glow hero-glow--1"></div>
        <div class="hero-glow hero-glow--2"></div>
        <div class="hero-pattern"></div>
      </div>
      <div class="hero__content">
        <div class="hero__text">
          <span class="hero__badge">AI 驱动 · 图像识别</span>
          <h1 class="hero__title">
            墨瞳<span class="hero__title--accent">识物</span>
          </h1>
          <p class="hero__desc">
            基于深度学习前沿架构，搭载五种主流模型。<br />
            覆盖 <strong>101 类日常物体</strong> 与 <strong>102 种花卉</strong> 细粒度识别，<br />
            一键上传，毫秒级精准预测。
          </p>
          <div class="hero__actions">
            <router-link to="/predict" class="hero-btn hero-btn--primary" v-if="auth.isLoggedIn">
              开始预测
              <svg width="18" height="18" viewBox="0 0 18 18"><path d="M6 4l5 5-5 5" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </router-link>
            <router-link to="/login" class="hero-btn hero-btn--primary" v-else>
              立即使用
            </router-link>
            <a href="#features" class="hero-btn hero-btn--ghost">了解更多</a>
          </div>
          <div class="hero__stats">
            <div class="stat-item">
              <span class="stat-number">5</span>
              <span class="stat-label">模型架构</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-number">203</span>
              <span class="stat-label">识别类别</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-number">&gt;95%</span>
              <span class="stat-label">识别准确率</span>
            </div>
          </div>
        </div>
        <div class="hero__visual">
          <div class="hero-card hero-card--1">
            <div class="hero-card__img">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect width="48" height="48" rx="12" fill="var(--ink-100)"/>
                <path d="M16 32V16l8 8 8-8v16" stroke="var(--ink-600)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span>物体分类</span>
          </div>
          <div class="hero-card hero-card--2">
            <div class="hero-card__img">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect width="48" height="48" rx="12" fill="var(--gold-100)"/>
                <circle cx="18" cy="18" r="6" stroke="var(--gold-500)" stroke-width="3"/>
                <circle cx="30" cy="18" r="6" stroke="var(--gold-500)" stroke-width="3"/>
                <circle cx="24" cy="30" r="6" stroke="var(--gold-500)" stroke-width="3"/>
              </svg>
            </div>
            <span>花卉识别</span>
          </div>
          <div class="hero-card hero-card--3">
            <div class="hero-card__img">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect width="48" height="48" rx="12" fill="var(--ink-100)"/>
                <path d="M14 14h20v20H14z" stroke="var(--ink-600)" stroke-width="3" rx="4"/>
                <path d="M24 18v12M18 24h12" stroke="var(--ink-600)" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>
            <span>即时预测</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ 特性 ══════════ -->
    <section class="features" id="features">
      <div class="section-header">
        <span class="section-label">核心特性</span>
        <h2>为什么选择墨瞳</h2>
        <p class="section-desc">全方位满足图像识别需求，从研究到应用，一步到位</p>
      </div>
      <div class="features__grid">
        <div
          v-for="(f, i) in features"
          :key="f.title"
          class="feature-card"
          :style="{ animationDelay: `${i * 0.08}s` }"
        >
          <div class="feature-card__icon" :style="{ background: f.gradient }">
            <el-icon :size="28"><component :is="f.icon" /></el-icon>
          </div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ══════════ 模型展示 ══════════ -->
    <section class="models">
      <div class="section-header">
        <span class="section-label">模型架构</span>
        <h2>五大前沿模型</h2>
        <p class="section-desc">从经典 CNN 到 Vision Transformer，覆盖主流深度学习架构</p>
      </div>
      <div class="models__grid">
        <div
          v-for="(m, i) in modelList"
          :key="m.name"
          class="model-card"
          :style="{ animationDelay: `${i * 0.1}s` }"
        >
          <div class="model-card__rank">{{ i + 1 }}</div>
          <h4>{{ m.displayName }}</h4>
          <span class="model-card__type">{{ m.type }}</span>
          <div class="model-card__ring">
            <svg viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" fill="none" stroke="var(--warm-100)" stroke-width="6"/>
              <circle
                cx="50" cy="50" r="42" fill="none"
                :stroke="m.color" stroke-width="6" stroke-linecap="round"
                :stroke-dasharray="`${m.accuracy * 264} 264`"
                transform="rotate(-90 50 50)"
                class="model-card__ring-arc"
              />
            </svg>
            <span class="model-card__acc" :style="{ color: m.color }">{{ (m.accuracy * 100).toFixed(1) }}%</span>
          </div>
          <span class="model-card__label">准确率</span>
        </div>
      </div>
    </section>

    <!-- ══════════ CTA ══════════ -->
    <section class="cta">
      <div class="cta__card">
        <h2>准备好体验了吗？</h2>
        <p>上传一张图片，让 AI 告诉你它看到了什么</p>
        <router-link to="/predict" class="hero-btn hero-btn--primary" v-if="auth.isLoggedIn">
          马上预测
        </router-link>
        <router-link to="/register" class="hero-btn hero-btn--primary" v-else>
          免费注册开始使用
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { Upload, Cpu, DataAnalysis, Monitor, Picture, ChatDotRound } from '@element-plus/icons-vue'

const auth = useAuthStore()

const features = [
  {
    title: '图片上传',
    desc: '支持 JPG / PNG 格式，拖拽上传，最大 10MB，即时预览',
    icon: Upload,
    gradient: 'linear-gradient(135deg, #2a4a8a, #4a6db5)',
  },
  {
    title: '智能预测',
    desc: '五种模型实时推理，返回 Top-5 预测与置信度评分',
    icon: Cpu,
    gradient: 'linear-gradient(135deg, #1a6b3c, #388e56)',
  },
  {
    title: '历史记录',
    desc: '完整保存每次预测，支持按模型筛选与分页回溯',
    icon: DataAnalysis,
    gradient: 'linear-gradient(135deg, #8b6914, #c9a96e)',
  },
  {
    title: '模型对比',
    desc: '多模型准确率横向对比，可视化图表直观展示差异',
    icon: Monitor,
    gradient: 'linear-gradient(135deg, #7c3a5e, #b84c7d)',
  },
  {
    title: '双数据集',
    desc: 'Caltech-101 物体 + Oxford 102 花卉，203 个类别全覆盖',
    icon: Picture,
    gradient: 'linear-gradient(135deg, #3a5e7c, #5a8db8)',
  },
  {
    title: '用户系统',
    desc: '注册登录、JWT 认证，个人预测数据独立安全存储',
    icon: ChatDotRound,
    gradient: 'linear-gradient(135deg, #5c3d0a, #b8922a)',
  },
]

const modelList = [
  { name: 'efficientnet', displayName: 'EfficientNet-B1', type: '迁移学习', accuracy: 0.93, color: '#388e56' },
  { name: 'densenet', displayName: 'DenseNet-121', type: '迁移学习', accuracy: 0.93, color: '#2a4a8a' },
  { name: 'resnet50', displayName: 'ResNet-50', type: '迁移学习', accuracy: 0.92, color: '#4a6db5' },
  { name: 'vit', displayName: 'ViT-B/16', type: 'Transformer', accuracy: 0.92, color: '#7c3a5e' },
  { name: 'custom_cnn', displayName: 'Custom CNN', type: '从头训练', accuracy: 0.91, color: '#b8922a' },
]
</script>

<style scoped>
/* ══════════ Hero ══════════ */
.hero {
  position: relative;
  overflow: hidden;
  padding: var(--space-20) 0 var(--space-16);
  margin: -24px -20px 0;
  border-radius: 0 0 var(--radius-2xl) var(--radius-2xl);
}
.hero__bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(175deg, var(--warm-50) 0%, var(--ink-50) 40%, var(--warm-75) 100%);
  z-index: 0;
}
.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  pointer-events: none;
}
.hero-glow--1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(42, 74, 138, 0.25), transparent);
  top: -100px;
  right: -60px;
}
.hero-glow--2 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(201, 169, 110, 0.2), transparent);
  bottom: -80px;
  left: -40px;
}
.hero-pattern {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 80%, rgba(201, 169, 110, 0.08) 0, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(42, 74, 138, 0.06) 0, transparent 50%);
  opacity: 0.6;
}

.hero__content {
  position: relative;
  z-index: 1;
  max-width: var(--container-xl);
  margin: 0 auto;
  padding: 0 var(--space-6);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-12);
  align-items: center;
}

.hero__badge {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
  color: var(--gold-700);
  background: var(--gold-100);
  padding: 6px 14px;
  border-radius: var(--radius-full);
  margin-bottom: var(--space-6);
}

.hero__title {
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  font-weight: 900;
  color: var(--ink-800);
  line-height: 1.15;
  margin-bottom: var(--space-6);
  letter-spacing: 0.04em;
}
.hero__title--accent {
  color: var(--gold-400);
  position: relative;
}

.hero__desc {
  font-size: var(--text-md);
  line-height: var(--leading-relaxed);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-8);
  max-width: 460px;
}
.hero__desc strong {
  color: var(--color-text);
  font-weight: 600;
}

.hero__actions {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-10);
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 600;
  padding: 14px 28px;
  border-radius: var(--radius-lg);
  text-decoration: none;
  transition: all var(--duration-normal) var(--ease-out-expo);
  cursor: pointer;
  border: none;
}
.hero-btn--primary {
  background: linear-gradient(135deg, var(--ink-700), var(--ink-600));
  color: #fff;
  box-shadow: 0 8px 28px rgba(26, 39, 68, 0.25);
}
.hero-btn--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 36px rgba(26, 39, 68, 0.35);
}
.hero-btn--ghost {
  background: var(--color-surface);
  color: var(--ink-700);
  border: 1px solid var(--color-border);
}
.hero-btn--ghost:hover {
  border-color: var(--ink-400);
  background: var(--ink-50);
}

/* Hero 统计 */
.hero__stats {
  display: flex;
  gap: var(--space-6);
  align-items: center;
}
.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat-number {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--ink-700);
  line-height: 1;
}
.stat-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  letter-spacing: var(--tracking-wide);
}
.stat-divider {
  width: 1px;
  height: 36px;
  background: var(--color-border);
}

/* Hero 装饰卡片 */
.hero__visual {
  position: relative;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hero-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  box-shadow: var(--shadow-lg);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
  animation: float 5s ease-in-out infinite;
}
.hero-card--1 { top: 15%; left: 15%; animation-delay: 0s; }
.hero-card--2 { top: 45%; right: 10%; animation-delay: 1.6s; }
.hero-card--3 { bottom: 15%; left: 25%; animation-delay: 3.2s; }
.hero-card__img svg { display: block; }

/* ══════════ 分区标题 ══════════ */
.section-header {
  text-align: center;
  margin-bottom: var(--space-12);
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
  max-width: 480px;
  margin: 0 auto;
}

/* ══════════ 特性网格 ══════════ */
.features {
  padding: var(--space-20) 0;
}
.features__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}
.feature-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  text-align: center;
  cursor: default;
  transition: all var(--duration-normal) var(--ease-out-expo);
  animation: slideUp 0.6s var(--ease-out-expo) both;
  position: relative;
  overflow: hidden;
}
.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--gold-400), transparent);
  opacity: 0;
  transition: opacity var(--duration-normal) var(--ease-out-quart);
}
.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-xl);
  border-color: transparent;
}
.feature-card:hover::before {
  opacity: 1;
}
.feature-card__icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-4);
  color: #fff;
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}
.feature-card h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  margin-bottom: var(--space-2);
}
.feature-card p {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  line-height: var(--leading-relaxed);
}

/* ══════════ 模型卡片 ══════════ */
.models {
  padding: var(--space-12) 0 var(--space-20);
}
.models__grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--space-5);
}
.model-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-6) var(--space-4);
  text-align: center;
  animation: scaleIn 0.5s var(--ease-spring) both;
  transition: all var(--duration-normal) var(--ease-out-expo);
  position: relative;
}
.model-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}
.model-card__rank {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--ink-700);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
}
.model-card h4 {
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: 4px;
}
.model-card__type {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  display: block;
  margin-bottom: var(--space-4);
}
.model-card__ring {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-2);
}
.model-card__ring svg { width: 80px; height: 80px; }
.model-card__ring-arc {
  transition: stroke-dasharray 1s var(--ease-out-expo);
}
.model-card__acc {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
}
.model-card__label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* ══════════ CTA ══════════ */
.cta {
  padding: var(--space-8) 0 var(--space-16);
}
.cta__card {
  background: linear-gradient(135deg, var(--ink-800), var(--ink-700));
  border-radius: var(--radius-2xl);
  padding: var(--space-16) var(--space-8);
  text-align: center;
  position: relative;
  overflow: hidden;
}
.cta__card::before {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(201, 169, 110, 0.2), transparent);
  top: -80px;
  right: -60px;
  border-radius: 50%;
}
.cta__card h2 {
  color: #fff;
  font-size: var(--text-3xl);
  margin-bottom: var(--space-3);
}
.cta__card p {
  color: var(--warm-300);
  font-size: var(--text-md);
  margin-bottom: var(--space-8);
}
.cta__card .hero-btn--primary {
  background: linear-gradient(135deg, var(--gold-400), var(--gold-500));
  color: var(--ink-800);
}

/* ══════════ 响应式 ══════════ */
@media (max-width: 1024px) {
  .hero__content {
    grid-template-columns: 1fr;
    gap: var(--space-8);
  }
  .hero__visual {
    display: none;
  }
  .features__grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .models__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .hero {
    padding: var(--space-12) 0 var(--space-10);
    margin: -12px -10px 0;
    border-radius: 0 0 var(--radius-xl) var(--radius-xl);
  }
  .hero__title {
    font-size: var(--text-3xl);
  }
  .hero__desc {
    font-size: var(--text-base);
  }
  .hero__actions {
    flex-direction: column;
  }
  .hero__stats {
    gap: var(--space-4);
  }
  .stat-number {
    font-size: 1.35rem;
  }
  .features__grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }
  .models__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }
  .section-header h2 {
    font-size: var(--text-2xl);
  }
  .cta__card {
    padding: var(--space-10) var(--space-4);
  }
  .cta__card h2 {
    font-size: var(--text-2xl);
  }
}
</style>
