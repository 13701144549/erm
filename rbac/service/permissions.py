def initial_session(user, request):
    # 方案一
    # permissions = user.roles.all().values('permissions__url').distinct()
    # permission_list = []
    # for item in permissions:
    #     permission_list.append(item['permissions__url'])
    # request.session['permission_list'] = permission_list

    # 方案二
    permissions = user.roles.all().values('permissions__url', 'permissions__group_id', 'permissions__action').distinct()
    permission_dict = {}
    for item in permissions:
        if not item.get('permissions__group_id') in permission_dict:
            permission_dict[item.get('permissions__group_id')] = {'urls': [item['permissions__url'], ],
                                                                  'actions': [item['permissions__action'], ]}
        else:
            permission_dict[item.get('permissions__group_id')]['urls'].append(item['permissions__url'])
            permission_dict[item.get('permissions__group_id')]['actions'].append(item['permissions__action'])
    request.session['permission_dict'] = permission_dict

    # 注册菜单管理
    permissions = user.roles.all().values('permissions__url', 'permissions__title',
                                          'permissions__action').distinct()
    menu_permission_list = []
    for item in permissions:
        if item['permissions__action'] == 'show':
            menu_permission_list.append((item['permissions__url'], item['permissions__title']))
    request.session['menu_permission_list'] = menu_permission_list
