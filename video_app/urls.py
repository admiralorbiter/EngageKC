from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('upload/<int:session_pk>/', views.upload_media, name='upload_media'),  # Ensure session_id is included
    path('delete/<int:pk>/', views.delete_media, name='delete_media'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('start-session/', views.start_session, name='start_session'),
    path('join-session/', views.join_session, name='join_session'),
    path('session/<int:pk>/', views.session_detail, name='session_detail'),
    path('join-session/<str:session_code>/', views.join_session, name='join_session'),  # Update to accept session code
    path('login/', views.login, name='login')
]
