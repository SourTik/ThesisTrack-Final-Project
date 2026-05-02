from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from core.decorators import role_required

from .models import Notification


@role_required(User.STUDENT, User.SUPERVISOR, User.ADMIN)
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)

    filter_state = request.GET.get('state', 'all')
    category_filter = request.GET.get('category', 'all')

    if filter_state == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_state == 'read':
        notifications = notifications.filter(is_read=True)

    if category_filter != 'all':
        notifications = notifications.filter(category=category_filter)

    notification_total = Notification.objects.filter(user=request.user).count()
    unread_total = Notification.objects.filter(user=request.user, is_read=False).count()
    read_total = notification_total - unread_total

    return render(
        request,
        'notifications/notification_list.html',
        {
            'notifications': notifications,
            'filter_state': filter_state,
            'category_filter': category_filter,
            'filter_categories': Notification.CATEGORY_CHOICES,
            'notification_total': notification_total,
            'unread_total': unread_total,
            'read_total': read_total,
        },
    )


@role_required(User.STUDENT, User.SUPERVISOR, User.ADMIN)
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return redirect('notifications:list')


@role_required(User.STUDENT, User.SUPERVISOR, User.ADMIN)
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:list')
