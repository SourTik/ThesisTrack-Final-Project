from django.urls import path

from .views import ThesisTrackLoginView, ThesisTrackLogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', ThesisTrackLoginView.as_view(), name='login'),
    path('logout/', ThesisTrackLogoutView.as_view(), name='logout'),
]