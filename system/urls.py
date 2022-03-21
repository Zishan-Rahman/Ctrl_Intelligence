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
from bookclub.views import account_views, authentication_views, dashboard_views, book_views, club_views, user_views, search_views, application_views, meeting_views, messaging_views  , feed_views , post_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="main/password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='main/password/password_reset_complete.html'), name='password_reset_complete'),
    path("password_reset", account_views.password_reset_request, name="password_reset"),
    path('', account_views.landing_page, name='landing_page'),
    path('users/', user_views.UsersListView.as_view() , name = 'user_list'),
    path('clubs/', club_views.ClubsListView.as_view() , name = 'club_list'),
    path('books/', book_views.BooksListView.as_view() , name = 'book_list'),
    path('sign_up/', authentication_views.sign_up, name='sign_up'),
    path('login/', authentication_views.LogInView.as_view(), name='login'),
    path('log_out/', authentication_views.log_out, name='log_out'),
    path('home/', dashboard_views.home_page, name='home'),
    path('password/', account_views.PasswordView.as_view(), name='password'),
    path('profile/', account_views.user_profile, name='profile'),
    path('profile/edit/', user_views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('applications/', application_views.ApplicationsView.as_view(), name='applications'),
    path('applications/accept/<int:pk>/', application_views.app_accept, name='app_accept'),
    path('applications/remove/<int:pk>/', application_views.app_remove, name='app_remove'),
    path('new_application/<int:club_id>/', application_views.new_application, name='new_application'),
    path('club_profile/<int:club_id>/', club_views.club_profile, name='club_profile'),
    path('club_profile/<int:club_id>/members', club_views.ClubMemberListView.as_view(), name='club_members'),
    path('club_profile/<int:club_id>/meetings', meeting_views.ClubMeetingsListView.as_view(), name='club_meetings'),
    path('user_profile/<int:user_id>/', user_views.user_profile, name='user_profile'),
    path('book_profile/<int:book_id>/', book_views.ShowBookView.as_view(), name='book_profile'),
    path('my_clubs/', club_views.club_selector, name='club_selector'),
    path('my_clubs1/', club_views.club_selector_alt, name="club_selector_alt"),
    path('my_applications/', application_views.MyApplicationsView.as_view(), name='my_applications'),
    path('new_club/', club_views.new_club, name='new_club'),
    path('club_profile/<int:pk>/meeting/', meeting_views.MeetingScheduler.as_view(), name='schedule_meeting'),
    path('search/', search_views.search, name='search_page'),
    path('leave_club/<int:club_id>/', club_views.leave_club, name='leave_club'),
    path('inbox/', messaging_views.ListChatsView.as_view(), name='inbox'),
    path('inbox/create_chat', messaging_views.CreateChatView.as_view(), name='create_chat'),
    path('inbox/<int:pk>/', messaging_views.ChatView.as_view(), name='chat'),
    path('inbox/<int:pk>/create_message/', messaging_views.CreateMessageView.as_view(), name='create_message'),
    path('club_profile/<int:c_pk>/members/<int:u_pk>/promote', club_views.promote_member_to_organiser, name='promote_member_to_organiser'),
    path('club_profile/<int:c_pk>/members/<int:u_pk>/demote', club_views.demote_organiser_to_member, name='demote_organiser_to_member'),
    path('club_profile/<int:c_pk>/members/<int:u_pk>/kick', club_views.kick_user_from_club, name='kick_user_from_club'),
    path('club_profile/<int:c_pk>/members/<int:u_pk>/transfer', club_views.transfer_ownership, name='transfer_ownership'),
    path('club_profile/<int:c_pk>/edit/', club_views.ClubUpdateView.as_view(), name='edit_club'),
    path('favourites/', book_views.Favourites.as_view(), name='favourites'),
    path('book_profile/<int:book_id>/favourite', book_views.make_favourite, name="make_favourite"),
    path('book_profile/<int:book_id>/unfavourite', book_views.Unfavourite, name="Unfavourite"),
    path('book_profile/<int:book_id>/rating', book_views.update_ratings, name="update_ratings"),
    path('club_profile/<int:c_pk>/disband', club_views.disband_club, name='disband_club'),
    path('club_profile/<int:club_id>/feed/', feed_views.FeedView.as_view(), name='feed'),
    path('follow_toggle/<int:user_id>', user_views.follow_toggle , name = 'follow_toggle'),
    path('club_profile/<int:club_id>/new_post/', post_views.NewPostView.as_view(), name='new_post'),
]
