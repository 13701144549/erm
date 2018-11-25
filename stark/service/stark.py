import copy
import json
from django.db.models import Q
from django.urls import reverse
from django.conf.urls import url
from django.forms.boundfield import BoundField
from django.forms.models import ModelChoiceField
from stark.utils.mypage import Pagination
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse, render, redirect
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField


class ShowList(object):  # 把需要显示的内容单独做一个类，可以避免下面的显示函数代码混乱
    def __init__(self, config, data_list, request):
        self.config = config  # ModelStark 的实例对象
        self.data_list = data_list  # 需要显示的数据列表
        self.request = request  # 当前访问页面的请求
        # 分页
        data_count = self.data_list.count()  # 需要显示数据的总数量
        current_page = int(self.request.GET.get('page', 1))  # 当前页码
        base_path = self.request.path  # 当前的路径
        params = self.request.GET  # GET 请求中的数据
        self.pagination = Pagination(current_page, data_count, base_path, params, per_page_num=10, pager_count=7)
        # 实例化分页对象
        self.page_data = self.data_list[self.pagination.start:self.pagination.end]  # 对每页显示的内容进行数据切片

        # actions
        self.actions = self.config.new_actions()  # 初始化 'actions' 属性，具体的 actions 列表是调用 new_actions() 函数所得

    def get_filter_linktags(self):  # 'filter' 方法，处理 'filter' 显示的问题
        link_dic = {}  # 建立一个空字典
        for filter_field in self.config.list_filter:  # 循环 'list_filter' 自定义的列表
            params = copy.deepcopy(self.request.GET)  # 对 self.request.GET 进行深copy
            cid = self.request.GET.get(filter_field, 0)  # 取出url中每一个 filter_field 后面对应的值
            filter_field_obj = self.config.model._meta.get_field(filter_field)
            # 根据自定义的字符串 filter_field 获得对应的对象属性（app01.Books.author，app01.Books.name ）
            if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                # 判断 filter_field_obj 对象是否是一对多或者是多对多，返回值的布尔值
                data_list = filter_field_obj.rel.to.objects.all()
                # 取出所有一对多或多对多关联的对象（<QuerySet [<Author: 大佬>, <Author: 郭靖>, <Author: 小明>]>）
            else:
                data_list = self.config.model.objects.all().values('pk', filter_field)
                # 取出所有一般字段的对应的所有对象，显示样式是values('pk', filter_field)
                # （<QuerySet [{'pk': 5, 'name': 'NBA日常'}, {'pk': 6, 'name': 'CBA日常'},
                # {'pk': 7, 'name': '篮球那些事'}, {'pk': 8, 'name': '足球那些事'}]>）
            temp = []
            # 处理  ‘全部’ 标签选项
            if params.get(filter_field):  # 如果能在 params 中得到 filter_field 这个键，说明 url 里已经有筛选条件的配置
                del params[filter_field]  # ‘全部’标签的作用是把同一键的值全部都清楚，所以就直接删除这个键
                temp.append("<a href='?%s'>全部</a>" % (params.urlencode(),))  # 拼接路径
            else:
                temp.append("<a class='active' href='#'>全部</a>")  # 否则就是 url 里没有筛选条件的配置，说明‘全部’标签已被选择，加一个被选择的样式
            # 处理 其他数据  标签
            for obj in data_list:  # 循环上面筛选出来的所有 数据对象
                if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                    # 处理其他标签，判断是不是关联字段
                    pk = obj.pk  # 如果是关联字段，则 pk 是 数据对象的 pk
                    text = str(obj)  # 如果是关联字段，则 text 是 数据对象的 str 值
                    params[filter_field] = pk  # 如果是关联字段，则 给 params 付一个 键值对 params[filter_field] = pk
                    # （<QueryDict: {'author': [7]}>）
                else:
                    pk = obj.get('pk')  # 普通字段，则 pk 是 数据对象里的键 pk
                    text = obj.get(filter_field)  # 普通字段，则 text 是 数据对象里的键 filter_field
                    params[filter_field] = text  # 普通字段，则 给 params 付一个 键值对 params[filter_field] = text
                    # （<QueryDict: {'name': ['NBA日常']}>）
                _url = params.urlencode()  # 把 params 编码成 url
                if cid == str(pk) or cid == text:  # 如果 url 中的 cid 等于 a 标签中这个对象的 pk 或者 text，则这个 a 标签是被选中的状态
                    link_tag = "<a class='active' href='?%s'>%s</a>" % (_url, text)
                else:
                    link_tag = "<a href='?%s'>%s</a>" % (_url, text)  # 否则就是没有被选中
                temp.append(link_tag)  # 把构建完的 a 标签添加到 temp 列表中
            link_dic[filter_field] = temp  # 每一个 filter_field 作为键，值是它对应的所有的 a 标签的列表，
            # （{'author': ["<a class='active' href='#'>全部</a>", "<a href='?author=7'>大佬</a>",
            # "<a href='?author=8'>郭靖</a>", "<a href='?author=9'>小明</a>"]}）
        return link_dic

    def get_action_list(self):  # 得到 'action' 列表的函数
        temp = []
        for action in self.actions:  # 循环 actions 列表
            temp.append({
                'name': action.__name__,
                'desc': action.short_description  # actions 列表中的函数对应的中文描述（ patch_init.short_description = '批量初始化'）
            })  # 键值对，actions 列表中的函数名是键，其对应的自定义中文名描述是值
        return temp

    def get_header(self):  # 得到表头信息的函数
        header_list = []
        for field in self.config.new_list_display():  # 循环 new_list_display 列表，field 是要显示的表头字段信息
            if callable(field):  # 如果 field 是可以被调用的，说明它不是一个普通的字段，而是一个函数方法
                val = field(self, header=True)  # 调用这个方法得到返回值
                header_list.append(val)  # 把这个返回值添加到 header_list 列表中
            else:
                if field == '__str__':  # 如果 field 是 '__str__' ，说明是默认的 list_display 列表
                    header_list.append(self.config.model._meta.model_name.upper())  # 需要显示的内容添加到 header_list 表中，显示大写的对象名
                else:
                    val = self.config.model._meta.get_field(field).verbose_name
                    # 如果是普通的字段，则得到它的对象对应的自定义 verbose_name 属性内容
                    header_list.append(val)
        return header_list

    def get_body(self):  # 得到表单数据信息函数
        new_data_list = []
        for obj in self.page_data:  # 循环分页后的数据
            temp = []
            for field in self.config.new_list_display():  # 循环 new_list_display 列表
                if callable(field):
                    val = field(self.config, obj)
                else:
                    try:
                        field_obj = self.config.model._meta.get_field(field)
                        if isinstance(field_obj, ManyToManyField):
                            ret = getattr(obj, field).all()
                            t = []
                            for mobj in ret:
                                t.append(str(mobj))
                            val = ','.join(t)
                        else:
                            if field_obj.choices:
                                val = getattr(obj, 'get_'+field+'_display')
                            else:
                                val = getattr(obj, field)
                            if field in self.config.list_display_links:
                                _url = self.config.get_change_url(obj)
                                val = mark_safe("<a href='%s'>%s</a>" % (_url, val))
                    except Exception as e:
                        val = getattr(obj, field)
                temp.append(val)
            new_data_list.append(temp)
        return new_data_list


class ModelStark(object):  # 自定义表格样式类
    list_display = ['__str__', ]  # 自定义默认的 list_display 表，默认的需要显示对象名，就使用 '__str__'，表格作用是现实的字段
    list_display_links = []  # 自定义默认的 list_display_links 表，为空，表格的作用是 把编辑列去掉，点击里面的字段名会进入编辑页面
    modelform_class = None  # 自定义一个model form的变量，如果注册时没有定义 model form 就用默认的
    search_fields = []
    actions = []
    list_filter = []

    def __init__(self, model, site):
        self.model = model
        self.site = site

    def edit(self, obj=None, header=False):
        if header:  # 判断是否是表头信息，如果是，那就自定义表头信息
            return '操作'
        _url = self.get_change_url(obj)
        return mark_safe("<a href='%s'>编辑</a>" % _url)  # 表单信息显示的内容

    def deletes(self, obj=None, header=False):
        if header:
            return '操作'
        _url = self.get_delete_url(obj)
        return mark_safe("<a href='%s'>删除</a>" % _url)

    def checkbox(self, obj=None, header=False):
        if header:
            return mark_safe('<input id="choice" type="checkbox">')
        return mark_safe('<input class="choice_item" type="checkbox" name="selected_pk" value="%s">' % obj.pk)

    def patch_delete(self, request, queryset):
        queryset.delete()

    patch_delete.short_description = '批量删除'

    def get_change_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_change" % (app_label, model_name), args=(obj.pk,))
        return _url

    def get_delete_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_delete" % (app_label, model_name), args=(obj.pk,))
        return _url

    def get_add_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_add" % (app_label, model_name))
        return _url

    def get_list_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_list" % (app_label, model_name))
        return _url

    def new_list_display(self):
        temp = []
        temp.append(ModelStark.checkbox)
        temp.extend(self.list_display)
        if not self.list_display_links:
            temp.append(ModelStark.edit)
        temp.append(ModelStark.deletes)
        return temp

    def new_actions(self):
        temp = []
        temp.append(ModelStark.patch_delete)
        temp.extend(self.actions)
        return temp

    def get_modelform_class(self):
        if not self.modelform_class:
            from django.forms import ModelForm
            from django.forms import widgets as wid
            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = '__all__'

            return ModelFormDemo
        else:
            return self.modelform_class

    def get_new_form(self, form):
        for bfield in form:
            if isinstance(bfield.field, ModelChoiceField):
                bfield.is_pop = True
                related_model_name = bfield.field.queryset.model._meta.model_name
                related_app_label = bfield.field.queryset.model._meta.app_label
                _url = reverse("%s_%s_add" % (related_app_label, related_model_name))
                bfield.url = _url + "?pop_res_id=id_%s" % bfield.name
        return form

    def add_view(self, request):
        ModelFormDemo = self.get_modelform_class()
        form = ModelFormDemo()
        state = True
        if request.method == 'POST':
            form = ModelFormDemo(request.POST)
            if form.is_valid():
                obj = form.save()
                pop_res_id = request.GET.get('pop_res_id')
                if pop_res_id:
                    res = {"pk": obj.pk, "text": str(obj), "pop_res_id": pop_res_id}
                    return render(request, 'pop.html', {"res": res})
                return redirect(self.get_list_url())
        form = self.get_new_form(form)
        return render(request, 'add&change_view.html', locals())

    def delete_view(self, request, id):
        url = self.get_list_url()
        if request.method == 'POST':
            self.model.objects.filter(pk=id).delete()
            return redirect(url)
        return render(request, 'delete_view.html', locals())

    def change_view(self, request, id):
        ModelFormDemo = self.get_modelform_class()
        edit_obj = self.model.objects.filter(pk=id).first()
        form = ModelFormDemo(instance=edit_obj)
        state = False
        if request.method == 'POST':
            form = ModelFormDemo(request.POST, instance=edit_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
        form = self.get_new_form(form)
        return render(request, 'add&change_view.html', locals())

    def get_search_condition(self, request):
        key_word = request.GET.get('q', '')
        self.key_word = key_word
        search_connection = Q()
        if key_word:
            search_connection.connector = 'or'
            for search_field in self.search_fields:
                search_connection.children.append((search_field + '__contains', key_word))
        return search_connection

    def get_filter_condition(self, request):
        filter_condition = Q()
        for filter_field, val in request.GET.items():
            if filter_field !="page":
                filter_condition.children.append((filter_field, val))
        return filter_condition

    def list_view(self, request):
        if request.method == 'POST':  # action 操作使用
            action = request.POST.get('action')
            selected_pk = request.POST.getlist('selected_pk')
            if selected_pk:
                action_func = getattr(self, action)
                queryset = self.model.objects.filter(pk__in=selected_pk)
                ret = action_func(request, queryset)
                # return ret
        # 获取search的Q对象
        search_connection = self.get_search_condition(request)
        # 获取filter的Q对象
        filter_condition = self.get_filter_condition(request)
        # 从数据库取数据
        data_list = self.model.objects.all().filter(search_connection).filter(filter_condition)
        # 展示数据（表头和表单）从ShowList类取出来
        show_list = ShowList(self, data_list, request)
        # 查看url
        add_url = self.get_add_url()
        return render(request, 'list_view.html', locals())

    def extra_url(self):
        return []

    def get_urls(self):
        temp = []
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        temp.append(url(r"^add/", self.add_view, name="%s_%s_add" % (app_label, model_name)))
        temp.append(url(r"^(\d+)/delete/", self.delete_view, name="%s_%s_delete" % (app_label, model_name)))
        temp.append(url(r"^(\d+)/change/", self.change_view, name="%s_%s_change" % (app_label, model_name)))
        temp.append(url(r"^$", self.list_view, name="%s_%s_list" % (app_label, model_name)))
        temp.extend(self.extra_url())
        return temp

    @property
    def urls(self):
        return self.get_urls(), None, None


class StarkSite(object):
    def __init__(self):
        self._registry = {}

    def register(self, model, stark_class=None):
        if not stark_class:
            stark_class = ModelStark
        self._registry[model] = stark_class(model, self)

    def main_list(self, request):
        dic = self.get_app_info()
        return render(request, 'main_list.html', locals())

    def app_list(self, request, app_name):
        app_name = app_name.upper()
        dic = self.get_app_info()
        for app in dic:
            if app == app_name:
                app_info = dic[app]
        return render(request, 'app_list.html', locals())

    def get_app_info(self):
        temp = []
        for model, stark_class_obj in self._registry.items():
            model_name = model._meta.model_name
            app_label = model._meta.app_label
            temp.append((app_label.upper(), model_name.capitalize()))
        dic = {}
        for item in temp:
            if item[0] in dic:
                dic[item[0]].append(item[1])
            else:
                dic[item[0]] = [item[1], ]
        return dic

    def get_urls(self):
        temp = []
        for model, stark_class_obj in self._registry.items():
            model_name = model._meta.model_name
            app_label = model._meta.app_label
            # 分发增删改查url
            temp.append(url(r"^%s/%s/" % (app_label, model_name), stark_class_obj.urls))
            temp.append(url(r"^$", self.main_list))  # 后台首页路径
            temp.append(url(r"^(?P<app_name>%s)/$" % (app_label,), self.app_list))  # 后台各APP首页路径
        return temp

    @property
    def urls(self):
        return self.get_urls(), None, None


site = StarkSite()
