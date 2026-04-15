from django.shortcuts import render

from accounts.models import User
from core.decorators import role_required


@role_required(User.STUDENT, User.SUPERVISOR, User.ADMIN)
def layout_preview(request):
    return render(request, 'core/layout_preview.html')
