from django.urls import path

from .views import layout_preview

app_name = 'core'

urlpatterns = [
    path('layout-preview/', layout_preview, name='layout-preview'),
]