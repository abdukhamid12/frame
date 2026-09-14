from django.contrib import admin
from .models import Movie, Genre, Rating, Watchlist
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title','year','featured','published']
    list_filter = ['published','featured','genres','year']
    search_fields = ['title','director']
    prepopulated_fields = {'slug':('title',)}
    filter_horizontal = ['genres']
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
admin.site.register(Rating)
admin.site.register(Watchlist)
admin.site.site_header = 'FRAME · Studio'
