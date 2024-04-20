
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path("following_posts", views.following_posts, name="following_posts"),
    path("edit/<int:id>", views.edit, name="edit"),
    path('toggle_likes/<int:pid>', views.toggle_likes, name='toggle_likes'),
    path('get_like_count/<int:pid>', views.get_like_count, name='get_like_count'),
]
