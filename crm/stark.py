from stark.service.stark import site, ModelStark
from .models import *
from django.forms import ModelForm
from django.forms import widgets as wid
from django.shortcuts import HttpResponse, render, redirect
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.db.models import Q
import datetime
from django.http import JsonResponse


class UserModelForm(ModelForm):
    class Meta:
        model = UserInfo
        fields = '__all__'
        widgets = {
            'password': wid.PasswordInput
        }
        error_messages = {
            'name': {'required': '员工姓名不能为空',},
            'username': {'required': '用户名不能为空',},
            'password': {'required': '用户密码不能为空',},
            'email': {'required': '用户邮箱不能为空',},
            'depart': {'required': '部门不能为空',},
        }


class UserConfig(ModelStark):
    list_display = ['name', 'email', 'depart']
    modelform_class = UserModelForm


class ClassModelForm(ModelForm):
    class Meta:
        model = ClassList
        fields = '__all__'
        widgets = {
            'start_date': wid.TextInput(attrs={
                'type': 'date'
            }),
            'graduate_date': wid.TextInput(attrs={
                'type': 'date'
            })
        }
        error_messages = {
            'school': {'required': '校区不能为空',},
            'course': {'required': '课程名称不能为空',},
            'semester': {'required': '班级（期）不能为空',},
            'price': {'required': '学费不能为空',},
            'start_date': {'required': '开班日期不能为空',},
            'teachers': {'required': '任课老师不能为空',},
            'tutor': {'required': '班主任不能为空',},
        }


class ClassConfig(ModelStark):
    def display_class_name(self, obj=None, header=False):
        if header:
            return '班级名称'
        class_name = "{0}（{1}）".format(obj.course.name, str(obj.semester))
        return class_name

    list_display = [display_class_name, 'tutor', 'teachers', 'price', 'school']
    modelform_class = ClassModelForm


class CusotmerModelForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'recv_date': wid.TextInput(attrs={
                'type': 'date'
            }),
            'last_consult_date': wid.TextInput(attrs={
                'type': 'date'
            })
        }
        error_messages = {
            'name': {'required': '学生姓名不能为空',},
            'qq': {'required': '学生qq不能为空',},
            'gender': {'required': '学生性别不能为空',},
            'course': {'required': '咨询课程不能为空',},
            'status': {'required': '客户状态不能为空',},
            'consultant': {'required': '课程顾问不能为空',},
            'recv_date': {'required': '当前课程顾问的接单日期不能为空',},
            'last_consult_date': {'required': '最后跟进日期不能为空',},
        }


class CusotmerConfig(ModelStark):
    def display_gender(self, obj=None, header=False):
        if header:
            return '性别'
        return obj.get_gender_display()
        # Django提供的方法，提取gender_choices = ((1, '男'), (2, '女'))中的'男'和'女'，方法命名结构是 "get_字段名_display()"

    def display_course(self, obj=None, header=False):
        if header:
            return '咨询课程'
        temp = []
        for course in obj.course.all():
            s = "<a href='/stark/crm/customer/cancel_course/%s/%s' style='border:1px solid #369;padding:3px 6px'><span>%s</span></a>&nbsp;" \
                % (obj.pk, course.pk, course.name)
            temp.append(s)

        return mark_safe("".join(temp))

    list_display = ['name', display_gender, 'qq', display_course, 'consultant']
    modelform_class = CusotmerModelForm

    def cancel_course(self, request, customer_id, course_id):
        obj = Customer.objects.filter(pk=customer_id).first()
        obj.course.remove(course_id)
        return redirect(self.get_list_url())

    def public_customer(self, request):
        now = datetime.datetime.now()
        delta_day3 = datetime.timedelta(days=3)
        delta_day15 = datetime.timedelta(days=15)
        user_id = 1
        customer_list = Customer.objects.filter(
            Q(last_consult_date__lt=now - delta_day3) | Q(recv_date__lt=now - delta_day15), status=2).exclude(
            consultant=user_id)
        return render(request, 'public.html', locals())

    def further(self, request, customer_id):
        user_id = 3
        now = datetime.datetime.now()
        delta_day3 = datetime.timedelta(days=3)
        delta_day15 = datetime.timedelta(days=15)
        ret = Customer.objects.filter(pk=customer_id).filter(
            Q(last_consult_date__lt=now - delta_day3) | Q(recv_date__lt=now - delta_day15), status=2).update(
            consultant=user_id, last_consult_date=now, recv_date=now)
        if not ret:
            return HttpResponse('已经被跟进了')
        CustomerDistrbute.objects.create(customer_id=customer_id, consultant_id=user_id, date=now, status=1)
        return HttpResponse('跟进成功')

    def mycustomer(self, request):
        user_id = 1
        customer_distrbute_list = CustomerDistrbute.objects.filter(consultant=user_id)
        return render(request, 'mycustomer.html', locals())

    def extra_url(self):
        temp = []
        temp.append(url(r"cancel_course/(\d+)/(\d+)", self.cancel_course))
        temp.append(url(r"public/", self.public_customer))
        temp.append(url(r"further/(\d+)", self.further))
        temp.append(url(r"mycustomer/", self.mycustomer))
        return temp


class DepartmentModelForm(ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
        error_messages = {
            'title': {'required': '部门名称不能为空',},
            'code': {'required': '部门编号不能为空',},
        }


class DepartmentConfig(ModelStark):
    list_display = ['title', 'code']
    modelform_class = DepartmentModelForm


class CourseModelForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        error_messages = {
            'name': {'required': '课程名称不能为空',},
        }


class CourseConfig(ModelStark):
    list_display = ['name']
    modelform_class = CourseModelForm


class SchoolModelForm(ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        error_messages = {
            'title': {'required': '校区名称不能为空',},
        }


class SchoolConfig(ModelStark):
    list_display = ['title']
    modelform_class = SchoolModelForm


class StudentModelForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'date': wid.TextInput(attrs={
                'type': 'date'
            }),
            'password': wid.PasswordInput
        }
        error_messages = {
            'customer': {'required': '客户信息不能为空',},
            'username': {'required': '用户名不能为空',},
            'password': {'required': '密码不能为空',},
        }


class StudentConfig(ModelStark):
    def score_view(self, request, sid):
        student = Student.objects.filter(pk=sid).first()
        class_list = student.class_list.all()
        data = {'data_list': [], 'name': student.customer.name}
        if request.is_ajax():
            sid = request.GET.get('sid')
            cid = request.GET.get('cid')
            study_record_list = StudyRecord.objects.filter(student=sid, course_record__class_obj=cid)
            for study_record in study_record_list:
                day_num = study_record.course_record.day_num
                data['data_list'].append(['day%s' % day_num, study_record.score])
            return JsonResponse(data)

        return render(request, 'score_view.html', locals())

    def extra_url(self):
        temp = []
        temp.append(url(r"score_view/(\d+)", self.score_view))
        return temp

    def score_show(self, obj=None, header=False):
        if header:
            return '查看成绩'
        return mark_safe("<a href='/stark/crm/student/score_view/%s'>查看成绩</a>" % obj.pk)

    list_display = ['customer', 'class_list', score_show]
    modelform_class = StudentModelForm


class CourseRecordModelForm(ModelForm):
    class Meta:
        model = CourseRecord
        fields = '__all__'
        error_messages = {
            'class_obj': {'required': '班级不能为空',},
            'day_num': {'required': '节次不能为空',},
            'teacher': {'required': '讲师不能为空',},
        }


class CourseRecordConfig(ModelStark):
    modelform_class = CourseRecordModelForm

    def score(self, request, course_record_id):
        study_record_list = StudyRecord.objects.filter(course_record=course_record_id)
        score_choices = StudyRecord.score_choices
        if request.method == 'POST':
            data = {}
            for key, value in request.POST.items():
                if key == 'csrfmiddlewaretoken':
                    continue
                field, pk = key.rsplit('_', 1)
                if pk in data:
                    data[pk][field] = value
                else:
                    data[pk] = {field: value}
            for pk, update_data in data.items():
                StudyRecord.objects.filter(pk=pk).update(**update_data)
            return redirect(request.path)
        return render(request, "score.html", locals())

    def extra_url(self):
        temp = []
        temp.append(url(r"record_score/(\d+)", self.score))
        return temp

    def record(self, obj=None, header=False):
        if header:
            return "学习记录"
        return mark_safe("<a href='/stark/crm/studyrecord/?course_record=%s'>记录</a>" % obj.pk)

    def record_score(self, obj=None, header=False):
        if header:
            return "录入成绩"
        return mark_safe("<a href='record_score/%s'>录入</a>" % obj.pk)

    list_display = ['class_obj', 'day_num', 'teacher', 'date', record, record_score]

    def patch_studyrecord(self, request, queryset):
        temp = []
        for course_record in queryset:
            student_list = Student.objects.filter(class_list__id=course_record.class_obj.pk)
            for student in student_list:
                obj = StudyRecord(student=student, course_record=course_record)
                temp.append(obj)
        StudyRecord.objects.bulk_create(temp)

    patch_studyrecord.short_description = '批量生成学习记录'
    actions = [patch_studyrecord, ]


class StudyRecordModelForm(ModelForm):
    class Meta:
        model = StudyRecord
        fields = '__all__'
        error_messages = {
            'course_record': {'required': '第几天课程不能为空',},
            'student': {'required': '学员不能为空',},
        }


class StudyRecordConfig(ModelStark):
    list_display = ['course_record', 'student', 'record', 'score']
    modelform_class = StudyRecordModelForm

    def patch_late(self, request, queryset):
        queryset.update(record='late')

    patch_late.short_description = '迟到'

    def patch_vacate(self, request, queryset):
        queryset.update(record='vacate')

    patch_vacate.short_description = '请假'

    def patch_noshow(self, request, queryset):
        queryset.update(record='noshow')

    patch_noshow.short_description = '缺勤'

    def patch_leave_early(self, request, queryset):
        queryset.update(record='leave_early')

    patch_leave_early.short_description = '早退'

    actions = [patch_late, patch_vacate, patch_noshow, patch_leave_early]


class ConsultRecordModelForm(ModelForm):
    class Meta:
        model = ConsultRecord
        fields = '__all__'
        error_messages = {
            'customer': {'required': '所咨询客户不能为空',},
            'consultant': {'required': '跟踪人不能为空',},
            'note': {'required': '跟踪内容不能为空',},
        }


class ConsultRecordConfig(ModelStark):
    list_display = ['customer', 'consultant', 'date']
    modelform_class = ConsultRecordModelForm


site.register(Customer, CusotmerConfig)
site.register(Department, DepartmentConfig)
site.register(UserInfo, UserConfig)
site.register(Course, CourseConfig)
site.register(ConsultRecord, ConsultRecordConfig)
site.register(CourseRecord, CourseRecordConfig)
site.register(StudyRecord, StudyRecordConfig)
site.register(Student, StudentConfig)
site.register(School, SchoolConfig)
site.register(ClassList, ClassConfig)
site.register(CustomerDistrbute)
