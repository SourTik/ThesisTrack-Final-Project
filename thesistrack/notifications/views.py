from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from core.decorators import role_required
from .models import Notification


@role_required(User.STUDENT, User.SUPERVISOR, User.ADMIN)
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})


@role_required(User.STUDENT, User.SUPERVISOR, User.ADMIN)
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return redirect('notifications:list')
