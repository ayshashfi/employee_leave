from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password
    department = models.ForeignKey('Department', on_delete=models.CASCADE, null=True)  # Assuming a manager is associated with one department
    is_employee = models.BooleanField(default=False)  # Default should be False
    is_manager = models.BooleanField(default=False)   # Default should be False

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='leave_app_users',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='leave_app_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username
    
    # def set_password(self, raw_password):
    #     self.password = make_password(raw_password)

    # def save(self, *args, **kwargs):
    #     if not self.pk:  # Only hash password when creating a new user
    #         self.set_password(self.password)
    #     super().save(*args, **kwargs)  # Call the parent class's save method


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL here
    phone_number = models.CharField(max_length=15, null=True)
    address = models.TextField(null=True)
    date_of_birth = models.DateField(null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)  # Profile picture field

    def __str__(self):
        return self.user.username


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference to the employee
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Approved, Rejected

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} from {self.start_date} to {self.end_date}"

    @property
    def duration(self):
        return (self.end_date - self.start_date).days

    def clean(self):
        # Validate that the end date is after the start date
        if self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")
        # You can add more validations here (e.g., leave balance)


class ManagerApproval(models.Model):
    leave = models.OneToOneField(LeaveRequest, on_delete=models.CASCADE)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL here
    approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manager.username} - {self.leave.employee.username} - Approved: {self.approved}"

    def approve_leave(self):
        """Method to approve leave and update the leave request status."""
        self.approved = True
        self.leave.status = 'Approved'
        self.leave.save()
        self.save()

    def reject_leave(self):
        """Method to reject leave and update the leave request status."""
        self.approved = False
        self.leave.status = 'Rejected'
        self.leave.save()
        self.save()
