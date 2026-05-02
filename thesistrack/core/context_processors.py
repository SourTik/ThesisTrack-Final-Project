from notifications.models import Notification


def unread_notifications_count(request):
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {'unread_notifications_count': count}


def recent_notifications(request):
    if not request.user.is_authenticated:
        return {'recent_notifications': []}

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    return {'recent_notifications': notifications}