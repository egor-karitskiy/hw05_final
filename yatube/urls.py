from django.urls import path, include
from django.contrib import admin
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as fwv
from django.contrib.flatpages import views as fpv

handler404 = 'posts.views.page_not_found' # noqa
handler500 = 'posts.views.server_error' # noqa

urlpatterns = [

    path('api/v1/api-token-auth/', fwv.obtain_auth_token),
    path('admin/',
         admin.site.urls),
    path('',
         include('posts.urls')
         ),
    path('about/',
         include('django.contrib.flatpages.urls')
         ),
    path('auth/',
         include('users.urls')
         ),
    path('auth/',
         include("django.contrib.auth.urls"),
         name='auth'
         ),


]

urlpatterns += [
    path('about-us/',
         fpv.flatpage,
         {'url': '/about-us/'},
         name='about'),
    path('terms/',
         fpv.flatpage,
         {'url': '/terms/'},
         name='terms'),
]

urlpatterns += [
    path('api-token-auth/', fwv.obtain_auth_token)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)