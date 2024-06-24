from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('medialist/', views.media_list, name='media_list'),
    path('upload/', views.upload_media, name='upload_media'),
    path('delete/<int:pk>/', views.delete_media, name='delete_media'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
]
