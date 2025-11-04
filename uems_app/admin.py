from django.contrib import admin
from .models import Organizer, Venue, Event, Ticket, Attendee, User

# Register your models here.

@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'phone')
    search_fields = ('name', 'contact_email')

@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'date_joined')
    list_filter = ('username', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'date_joined')

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')
    search_fields = ('name', 'address')

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


class AttendeeInline(admin.TabularInline):
    model = Attendee
    extra = 0
    readonly_fields = ('full_name', 'email', 'created_at')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'from_date', 'to_date', 'archived', 'is_public')
    list_filter = ('from_date', 'organizer', 'archived', 'is_public')
    search_fields = ('title', 'description')
    inlines = [TicketInline, AttendeeInline]

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'quantity')
    search_fields = ('name', 'event__title')

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'event', 'checked_in', 'created_at')
    list_filter = ('checked_in', 'event')
    search_fields = ('full_name', 'email', 'event__title')
    readonly_fields = ('created_at',)

# admin.site.site_header = "UEMS Administration"
# admin.site.site_title = "University Events Management System"
# admin.site.index_title = "Manage Events, Organizers, and Attendees"