import re
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect


class ValidPermission(MiddlewareMixin):
    def process_request(self, request):
        # 当前访问路径
        current_path = request.path_info

        # 检查是否属于白名单
        valid_url_list = ['/login/', '/register/', '/main/', '/admin/.*']
        for valid_url in valid_url_list:
            ret = re.match(valid_url, current_path)
            if ret:
                return None

        # 检验是否登陆
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('/login/')

        # 校验权限（方法一）
        # permission_list = request.session.get('permission_list', [])
        # flag = False
        # for permission in permission_list:
        #     permission = '^{}$'.format(permission)
        #     ret = re.match(permission, current_path)
        #     if ret:
        #         flag = True
        #         break
        # if not flag:
        #     return HttpResponse('没有访问权限！')
        # return None

        # 校验权限（方法二）
        permission_dict = request.session.get('permission_dict')
        for item in permission_dict.values():
            urls = item['urls']
            for reg in urls:
                reg = '^{}$'.format(reg)
                ret = re.match(reg, current_path)
                if ret:
                    request.actions = item['actions']
                    return None
        return HttpResponse('没有访问权限！')
