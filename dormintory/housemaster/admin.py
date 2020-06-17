from django.contrib import admin

# Register your models here.
from housemaster.models import *
admin.site.register(Verification)
admin.site.register(Dor)
admin.site.register(User)
admin.site.register(Stu)
admin.site.register(Change_dor)
admin.site.register(Fix_dor)
admin.site.register(Notice)
