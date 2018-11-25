from django import template
from rbac.models import *
register = template.Library()


@register.inclusion_tag('nav-menu.html')
def get_nav_menu(request):
    user_id = request.session.get('user_id')
    user = UserInfo.objects.filter(pk=user_id).first()
    menu_permission_list = request.session.get('menu_permission_list')
    return {'user': user, 'menu_permission_list': menu_permission_list}
