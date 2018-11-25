from stark.service.stark import site, ModelStark
from .models import *


class UserInfoConfig(ModelStark):
    list_display = ['id', 'username', 'roles']
    # list_display_links = ['username']


class RoleConfig(ModelStark):
    list_display = ['id', 'title', 'permissions']
    # list_display_links = ['title']


class PermissionConfig(ModelStark):
    list_display = ['id', 'title', 'url', 'action', 'group']
    # list_display_links = ['title']


class PermissionGroupConfig(ModelStark):
    list_display = ['id', 'title']
    # list_display_links = ['title']


site.register(UserInfo, UserInfoConfig)
site.register(Role, RoleConfig)
site.register(Permission, PermissionConfig)
site.register(PermissionGroup, PermissionGroupConfig)

