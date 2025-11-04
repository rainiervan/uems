from django.urls import path
from . import views

urlpatterns = [
    # Dashboard (root)
    path('', views.dashboard_view, name='dashboard'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),

    # Management (for admins)
    path('management/', views.management_view, name='management'),

    # Events CRUD
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),

    # Attendee registration
    path('events/<int:pk>/register/', views.register_for_event, name='event_register'),
]