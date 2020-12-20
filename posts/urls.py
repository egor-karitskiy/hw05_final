from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.index,
         name='index'),
    path('follow/',
         views.follow_index,
         name='follow_index'),
    path('<str:username>/follow',
         views.profile_follow,
         name='profile_follow'),
    path('<str:username>/unfollow',
         views.profile_unfollow,
         name='profile_unfollow'),
    path('group/<slug:slug>/',
         views.group_posts,
         name='group_slug'),
    path('new/',
         views.new_post,
         name='new_post'),
    path('<str:username>/',
         views.profile,
         name='profile'),
    path('<str:username>/<int:post_id>/',
         views.post_view,
         name='post'),
    path(
        '<str:username>/<int:post_id>/edit/',
        views.post_edit,
        name='post_edit'
        ),
    path('<str:username>/<int:post_id>/comment',
         views.add_comment,
         name="add_comment"),
    path('api/v1/posts/',
         views.api_posts,
         name='api_posts'),
    path('api/v1/posts/<int:post_id>/',
         views.api_posts_detail,
         name='api_posts_detail'),
    path('api/v2/posts/',
         views.APIPost.as_view(),
         name='class_api_posts'),
    path('api/v2/posts/<int:id>/',
         views.APIPostDetail.as_view(),
         name='class_api_posts_detail')
                ]
