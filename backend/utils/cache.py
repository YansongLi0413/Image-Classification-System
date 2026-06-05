"""
Redis 缓存工具
"""
import json
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL = {
    'session': 86400,
    'prediction': 3600,
    'model_list': 300,
    'user_history': 3600,
}


def cache_get(key: str):
    """从缓存获取值（自动 JSON 反序列化）"""
    try:
        value = cache.get(key)
        if isinstance(value, str):
            return json.loads(value)
        return value
    except Exception:
        return None


def cache_set(key: str, value, ttl: int = 3600):
    """设置缓存值（自动 JSON 序列化）"""
    try:
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)
        cache.set(key, value, ttl)
    except Exception as e:
        logger.debug(f"缓存写入失败: {e}")


def cache_delete(key: str):
    """删除缓存"""
    cache.delete(key)


def cache_delete_pattern(pattern: str):
    """按模式删除缓存（需 Redis 支持 keys 命令）"""
    try:
        cache.delete_pattern(pattern)
    except AttributeError:
        pass  # 后端不支持 pattern 删除
