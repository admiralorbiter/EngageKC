from django.urls import path, include
from . import views
from .media_views import upload_media, delete_media, edit_media, like_media  # Updated imports
from .session_views import start_session, session, pause_session, delete_session, generate_users_for_section  # New imports
from .auth_views import login, student_login, student_logout, AdminLoginView, update_teacher_info  # New imports
from django.contrib import admin
from .student_management_views import download_students, delete_student, student_detail

urlpatterns = [
    path('download-students/', download_students, name='download_students'),
    path('edit-media/<int:pk>/', edit_media, name='edit_media'),  # Updated view reference
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('upload/<int:session_pk>/', upload_media, name='upload_media'),  # Updated view reference
    path('delete-media/<int:pk>/', delete_media, name='delete_media'),  # Updated view reference
    path('accounts/', include('django.contrib.auth.urls')),
    path('start-session/', start_session, name='start_session'),  # Updated view reference
    path('student-login/', student_login, name='student_login'),  # Updated view reference
    path('session/<int:session_pk>/', session, name='session'),  # Updated view reference
    path('join-session/<str:session_code>/', student_login, name='student_login'),  # Updated view reference
    path('login/', login, name='login'),  # Updated view reference
    path('like/<int:media_id>/', like_media, name='like_media'),  # Updated view reference
    path('session/<int:session_pk>/delete/', delete_session, name='delete_session'),  # Updated view reference
    path('session/<int:session_pk>/pause/', pause_session, name='pause_session'),  # Updated view reference
    path('post/<int:id>/', views.post, name='post'),
    path('teacher_view/', views.teacher_view, name='teacher_view'),
    path('delete-student/<int:student_id>/', delete_student, name='delete_student'),
    path('generate-students/', generate_users_for_section, name='generate_students'),
    path('like-media/<int:media_id>/<str:like_type>/', like_media, name='like_media'),  # Updated view reference
    path('filter_media/<int:session_pk>/', views.filter_media, name='filter_media'),
    path('set-media-password/', views.set_media_password, name='set_media_password'),
    path('edit-media/<int:pk>/', edit_media, name='edit_media'),  # Updated view reference
    path('student-logout/', student_logout, name='student_logout'),  # Updated view reference
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('update_teacher_info/', update_teacher_info, name='update_teacher_info'),  # Updated view reference
    path('student/<int:student_id>/', student_detail, name='student_detail'),
]