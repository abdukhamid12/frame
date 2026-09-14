from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Avg, Count, Q
from .models import Movie, Genre, Rating, Watchlist

def catalog():
    return Movie.objects.filter(published=True).prefetch_related('genres').annotate(average=Avg('ratings__score'),votes=Count('ratings'))

def home(request):
    movies = catalog()
    return render(request,'home.html',{'hero':movies.filter(featured=True).first() or movies.first(),'movies':movies[:12],'picks':movies.order_by('-year')[:6],'genres':Genre.objects.all(),'page':'home'})

def browse(request):
    movies = catalog()
    query = request.GET.get('q','').strip()
    genre = request.GET.get('genre','')
    sort = request.GET.get('sort','newest')
    if query: movies = movies.filter(Q(title__icontains=query)|Q(director__icontains=query)|Q(cast__icontains=query))
    if genre: movies = movies.filter(genres__slug=genre)
    movies = movies.order_by({'rating':'-average','title':'title','newest':'-year'}.get(sort,'-year'))
    return render(request,'browse.html',{'movies':movies,'genres':Genre.objects.all(),'query':query,'selected_genre':genre,'sort':sort,'heading':'Find your next obsession','page':'browse'})

def detail(request,slug):
    movie = get_object_or_404(catalog(),slug=slug)
    saved = request.user.is_authenticated and Watchlist.objects.filter(user=request.user,movie=movie).exists()
    rating = Rating.objects.filter(user=request.user,movie=movie).first() if request.user.is_authenticated else None
    related = catalog().filter(genres__in=movie.genres.all()).exclude(pk=movie.pk).distinct()[:6]
    return render(request,'detail.html',{'movie':movie,'saved':saved,'rating':rating,'related':related,'scores':range(1,11)})

@login_required
def watchlist(request):
    return render(request,'browse.html',{'movies':catalog().filter(saved_by__user=request.user),'heading':'Your next movie night','is_watchlist':True,'page':'watchlist'})

@login_required
@require_POST
def save_movie(request,slug):
    movie = get_object_or_404(Movie,slug=slug,published=True)
    item,created = Watchlist.objects.get_or_create(user=request.user,movie=movie)
    if not created: item.delete()
    messages.success(request,'Added to your list.' if created else 'Removed from your list.')
    return redirect('detail',slug=slug)

@login_required
@require_POST
def rate_movie(request,slug):
    movie = get_object_or_404(Movie,slug=slug,published=True)
    try: score = int(request.POST.get('score',''))
    except (ValueError,TypeError): score = 0
    if 1 <= score <= 10:
        Rating.objects.update_or_create(user=request.user,movie=movie,defaults={'score':score})
        messages.success(request,'Your rating has been saved.')
    else: messages.error(request,'Choose a rating between 1 and 10.')
    return redirect('detail',slug=slug)

def signup(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request,form.save())
        return redirect('home')
    return render(request,'registration/signup.html',{'form':form})
