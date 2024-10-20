from django.urls import path
from .views import index,login_view,employee_dashboard,admin_dashboard,manager_dashboard,logout_view,profile_view,update_profile,create_manager,create_department,create_employee,submit_leave_request,leave_request_list ,delete_leave_request,manager_leave_request_list,approve_leave_request,reject_leave_request,employee_profile,manager_profile

urlpatterns = [
    path('index/', index, name='index'),  # Home page with login form
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'), 
    path('employee_dashboard/', employee_dashboard, name='employee_dashboard'),
    path('manager_dashboard/', manager_dashboard, name='manager_dashboard'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),  
    path('profile/', profile_view, name='profile'),  
    path('profile/update/<int:profile_id>/', update_profile, name='update_profile'),
    path('create-department/', create_department, name='create_department'),
    path('create_manager/', create_manager, name='create_manager'),
    path('create_employee/', create_employee, name='create_employee'),  
    path('submit_leave/', submit_leave_request, name='submit_leave_application'),
    path('leave-requests/', leave_request_list, name='leave_request_list'),  
    path('leave-requests/delete/<int:leave_request_id>/', delete_leave_request, name='delete_leave_request'),
    path('manager-leave-requests/', manager_leave_request_list, name='manager_leave_request_list'),
    path('approve-leave/<int:leave_request_id>/', approve_leave_request, name='approve_leave_request'),
    path('reject-leave/<int:leave_request_id>/', reject_leave_request, name='reject_leave_request'),
    path('employee/<int:employee_id>/', employee_profile, name='employee_profile'),
    path('manager/<int:manager_id>/', manager_profile, name='manager_profile'),
]
