from django.test import TestCase

# Create your tests here.


# list = [{'permissions__url': '/users/',
#          'permissions__group_id': 1,
#          'permissions__action': 'list'},
#
#         {'permissions__url': '/users/add/',
#          'permissions__group_id': 1,
#          'permissions__action': 'add'},
#
#         {'permissions__url': '/users/delete/(\\d+)',
#          'permissions__group_id': 1,
#          'permissions__action': 'delete'},
#
#         {'permissions__url': 'users/edit/(\\d+)',
#          'permissions__group_id': 1,
#          'permissions__action': 'edit'},
#
#         {'permissions__url': '/roles/',
#          'permissions__group_id': 2,
#          'permissions__action': 'list'}
#
#         ]

# dic = {1: {'urls': [], 'actions': []}, 2: {'urls': [], 'actions': []}}
# for dic1 in list:
#     if dic1['permissions__group_id'] == 1:
#         dic[1]['urls'].append(dic1['permissions__url'])
#         dic[1]['actions'].append(dic1['permissions__action'])
#     else:
#         dic[2]['urls'].append(dic1['permissions__url'])
#         dic[2]['actions'].append(dic1['permissions__action'])
# print(dic)

# dic = {}
# for item in list:
#     # print(item,'++++')
#     if item['permissions__group_id'] in dic:
#         # print(item['permissions__group_id'],'****')
#         dic[item['permissions__group_id']]['urls'].append(item['permissions__url'])
#         dic[item['permissions__group_id']]['actions'].append(item['permissions__action'])
#     else:
#         dic[item['permissions__group_id']] = {'urls': [item['permissions__url'], ], 'actions': [item['permissions__action'], ]}
# print(dic)

# x = dict(a="1", b="2")
# print(x)
