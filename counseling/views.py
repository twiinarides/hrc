from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CounselingSession, AnonymousSupportThread, AnonymousMessage
from core.notifications import notify_admin


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

        type_display = dict(CounselingSession.SESSION_TYPES).get(session_type, session_type)

        # Notify Admin in-app and via Email
        notify_admin(
            notification_type='session',
            title=f"New Counseling Session Request — {request.user.username}",
            message=f"Client: {request.user.username}\nSession Type: {type_display}\nPreferred Date: {date_str}\nNotes: {notes}",
            link=f"/admin/counseling/counselingsession/{session.id}/change/"
        )

        messages.success(request, "Your counseling session request has been submitted! Our team will get in touch with you shortly.")
        return redirect('my_sessions')

    return render(request, 'counseling/book.html')


@login_required
def my_sessions(request):
    sessions = CounselingSession.objects.filter(client=request.user).order_by('-preferred_date')
    return render(request, 'counseling/my_sessions.html', {'sessions': sessions})


def anonymous_chat(request):
    token = request.GET.get('token', '').strip().upper()
    search_error = None
    thread = None

    if token:
        # Search exact or case-insensitive prefix match
        thread = AnonymousSupportThread.objects.filter(token__iexact=token).first()
        if not thread:
            # Try searching by token containing or stripped
            thread = AnonymousSupportThread.objects.filter(token__icontains=token).first()

        if not thread:
            search_error = f"No anonymous thread found matching token '{token}'. Please check your token and try again."

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        category = request.POST.get('category', 'General Support')

        if not thread:
            thread = AnonymousSupportThread.objects.create(category=category)

        if content:
            AnonymousMessage.objects.create(
                thread=thread,
                sender_is_counselor=False,
                content=content
            )

            # Notify Admin in-app & Email
            notify_admin(
                notification_type='anonymous',
                title=f"New Anonymous Support Message (Token: {thread.token})",
                message=f"Category: {category}\nToken: {thread.token}\nMessage: {content}",
                link=f"/admin/counseling/anonymoussupportthread/{thread.id}/change/"
            )

        return redirect(f"/counseling/anonymous/?token={thread.token}")

    messages_list = thread.messages.order_by('timestamp') if thread else []
    return render(request, 'counseling/anonymous.html', {
        'thread': thread,
        'messages_list': messages_list,
        'search_error': search_error,
        'search_token': token,
    })
