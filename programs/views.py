from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Program, ProgramApplication


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

        # ─── Send Email Notification to Admins ───────────────────────────────
        try:
            subject = f"[HRC] New Application: {program.title} — {full_name}"
            message_body = f"""
A new program application has been submitted at Hope Reception Centre.

═══════════════════════════════════════
PROGRAM:        {program.title}
═══════════════════════════════════════
Applicant Name: {full_name}
Username:       {request.user.username}
Phone:          {phone_number}
Age:            {age if age else 'Not provided'}
Submitted:      {application.submitted_at.strftime('%d %B %Y at %H:%M EAT')}

REASON FOR APPLICATION:
{reason}

ADDITIONAL INFORMATION:
{additional_info if additional_info else 'None provided'}

═══════════════════════════════════════
To review this application, log in to the admin console:
https://hopereceptioncenter.org/admin/programs/programapplication/
Or visit your Admin Dashboard:
https://hopereceptioncenter.org/dashboard/stats/
═══════════════════════════════════════
This is an automated notification from Hope Reception Centre Web System.
"""
            send_mail(
                subject=subject,
                message=message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.ADMIN_NOTIFICATION_EMAILS,
                fail_silently=True,
            )
        except Exception as e:
            # Don't crash if email fails — just log it
            print(f"[EMAIL ERROR] Failed to send notification: {e}")

        messages.success(request, f"Your application for '{program.title}' has been submitted! Our team will review it and reach out to you via phone shortly.")
        return redirect('my_applications')

    return render(request, 'programs/apply.html', {'program': program})


@login_required
def my_applications(request):
    applications = ProgramApplication.objects.filter(applicant=request.user).order_by('-submitted_at')
    return render(request, 'programs/my_applications.html', {'applications': applications})
