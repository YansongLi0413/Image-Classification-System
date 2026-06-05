"""
用户模型 — 自定义 User + UserProfile
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """自定义用户模型"""
    ROLE_CHOICES = [('user', '普通用户'), ('admin', '管理员')]

    email = models.EmailField(unique=True, verbose_name='邮箱')
    avatar = models.URLField(max_length=500, blank=True, default='', verbose_name='头像URL')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'users_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username
