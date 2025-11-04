from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.views.decorators.cache import never_cache
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .forms import RegisterForm, LoginForm, EventForm, AttendeeForm, UserCreateForm, TicketForm, VenueForm, OrganizerForm
from .models import Event, Attendee, Organizer, Ticket, Venue

User = get_user_model()

# ---------- Role Checking ----------
def is_admin(user):
    return user.is_authenticated and user.role in ['superadmin', 'admin']

def is_organizer(user):
    return user.is_authenticated and user.role == 'organizer'

def is_attendee(user):
    return user.is_authenticated and user.role == 'attendee'

# ---------- Authentication ----------

@never_cache
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    elif request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm()
    return render(request, "auth/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")

def register_view(request):
    if request.method == "POST":
        try:
            User.objects.get(email=request.POST.get("email"))
            messages.error(request, "This email has already been registered.")
        except ObjectDoesNotExist:
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, "Registration successful!")
                return redirect("dashboard_view")
            else:
                messages.error(request, "Please correct the errors below.")
    elif request.user.is_authenticated:
        return redirect("dashboard_view")

    form = RegisterForm()
    return render(request, "auth/register.html", {"form": form})

# ---------- Dashboard ----------

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    now = timezone.now().date()

    # ---- SUPERADMIN / ADMIN DASHBOARD ----
    if is_admin(user):
        total_events = Event.objects.count()
        ongoing_events = Event.objects.filter(from_date__lte=now, to_date__gte=now, archived=False).count()
        archived_events = Event.objects.filter(archived=True).count()

        context = {
            'role': 'Admin',
            'total_events': total_events,
            'ongoing_events': ongoing_events,
            'archived_events': archived_events,
        }
        return render(request, 'dashboard/dash_admin.html', context)

    # ---- ORGANIZER DASHBOARD ----
    elif is_organizer(user):
        organizer_events = Event.objects.filter(organizer__user=user)
        upcoming_events = organizer_events.filter(from_date__gte=timezone.now()).order_by('from_date')

        context = {
            'role': 'Organizer',
            'organizer_events': organizer_events,
            'upcoming_events': upcoming_events,
        }
        return render(request, 'dashboard/dash_organizer.html', context)

    # ---- ATTENDEE / USER DASHBOARD ----
    else:
        upcoming_events = Event.objects.filter(from_date__gte=timezone.now()).order_by('from_date')[:6]
        registered_events = Attendee.objects.filter(user=user).select_related('event')

        context = {
            'role': 'Attendee',
            'upcoming_events': upcoming_events,
            'registered_events': registered_events,
        }
        return render(request, 'dashboard/dash_user.html', context)

# ---------- Profile Management ----------

def profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in first.")
        return redirect("login")

    pwChange = PasswordChangeForm(request.user)

    if request.method == 'POST':
        change_type = request.POST.get("type")

        if change_type == "password_change":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                messages.info(request, "Password updated successfully. Please log in again.")
                logout(request)
                return redirect("login")
            else:
                messages.error(request, "Password update failed. Check fields and try again.")

        elif change_type == "email_change":
            old_email = request.POST.get("old_email")
            new_email = request.POST.get("new_email")
            if old_email == request.user.email:
                if not User.objects.filter(email=new_email).exists():
                    request.user.email = new_email
                    request.user.save()
                    messages.success(request, "Email updated successfully.")
                else:
                    messages.error(request, "Email already in use.")
            else:
                messages.error(request, "Old email mismatch.")

        elif change_type == "basic_change":
            username = request.POST.get("username")
            if User.objects.filter(username=username).exclude(id=request.user.id).exists():
                messages.error(request, "Username already in use.")
            else:
                user = request.user
                user.username = username
                user.first_name = request.POST.get("first_name")
                user.last_name = request.POST.get("last_name")
                user.save()
                messages.success(request, "Profile updated successfully.")

        return redirect("profile")

    context = {"password_form": pwChange}
    if is_admin(request.user):
        context["users"] = User.objects.all()
        context["events"] = Event.objects.all()

    return render(request, "profile/index.html", context)

def management_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("dashboard")
        else:
            users = User.objects.all()
            events = Event.objects.all()
            organizers = Organizer.objects.all()
            tickets = Ticket.objects.all()
            venues = Venue.objects.all()

            context = {
                "users": users,
                "events": events,
                "organizers": organizers,
                "tickets": tickets,
                "venues": venues
            }

            return render(request, "management/index.html", context)

def users_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("login")
        else:
            users = User.objects.all()

            return render(request, "management/users/index.html", {"users": users})

def create_user_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("event_list")
        else:
            if request.method == "POST":
                form = UserCreateForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    user.password = make_password("Userpw@123") # default password for accounts created through this form
                    user.save()

                    return redirect("users")
                else:
                    messages.error(request, "Unable to add new user. Please ensure you filled all the details correctly.")
    
    form = UserCreateForm()        
    return render(request, "management/users/create.html", {"form": form})

def edit_user_view(request, pk):
    user = get_object_or_404(User, id=pk)

    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("event_list")
        else:
            if request.method == "POST":
                form = UserCreateForm(request.POST, instance=user)
                if form.is_valid():
                    form.save()

                    return redirect("users")
                else:
                    messages.error(request, "Unable to add new user. Please ensure you filled all the details correctly.")
    
    form = UserCreateForm(instance=user)
    return render(request, "management/users/edit.html", {"form": form})

def delete_user(request, pk):
    if not request.user.is_superuser or not request.user.is_staff:
        return redirect("event_list")
    else:
        if request.method == "GET":
            user = get_object_or_404(User, id=pk)

            user.delete()
    
    return redirect("users")

def organizers_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("login")
        else:
            organizers = Organizer.objects.all()

            return render(request, "management/organizers/index.html", {"organizers": organizers})

def create_organizer_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("event_list")
        else:
            if request.method == "POST":
                form = OrganizerForm(request.POST)
                if form.is_valid():
                    form.save()

                    return redirect("organizers")
                else:
                    messages.error(request, "Unable to add new organizer. Please ensure you filled all the details correctly.")
    
    form = OrganizerForm()        
    return render(request, "management/organizers/create.html", {"form": form})

def edit_organizer_view(request, pk):
    organizer = get_object_or_404(Organizer, id=pk)

    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("event_list")
        else:
            if request.method == "POST":
                form = OrganizerForm(request.POST, instance=organizer)
                if form.is_valid():
                    form.save()

                    return redirect("organizers")
                else:
                    messages.error(request, "Unable to add new organizer. Please ensure you filled all the details correctly.")
    
    form = OrganizerForm(instance=organizer)
    return render(request, "management/organizers/edit.html", {"form": form})

def delete_organizer(request, pk):
    if not request.user.is_superuser or not request.user.is_staff:
        return redirect("event_list")
    else:
        if request.method == "GET":
            organizer = get_object_or_404(Organizer, id=pk)

            organizer.delete()
    
    return redirect("organizers")

def tickets_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("login")
        else:
            tickets = Ticket.objects.all()

            return render(request, "management/tickets/index.html", {"tickets": tickets})

def create_ticket_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("event_list")
        else:
            if request.method == "POST":
                form = TicketForm(request.POST)
                if form.is_valid():
                    form.save()

                    return redirect("tickets")
                else:
                    messages.error(request, "Unable to add new ticket. Please ensure you filled all the details correctly.")
    
    form = TicketForm()        
    return render(request, "management/tickets/create.html", {"form": form})

def edit_ticket_view(request, pk):
    ticket = get_object_or_404(Ticket, id=pk)

    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("event_list")
        else:
            if request.method == "POST":
                form = TicketForm(request.POST, instance=ticket)
                if form.is_valid():
                    form.save()

                    return redirect("tickets")
                else:
                    messages.error(request, "Unable to add new ticket. Please ensure you filled all the details correctly.")
    
    form = TicketForm(instance=ticket)
    return render(request, "management/tickets/edit.html", {"form": form})

def delete_ticket(request, pk):
    if not request.user.is_superuser or not request.user.is_staff:
        return redirect("event_list")
    else:
        if request.method == "GET":
            ticket = get_object_or_404(Ticket, id=pk)

            ticket.delete()
    
    return redirect("tickets")

def venues_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("login")
        else:
            venues = Venue.objects.all()

            return render(request, "management/venues/index.html", {"venues": venues})

def create_venue_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("event_list")
        else:
            if request.method == "POST":
                form = VenueForm(request.POST)
                if form.is_valid():
                    form.save()

                    return redirect("venues")
                else:
                    messages.error(request, "Unable to add new venue. Please ensure you filled all the details correctly.")
    
    form = VenueForm()        
    return render(request, "management/venues/create.html", {"form": form})

def edit_venue_view(request, pk):
    venue = get_object_or_404(Venue, id=pk)

    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect("event_list")
        else:
            if request.method == "POST":
                form = VenueForm(request.POST, instance=venue)
                if form.is_valid():
                    form.save()

                    return redirect("venues")
                else:
                    messages.error(request, "Unable to add new venue. Please ensure you filled all the details correctly.")
    
    form = VenueForm(instance=venue)
    return render(request, "management/venues/edit.html", {"form": form})

def delete_venue(request, pk):
    if not request.user.is_superuser or not request.user.is_staff:
        return redirect("event_list")
    else:
        if request.method == "GET":
            venue = get_object_or_404(Venue, id=pk)

            venue.delete()
    
    return redirect("venues")


# ---------- Event Management ----------

class EventListView(ListView):
    model = Event
    template_name = 'events/index.html'
    context_object_name = 'events'
    paginate_by = 12


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/view.html'
    context_object_name = 'event'

def register_for_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = AttendeeForm(request.POST)
        if form.is_valid():
            attendee = form.save(commit=False)
            attendee.event = event
            if request.user.is_authenticated:
                attendee.user = request.user
            attendee.save()
            messages.success(request, "You have successfully registered for the event!")
            return redirect(event.get_absolute_url())
    else:
        form = AttendeeForm()
    return render(request, 'events/register.html', {'form': form, 'event': event})

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/create.html'
    success_url = reverse_lazy('event_list')

    def dispatch(self, request, *args, **kwargs):
        if not (is_admin(request.user) or is_organizer(request.user)):
            messages.error(request, "You are not authorized to create events.")
            return redirect('event_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if is_organizer(self.request.user):
            form.instance.organizer = self.request.user.organizer_profile
        return super().form_valid(form)

class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/update.html'
    success_url = reverse_lazy('event_list')

    def dispatch(self, request, *args, **kwargs):
        if not (is_admin(request.user) or is_organizer(request.user)):
            messages.error(request, "You are not authorized to edit events.")
            return redirect('event_list')
        return super().dispatch(request, *args, **kwargs)

class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/delete.html'
    success_url = reverse_lazy('event_list')

    def dispatch(self, request, *args, **kwargs):
        if not (is_admin(request.user) or is_organizer(request.user)):
            messages.error(request, "You are not authorized to delete events.")
            return redirect('event_list')
        return super().dispatch(request, *args, **kwargs)
    
# ---------- Management View ----------
def management_view(request):
    return render(request, 'management/index.html')