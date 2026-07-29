from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Program, ProgramApplication
from core.notifications import notify_admin


def program_list(request):
    programs = Program.objects.filter(is_active=True)
    return render(request, 'programs/list.html', {'programs': programs})


def program_detail(request, slug):
    program = get_object_or_404(Program, slug=slug, is_active=True)
    related_programs = Program.objects.filter(is_active=True).exclude(slug=slug)[:3]
    return render(request, 'programs/detail.html', {
        'program': program,
        'related_programs': related_programs,
    })


@login_required
def apply_program(request, slug):
    program = get_object_or_404(Program, slug=slug, is_active=True)

    # Check if already applied
    existing = ProgramApplication.objects.filter(program=program, applicant=request.user).first()
    if existing:
        messages.info(request, f"You have already applied for '{program.title}'. Status: {existing.get_status_display()}")
        return redirect('program_detail', slug=slug)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        age = request.POST.get('age', '').strip()
        reason = request.POST.get('reason', '').strip()
        additional_info = request.POST.get('additional_info', '').strip()

        if not full_name or not phone_number or not reason:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'programs/apply.html', {'program': program})

        application = ProgramApplication.objects.create(
            program=program,
            applicant=request.user,
            full_name=full_name,
            phone_number=phone_number,
            age=int(age) if age.isdigit() else None,
            reason=reason,
            additional_info=additional_info,
        )

        # Notify Admin in-app & Email
        notify_admin(
            notification_type='application',
            title=f"New Program Application: {program.title} — {full_name}",
            message=f"Program: {program.title}\nApplicant: {full_name}\nPhone: {phone_number}\nAge: {age}\nReason: {reason}",
            link=f"/admin/programs/programapplication/{application.id}/change/"
        )

        messages.success(request, f"Your application for '{program.title}' has been submitted! Our team will review it and reach out to you via phone shortly.")
        return redirect('my_applications')

    return render(request, 'programs/apply.html', {'program': program})


@login_required
def my_applications(request):
    applications = ProgramApplication.objects.filter(applicant=request.user).order_by('-submitted_at')
    return render(request, 'programs/my_applications.html', {'applications': applications})
