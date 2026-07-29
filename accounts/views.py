from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from programs.models import ProgramApplication
from counseling.models import CounselingSession


def register_view(request):
    if request.method == 'POST':
        u_name = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('confirm_password')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=u_name).exists():
            messages.error(request, "Username already taken! Please choose another.")
            return render(request, 'accounts/register.html')

        if email and User.objects.filter(email=email).exists():
            messages.error(request, "An account with that email already exists.")
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=u_name,
            password=pass1,
            email=email,
            phone_number=phone,
        )
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f"Welcome to Hope Reception Centre, {user.username}! Your account has been created.")
        next_url = request.GET.get('next', 'home')
        return redirect(next_url)

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        u_name = request.POST.get('username', '').strip()
        pass1 = request.POST.get('password')
        user = authenticate(request, username=u_name, password=pass1)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def profile_view(request):
    sessions = CounselingSession.objects.filter(client=request.user).order_by('-created_at')[:5]
    applications = ProgramApplication.objects.filter(applicant=request.user).order_by('-submitted_at')[:5]
    return render(request, 'accounts/profile.html', {
        'sessions': sessions,
        'applications': applications,
    })
