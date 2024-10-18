from django import forms
from .models import Profile,Department, LeaveRequest, ManagerApproval,User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'date_of_birth', 'profile_picture']  # Include 'profile_picture'

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Example validation (length, format, etc.)
        if len(phone_number) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits long.")
        return phone_number
    
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']  # Assuming 'name' is the only field
    

class ManagerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'department']
        widgets = {
            'password': forms.PasswordInput(),  # Render password as a password field
            'department': forms.Select(),  # This will create a dropdown for departments
        }

    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
        return user


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'department']
        widgets = {
            'password': forms.PasswordInput(),  # Password input widget
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        user.is_employee = True  # Set the employee flag
        if commit:
            user.save()
        return user



# forms.py
from django import forms
from .models import LeaveRequest

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter reason for leave'}),
        }

