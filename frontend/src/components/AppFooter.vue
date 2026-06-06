<template>
  <footer class="footer">
    <!-- 装饰线 -->
    <div class="footer__rule">
      <span class="rule-diamond"></span>
    </div>

    <div class="footer__inner">
      <!-- 关于 -->
      <div class="footer__col">
        <h4 class="footer__heading">墨瞳 AI_APP</h4>
        <p class="footer__desc">基于深度学习的图像分类智能应用。支持 Caltech-101 物体识别与 Oxford 102 花卉分类，集成五种前沿模型架构，提供精准、高效的图片识别服务。</p>
      </div>

      <!-- 快速链接 -->
      <div class="footer__col">
        <h4 class="footer__heading">快速导航</h4>
        <ul class="footer__links">
          <li><router-link to="/">首页</router-link></li>
          <li><router-link to="/predict">图片预测</router-link></li>
          <li><router-link to="/history">历史记录</router-link></li>
          <li><router-link to="/profile">个人中心</router-link></li>
        </ul>
      </div>

      <!-- 技术栈 -->
      <div class="footer__col">
        <h4 class="footer__heading">技术栈</h4>
        <div class="footer__tags">
          <span class="tech-tag">PyTorch</span>
          <span class="tech-tag">Django</span>
          <span class="tech-tag">Vue.js</span>
          <span class="tech-tag">ResNet-50</span>
          <span class="tech-tag">ViT</span>
          <span class="tech-tag">EfficientNet</span>
        </div>
      </div>
    </div>

    <!-- 版权 -->
    <div class="footer__bottom">
      <div class="footer__inner">
        <p class="copyright">&copy; 2026 墨瞳 AI_APP — 深度学习图像分类智能应用</p>
        <p class="credit">Powered by PyTorch + Django + Vue.js</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
/* ══════════ 页脚容器 ══════════ */
.footer {
  background: var(--ink-900);
  color: var(--warm-200);
  position: relative;
  overflow: hidden;
}

/* 装饰规则线 */
.footer__rule {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-700), transparent);
  position: relative;
}
.rule-diamond {
  position: absolute;
  width: 10px;
  height: 10px;
  background: var(--gold-400);
  transform: rotate(45deg);
  box-shadow: 0 0 12px rgba(201, 169, 110, 0.5);
}

/* 网格布局 */
.footer__inner {
  max-width: var(--container-xl);
  margin: 0 auto;
  padding: var(--space-12) var(--space-6);
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr;
  gap: var(--space-10);
}

.footer__heading {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--gold-300);
  letter-spacing: 0.06em;
  margin-bottom: var(--space-4);
}

.footer__desc {
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  color: var(--warm-400);
  max-width: 360px;
}

.footer__links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.footer__links a {
  font-size: var(--text-sm);
  color: var(--warm-400);
  text-decoration: none;
  transition: color var(--duration-fast), transform var(--duration-fast);
  display: inline-block;
}
.footer__links a:hover {
  color: var(--gold-300);
  transform: translateX(4px);
}

.footer__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tech-tag {
  font-size: 0.6875rem;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.06);
  color: var(--warm-400);
  border: 1px solid rgba(255, 255, 255, 0.08);
  letter-spacing: 0.03em;
}

/* 底部版权 */
.footer__bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding: var(--space-6) 0;
}
.footer__bottom .footer__inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
  padding-top: 0;
  padding-bottom: 0;
  grid-template-columns: none;
}
.copyright {
  font-size: var(--text-xs);
  color: var(--warm-500);
  margin: 0;
}
.credit {
  font-size: var(--text-xs);
  color: var(--warm-600);
  margin: 0;
}

@media (max-width: 768px) {
  .footer__inner {
    grid-template-columns: 1fr;
    gap: var(--space-8);
    padding: var(--space-8) var(--space-4);
  }
  .footer__bottom .footer__inner {
    flex-direction: column;
    text-align: center;
  }
}
</style>
