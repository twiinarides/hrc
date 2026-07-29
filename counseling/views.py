from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import CounselingSession, AnonymousSupportThread, AnonymousMessage


@login_required
def book_session(request):
    if request.method == 'POST':
        session_type = request.POST.get('session_type')
        date_str = request.POST.get('preferred_date')
        notes = request.POST.get('notes', '')

        session = CounselingSession.objects.create(
            client=request.user,
            session_type=session_type,
            preferred_date=date_str,
            notes=notes
        )

        # ─── Admin Email Notification ─────────────────────────────────────────
        try:
            type_display = dict(CounselingSession.SESSION_TYPES).get(session_type, session_type)
            subject = f"[HRC] New Counseling Request — {request.user.username} ({type_display})"
            message_body = f"""
A new counseling session has been booked at Hope Reception Centre.

═══════════════════════════════════════
COUNSELING SESSION REQUEST
═══════════════════════════════════════
Client Username:  {request.user.username}
Session Type:     {type_display}
Preferred Date:   {date_str}
Submitted:        {session.created_at.strftime('%d %B %Y at %H:%M EAT')}

NOTES / REASON:
{notes if notes else 'No additional notes provided.'}

═══════════════════════════════════════
To manage this session, log in to the admin console:
https://hopereceptioncenter.org/admin/counseling/counselingsession/
Or visit your Admin Dashboard:
https://hopereceptioncenter.org/dashboard/stats/
═══════════════════════════════════════
This is an automated notification from the Hope Reception Centre Web System.
"""
            send_mail(
                subject=subject,
                message=message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.ADMIN_NOTIFICATION_EMAILS,
                fail_silently=True,
            )
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send session notification: {e}")

        messages.success(request, "Your counseling session request has been submitted! Our team will get in touch with you shortly.")
        return redirect('my_sessions')

    return render(request, 'counseling/book.html')


@login_required
def my_sessions(request):
    sessions = CounselingSession.objects.filter(client=request.user).order_by('-preferred_date')
    return render(request, 'counseling/my_sessions.html', {'sessions': sessions})


def anonymous_chat(request):
    token = request.GET.get('token')
    thread = None
    if token:
        thread = AnonymousSupportThread.objects.filter(token=token).first()

    if request.method == 'POST':
        content = request.POST.get('content')
        category = request.POST.get('category', 'General Support')

        if not thread:
            thread = AnonymousSupportThread.objects.create(category=category)

        AnonymousMessage.objects.create(
            thread=thread,
            sender_is_counselor=False,
            content=content
        )

        # Notify admins of new anonymous message
        try:
            send_mail(
                subject=f"[HRC] New Anonymous Support Message — Thread {str(thread.token)[:8]}",
                message=f"A new anonymous support message has been submitted.\n\nCategory: {category}\nThread Token: {thread.token}\nMessage: {content}\n\nRespond at: https://hopereceptioncenter.org/admin/counseling/anonymoussupportthread/",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.ADMIN_NOTIFICATION_EMAILS,
                fail_silently=True,
            )
        except Exception:
            pass

        return redirect(f"/counseling/anonymous/?token={thread.token}")

    messages_list = thread.messages.order_by('timestamp') if thread else []
    return render(request, 'counseling/anonymous.html', {'thread': thread, 'messages_list': messages_list})
