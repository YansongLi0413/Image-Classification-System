"""
数据校验工具
"""
from django.conf import settings


def validate_image(image_file) -> tuple:
    """
    校验上传图片
    Returns: (is_valid: bool, error_message: str)
    """
    # 大小校验
    if image_file.size > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        return False, f'图片大小不能超过 {max_mb:.0f}MB'

    # 类型校验
    if image_file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        return False, f'不支持的图片格式: {image_file.content_type}，仅支持 JPG/PNG'

    # 文件名安全校验
    import re
    if not re.match(r'^[\w\-. ]+$', image_file.name):
        return False, '文件名包含非法字符'

    return True, ''
