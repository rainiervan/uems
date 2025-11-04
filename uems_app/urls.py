from django.urls import path
from . import views

urlpatterns = [
    # path('', views.main, name='main'),
    path('', views.dashboard_view, name='dashboard'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),

    # Management
    path('management/', views.management_view, name="management"),

    # Users
    path('management/users/', views.users_view, name="users"),
    path('management/users/create/', views.create_user_view, name="user_create"),
    path('management/users/edit/<int:pk>', views.edit_user_view, name="user_edit"),
    path('management/users/delete/<int:pk>', views.delete_user, name="user_delete"),

    # Organizers
    path('management/organizers/', views.organizers_view, name="organizers"),
    path('management/organizers/create', views.create_organizer_view, name="organizer_create"),
    path('management/organizers/edit/<int:pk>', views.edit_organizer_view, name="organizer_edit"),
    path('management/organizers/delete/<int:pk>', views.delete_organizer, name="organizer_delete"),

    # Tickets
    path('management/tickets/', views.tickets_view, name="tickets"),
    path('management/tickets/create', views.create_ticket_view, name="ticket_create"),
    path('management/tickets/edit/<int:pk>', views.edit_ticket_view, name="ticket_edit"),
    path('management/tickets/delete/<int:pk>', views.delete_ticket, name="ticket_delete"),

    # Venues
    path('management/venues/', views.venues_view, name="venues"),
    path('management/venues/create', views.create_venue_view, name="venue_create"),
    path('management/venues/edit/<int:pk>', views.edit_venue_view, name="venue_edit"),
    path('management/venues/delete/<int:pk>', views.delete_venue, name="venue_delete"),

    # Events CRUD
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),

    # Attendee registration
    path('events/<int:pk>/register/', views.register_for_event, name='event_register'),
]