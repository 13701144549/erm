from rbac.models import *
from rbac.service.permissions import *
from django.shortcuts import render, HttpResponse, redirect
# Create your views here.


def index(request):
    return render(request, 'index.html')


# 定义一个类，用于灵活匹配增删改查四个权限
class Per(object):
    def __init__(self, actions):
        self.actions = actions

    def add(self):
        return 'add' in self.actions

    def show(self):
        return 'show' in self.actions

    def edit(self):
        return 'edit' in self.actions

    def delete(self):
        return 'delete' in self.actions


# 定义一个用户函数
def users(request):
    user_list = UserInfo.objects.all()
    per = Per(request.actions)
    return render(request, 'users.html', locals())


# 定义一个角色函数
def roles(request):
    roles_list = Role.objects.all()
    per = Per(request.actions)
    return render(request, 'roles.html', locals())


# 定义登陆函数
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = UserInfo.objects.filter(username=username, password=password).first()
        if user:
            request.session["user_id"] = user.pk
            initial_session(user, request)
            return redirect('/stark/')
    return render(request, 'login.html')


# 添加用户函数
def users_add(request):
    return HttpResponse('add')


# 删除用户函数
def users_delete(request, id):
    return HttpResponse('delete')


# 编辑用户函数
def users_edit(request, id):
    return HttpResponse('edit')


# 添加角色函数
def roles_add(request):
    return HttpResponse('roles_add')


# 删除角色函数
def roles_delete(request, id):
    return HttpResponse('roles_delete')


# 编辑角色函数
def roles_edit(request, id):
    return HttpResponse('roles_edit')