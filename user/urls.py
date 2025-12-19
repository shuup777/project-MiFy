from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Pages
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('library/', views.library_view, name='library'),
    
   
]