from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):
	notifications = Notification.objects.filter(user=request.user)
	return render(request, 'notifications/notification_list.html', {'notifications': notifications})


@login_required
def mark_as_read(request, notification_id):
	notification = get_object_or_404(Notification, id=notification_id, user=request.user)
	notification.is_read = True
	notification.save(update_fields=['is_read'])
	return redirect('notifications:list')
