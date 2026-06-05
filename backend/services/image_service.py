"""
图片服务 — 保存、校验、处理
"""
import hashlib
import logging
from pathlib import Path
from django.conf import settings
from apps.predictions.models import ImageInfo
from PIL import Image

logger = logging.getLogger(__name__)


class ImageService:
    """图片处理服务"""

    @staticmethod
    def save_image(image_file, user) -> ImageInfo:
        """保存上传图片并创建数据库记录"""
        storage_dir = Path(settings.STORAGE_ROOT) / 'images' / 'original'
        storage_dir.mkdir(parents=True, exist_ok=True)

        # 计算哈希
        content = image_file.read()
        image_hash = hashlib.sha256(content).hexdigest()

        # 检查是否已存在相同图片
        existing = ImageInfo.objects.filter(image_hash=image_hash, user=user).first()
        if existing:
            logger.info(f"图片已存在: {image_hash[:12]}")
            return existing

        # 保存文件
        ext = Path(image_file.name).suffix or '.jpg'
        filename = f'{image_hash[:16]}{ext}'
        filepath = storage_dir / filename

        with open(filepath, 'wb') as f:
            f.write(content)

        # 获取图片信息
        image_file.seek(0)
        img = Image.open(image_file)
        width, height = img.size

        # 创建数据库记录
        image_info = ImageInfo.objects.create(
            user=user,
            original_path=str(filepath),
            original_size=len(content),
            width=width,
            height=height,
            format=ext.lstrip('.').lower(),
            image_hash=image_hash,
        )
        logger.info(f"图片已保存: {filename} ({width}x{height}, {len(content)}B)")
        return image_info
