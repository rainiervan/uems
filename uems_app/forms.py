from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Event, Attendee
from datetime import datetime

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]

class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ["old_password", "new_password1", "new_password2"]

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'organizer',
            'title',
            'description',
            'venue',
            'thumbnail',
            'from_date',
            'to_date',
            'max_attendees',
            'is_public'
        ]
        widgets = {
            'from_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'to_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['full_name', 'email', 'ticket']