"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from bookclub import views
from bookclub.views import account_views, authentication_views, dashboard_views, club_related_views, book_views, club_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.landing_page, name='landing_page'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('home/', dashboard_views.home_page , name = 'home'),
    path('users/', account_views.user_list , name = 'user_list'),
    path('clubs/', club_views.club_list , name = 'club_list'),
    path('books/', book_views.book_list , name = 'book_list'),
    path('password/', account_views.PasswordView.as_view(), name='password'),
    path('profile/', account_views.ProfileUpdateView.as_view(), name='profile'),
    path('applications/', club_related_views.ApplicationsView.as_view(), name='applications'),
    path('applications/accept/<int:pk>/', club_related_views.app_accept, name='app_accept'),
    path('applications/remove/<int:pk>/', club_related_views.app_remove, name='app_remove'),
    path('new_club/', club_views.new_club, name='new_club'),
    path('club_profile/<int:club_id>/', club_views.club_profile, name='club_profile')

]
