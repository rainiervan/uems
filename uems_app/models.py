from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.conf import settings
from datetime import datetime

User = settings.AUTH_USER_MODEL

class User(AbstractUser):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('attendee', 'Attendee'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')

    def is_superadmin(self):
        return self.role == 'superadmin'

    def is_admin(self):
        return self.role == 'admin'

    def is_organizer(self):
        return self.role == 'organizer'

    def is_attendee(self):
        return self.role == 'attendee'

class Organizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organizer_profile')
    name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.name

class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail = models.FileField(upload_to='event_thumbnails/', null=True, blank=True)
    from_date = models.DateTimeField(default=datetime.now)
    to_date = models.DateTimeField(default=datetime.now)
    archived = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-from_date']

    def __str__(self):
        return f"{self.title} — {self.from_date.date()}"

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[self.pk])

    @property
    def spots_left(self):
        if self.max_attendees is None:
            return None
        booked = self.attendees.count()
        return max(self.max_attendees - booked, 0)
    
class Ticket(models.Model):
    event = models.ForeignKey(Event, related_name='tickets', on_delete=models.CASCADE)
    name = models.CharField(max_length=120, default='General Admission')
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} — {self.event.title}"
    
class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey(Event, related_name='attendees', on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    checked_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'event')

    def __str__(self):
        return f"{self.full_name} — {self.event.title}"