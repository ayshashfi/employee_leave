from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile ,Department,LeaveRequest
from .forms import ProfileForm  ,ManagerForm,DepartmentForm,EmployeeForm,LeaveRequestForm
from .models import LeaveRequest, User, ManagerApproval
from django.db.models import Count,F,Sum
from django.utils import timezone


def index(request):
    return render(request, 'leave_app/index.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on user role
            if user.is_employee:
                return redirect('employee_dashboard')
            elif user.is_manager:
                return redirect('manager_dashboard')
            elif user.is_superuser:
                return redirect('admin_dashboard')
            else:
                messages.error(request, "User role not recognized.")
        else:
            print(f"Authentication failed for username: {username} and password: {password}")  # Debug line
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'leave_app/index.html')





TOTAL_LEAVES_ALLOWED = 20
@login_required
def employee_dashboard(request):
    # Get all approved leave requests for the logged-in user
    leave_requests = LeaveRequest.objects.filter(employee=request.user, status="Approved")

    # Calculate total leave days taken
    total_leave_taken = 0
    for request_obj in leave_requests:
        leave_duration = (request_obj.end_date - request_obj.start_date).days + 1  # Including start and end date
        total_leave_taken += leave_duration

    # Calculate remaining leaves
    remaining_leaves = TOTAL_LEAVES_ALLOWED - total_leave_taken

    return render(request, 'leave_app/employee_dashboard.html', {
        'remaining_leaves': remaining_leaves,
    })




from django.db.models import Sum, F, ExpressionWrapper, DurationField, IntegerField
from datetime import timedelta
from datetime import timedelta

@login_required
def manager_dashboard(request):
    # Get the logged-in manager
    manager = request.user

    # Get employees managed by the current manager
    employees = User.objects.filter(department=manager.department, is_employee=True)

    total_leaves_per_year = 20  # Total leaves allotted per year
    leave_data = []

    # Ensure the keys for leave types are consistent (e.g., all lowercase)
    leave_types = ['annual', 'sick', 'personal', 'maternity', 'paternity']

    for employee in employees:
        # Get all approved leave requests for the employee
        approved_leaves = LeaveRequest.objects.filter(employee=employee, status='Approved')

        # Calculate total approved leave days taken
        total_leaves_taken = sum(
            (request_obj.end_date - request_obj.start_date).days + 1 for request_obj in approved_leaves
        )

        # Calculate remaining leaves
        remaining_leaves = total_leaves_per_year - total_leaves_taken

        # Initialize leave counters for each leave type
        leave_summary = {leave_type: 0 for leave_type in leave_types}

        # Count the number of days for each type of leave
        for leave in approved_leaves:
            leave_days = (leave.end_date - leave.start_date).days + 1  # Include both start and end dates
            # Use lowercase for comparison and dictionary key access
            leave_summary[leave.leave_type.lower()] += leave_days

        # Append the data for each employee
        leave_data.append({
            'employee': employee,
            'total_leaves_taken': total_leaves_taken,
            'remaining_leaves': remaining_leaves,
            'leave_summary': leave_summary,
        })

    # Context to be passed to the template
    context = {
        'leave_data': leave_data,
        'user': request.user,
    }
    return render(request, 'leave_app/manager_dashboard.html', context)

def admin_dashboard(request):
    # Get today's date
    today = timezone.now().date()

    # Get employees who have approved leave requests for today
    employees_with_leaves = []

    # Filter users who are employees and not managers
    user_info = User.objects.filter(is_employee=True, is_manager=False).prefetch_related('leaverequest_set')

    for user in user_info:
        # Check for approved leave requests for today
        approved_leaves = user.leaverequest_set.filter(
            status='Approved',
            start_date__lte=today,
            end_date__gte=today
        )
        if approved_leaves.exists():
            # Append user and their approved leaves
            employees_with_leaves.append({
                'user': user,
                'approved_leaves': approved_leaves
            })

    context = {
        'employees_with_leaves': employees_with_leaves,
    }

    return render(request, 'leave_app/admin_dashboard.html', context)





def profile_view(request):
    profile = request.user.profile  # Assuming the user is authenticated
    return render(request, 'leave_app/profile.html', {'profile': profile})




def employee_profile(request, employee_id):
    # Fetch the employee by ID
    employee = get_object_or_404(User, id=employee_id)
    
    context = {
        'employee': employee,
    }

    return render(request, 'leave_app/employee_profile.html', context)




def manager_profile(request, manager_id):
    manager = get_object_or_404(User, id=manager_id, is_manager=True)  # Adjust according to your model setup
    context = {
        'manager': manager,
    }
    return render(request, 'leave_app/manager_profile.html', context)




@login_required
def update_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)  # Fetch the profile by ID

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)  # Bind the form with the profile instance and handle file uploads
        email = request.POST.get('email')  # Get the email separately

        # Validate and save the form data
        if profile_form.is_valid():
            profile_form.save()  # Save the profile data
            profile.user.email = email  # Update the user's email
            profile.user.save()  # Save the user data
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')  # Redirect to the appropriate dashboard
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        profile_form = ProfileForm(instance=profile)  # Pre-fill the form with existing data

    context = {
        'profile_form': profile_form,
        'profile': profile
    }
    return render(request, 'profile.html', context)  # Render the editing template




def create_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department_name = form.cleaned_data['name']
            # Check if the department already exists
            if Department.objects.filter(name=department_name).exists():
                messages.error(request, "Department already exists!")  # Flash error message
            else:
                form.save()  # Save the new department
                messages.success(request, "Department created successfully!")  # Flash success message
                return redirect('create_department')  # Adjust this as needed
    else:
        form = DepartmentForm()

    # Fetch all existing departments to display
    departments = Department.objects.all()
    
    return render(request, 'leave_app/create_department.html', {'form': form, 'departments': departments})




def create_employee(request):
    employees = User.objects.filter(is_employee=True)
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee created successfully!')
            return redirect('create_employee')
    else:
        form = EmployeeForm()
    context = {
        'form': form,  # Assuming you have your form for creating an employee here
        'employees': employees,
    }
    return render(request, 'leave_app/create_employee.html', context)




def create_manager(request):
    managers = User.objects.filter(is_manager=True)  # Adjust this filter according to your User model setup
    if request.method == 'POST':
        form = ManagerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manager created successfully!')
            return redirect('create_manager')  # Redirect to create manager or another page
    else:
        form = ManagerForm()

    context = {
        'form': form,  # Assuming you have your form for creating a manager here
        'managers': managers,
    }
    return render(request, 'leave_app/create_manager.html', context)



@login_required
def manage_departments(request):
    departments = Department.objects.all()
    return render(request, 'leave_app/manage_departments.html', {'departments': departments})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LeaveRequest
from .forms import LeaveRequestForm

@login_required
def submit_leave_request(request):
    # Replace this logic with the actual logic to fetch remaining leaves for the logged-in user
    remaining_leaves = 10  # Example static value; this should be dynamic for each user
    leave_limit_exceeded = False
    selected_leave_days = 0

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Calculate the number of leave days
            selected_leave_days = (end_date - start_date).days + 1  # Add +1 to include both start and end date

            # Check if the leave limit is exceeded
            if selected_leave_days > remaining_leaves:
                leave_limit_exceeded = True
                messages.error(request, "The selected leave duration exceeds your remaining leaves.")
            else:
                # Save the leave application if everything is valid
                leave_application = form.save(commit=False)
                leave_application.employee = request.user  # Assign logged-in user as employee
                leave_application.save()

                messages.success(request, "Leave application submitted successfully.")
                return redirect('employee_dashboard')  # Redirect after successful submission
        else:
            messages.error(request, "There were errors in your form submission.")

    else:
        form = LeaveRequestForm()  # Initialize an empty form for GET requests

    context = {
        'form': form,
        'remaining_leaves': remaining_leaves,
        'leave_limit_exceeded': leave_limit_exceeded,
        'selected_leave_days': selected_leave_days,
    }
    return render(request, 'leave_app/submit_leave_application.html', context)



@login_required
def leave_request_list(request):
    # Get all leave requests for the logged-in employee
    leave_requests = LeaveRequest.objects.filter(employee=request.user)

    # Add a leave count to each request
    for request_obj in leave_requests:
        leave_duration = (request_obj.end_date - request_obj.start_date).days + 1  # Including start and end date
        request_obj.leave_duration = leave_duration

    return render(request, 'leave_app/leave_request_list.html', {
        'leave_requests': leave_requests,
    })



@login_required
def delete_leave_request(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id, employee=request.user)
    leave_request.delete()
    messages.success(request, 'Leave request deleted successfully!')
    return redirect('leave_request_list')  # Redirect to the leave request list view




@login_required
def manager_leave_request_list(request):
    # Get leave requests for the manager's department
    leave_requests = LeaveRequest.objects.filter(employee__department=request.user.department)
    return render(request, 'leave_app/manager_leave_request_list.html', {'leave_requests': leave_requests})




@login_required
def approve_leave_request(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    
    # Check if the leave request is from the same department
    if leave_request.employee.department == request.user.department:
        manager_approval, created = ManagerApproval.objects.get_or_create(leave=leave_request, manager=request.user)
        manager_approval.approve_leave()  # Call the method to approve the leave
        messages.success(request, 'Leave request approved successfully.')
    else:
        messages.error(request, 'You are not authorized to approve this request.')

    return redirect('manager_leave_request_list')  # Redirect back to the list



@login_required
def reject_leave_request(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    
    # Check if the leave request is from the same department
    if leave_request.employee.department == request.user.department:
        manager_approval, created = ManagerApproval.objects.get_or_create(leave=leave_request, manager=request.user)
        manager_approval.reject_leave()  # Call the method to reject the leave
        messages.success(request, 'Leave request rejected successfully.')
    else:
        messages.error(request, 'You are not authorized to reject this request.')

    return redirect('manager_leave_request_list')  # Redirect back to the list




def logout_view(request):
    logout(request)
    return redirect('login')
