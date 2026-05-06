from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.patient_register_view, name='patient_register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('staff/', views.staff_list_view, name='staff_list'),
    path('staff/add/', views.staff_create_view, name='staff_create'),
    path('staff/<int:pk>/edit/', views.staff_update_view, name='staff_update'),
    path('staff/<int:pk>/delete/', views.staff_delete_view, name='staff_delete'),
]
