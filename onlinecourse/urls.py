from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    # Route for course index
    path('', views.CourseListView.as_view(), name='index'),
    # Route for registration, login, logout
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    # Route for course details
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),
    
    # --- ADD/VERIFY THESE TWO ROUTES BELOW ---
    path('<int:course_id>/submit/', views.submit, name='submit'),
    path('course/<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name='exam_result'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)