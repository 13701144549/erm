from django.db import models


# Create your models here.


# 创建一个用户信息表
class UserInfo(models.Model):
    username = models.CharField(max_length=52)
    password = models.CharField(max_length=52)
    roles = models.ManyToManyField(to='Role')  # 用户信息表和角色表是多对多的关联

    def __str__(self):
        return self.username


# 创建一个角色表
class Role(models.Model):
    title = models.CharField(max_length=52)
    permissions = models.ManyToManyField(to='Permission')  # 角色表和权限表是多对多的关联

    def __str__(self):
        return self.title


# 创建一个权限表
class Permission(models.Model):
    title = models.CharField(max_length=52)
    url = models.CharField(max_length=52)
    action = models.CharField(max_length=52, default='')
    group = models.ForeignKey(to='PermissionGroup', default=1)    # 权限表和分组表是一对多的关联

    def __str__(self):
        return self.title


# 创建一个权限分组表
class PermissionGroup(models.Model):
    title = models.CharField(max_length=52)

    def __str__(self):
        return self.title
