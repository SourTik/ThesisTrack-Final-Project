from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def layout_preview(request):
	return render(request, 'core/layout_preview.html')
