
from django.contrib import admin
from .models import User, LeaveRequest, ManagerApproval, Department,Profile

admin.site.register(User)
admin.site.register(LeaveRequest)
admin.site.register(ManagerApproval)
admin.site.register(Department)
admin.site.register(Profile)
