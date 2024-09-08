from django.urls import path, include
from . import views
from django.contrib import admin

urlpatterns = [
    path('edit-media/<int:pk>/', views.edit_media, name='edit_media'),
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('upload/<int:session_pk>/', views.upload_media, name='upload_media'),  # Ensure session_id is included
    path('delete/<int:session_pk>/', views.delete_media, name='delete_media'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('start-session/', views.start_session, name='start_session'),
    path('join-session/', views.join_session, name='join_session'),
    path('session/<int:session_pk>/', views.session_detail, name='session_detail'),
    path('join-session/<str:session_code>/', views.join_session, name='join_session'),  # Update to accept session code
    path('login/', views.login, name='login'),
    path('like/<int:media_id>/', views.like_media, name='like_media'),
    path('session/<int:session_pk>/delete/', views.delete_session, name='delete_session'),  # Add this line
    path('session/<int:session_pk>/pause/', views.pause_session, name='pause_session'),   
    path('post/<int:id>/', views.post_detail, name='post_detail'),
    path('admin_view/', views.admin_view, name='admin_view'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('download-students/', views.download_students, name='download_students'),
    path('generate-students/', views.generate_students, name='generate_students'),
    path('like-media/<int:media_id>/<str:like_type>/', views.like_media, name='like_media'),
    path('filter_media/<int:session_pk>/', views.filter_media, name='filter_media'),
    path('set-media-password/', views.set_media_password, name='set_media_password'),
    path('edit-media/<int:pk>/', views.edit_media, name='edit_media'),
    path('student-logout/', views.student_logout, name='student_logout'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]