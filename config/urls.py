from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cinema import views, cabinet
urlpatterns = [path('admin/',admin.site.urls),path('accounts/',include('django.contrib.auth.urls')),path('accounts/signup/',views.signup,name='signup'),path('',views.home,name='home'),path('browse/',views.browse,name='browse'),path('my-list/',views.watchlist,name='watchlist'),path('movie/<slug:slug>/',views.detail,name='detail'),path('movie/<slug:slug>/save/',views.save_movie,name='save_movie'),path('movie/<slug:slug>/rate/',views.rate_movie,name='rate_movie')]
urlpatterns += [
    path('account/', cabinet.account, name='account'),
    path('account/studio/', cabinet.studio, name='studio'),
    path('account/studio/movies/new/', cabinet.movie_edit, name='movie_create'),
    path('account/studio/movies/<int:pk>/', cabinet.movie_edit, name='movie_edit'),
    path('account/studio/genres/new/', cabinet.genre_edit, name='genre_create'),
    path('account/studio/genres/<int:pk>/', cabinet.genre_edit, name='genre_edit'),
    path('account/studio/<str:kind>/<int:pk>/delete/', cabinet.delete_item, name='studio_delete'),
    path('account/studio/members/<int:pk>/role/', cabinet.member_role, name='member_role'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
