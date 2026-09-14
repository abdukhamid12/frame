from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Movie, Genre, Rating, Watchlist
from .forms import MovieForm, GenreForm

def editor_required(view):
    @login_required
    @wraps(view)
    def wrapped(request,*args,**kwargs):
        if not request.user.is_staff: raise PermissionDenied
        return view(request,*args,**kwargs)
    return wrapped

def require_permission(request,action,model):
    if not request.user.has_perm(f'cinema.{action}_{model}'): raise PermissionDenied

@login_required
def account(request):
    return render(request,'cabinet/account.html',{'saved_count':Watchlist.objects.filter(user=request.user).count(),'rating_count':Rating.objects.filter(user=request.user).count(),'page':'account'})

@editor_required
def studio(request):
    return render(request,'cabinet/studio.html',{'movies':Movie.objects.all() if request.user.has_perm('cinema.view_movie') else Movie.objects.none(),'genres':Genre.objects.all() if request.user.has_perm('cinema.view_genre') else Genre.objects.none(),'ratings':Rating.objects.select_related('user','movie').all() if request.user.has_perm('cinema.view_rating') else Rating.objects.none(),'members':get_user_model().objects.order_by('username') if request.user.is_superuser else [],'page':'account'})

@editor_required
def movie_edit(request,pk=None):
    require_permission(request,'change' if pk else 'add','movie')
    movie = get_object_or_404(Movie,pk=pk) if pk else None
    form = MovieForm(request.POST if request.method == 'POST' else None,request.FILES or None,instance=movie)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,'Movie saved and published.' if form.instance.published else 'Draft saved. It is hidden from the catalog.')
        return redirect('studio')
    return render(request,'cabinet/form.html',{'form':form,'heading':f'Edit {movie.title}' if movie else 'Add a movie','movie_form':True})

@editor_required
def genre_edit(request,pk=None):
    require_permission(request,'change' if pk else 'add','genre')
    genre = get_object_or_404(Genre,pk=pk) if pk else None
    form = GenreForm(request.POST if request.method == 'POST' else None,instance=genre)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,'Genre saved.')
        return redirect('studio')
    return render(request,'cabinet/form.html',{'form':form,'heading':'Edit genre' if genre else 'Add a genre'})

@editor_required
def delete_item(request,kind,pk):
    models = {'movie':Movie,'genre':Genre,'rating':Rating}
    if kind not in models: raise PermissionDenied
    require_permission(request,'delete',kind)
    item = get_object_or_404(models[kind],pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request,f'{kind.title()} deleted.')
        return redirect('studio')
    return render(request,'cabinet/delete.html',{'item':item,'kind':kind})

@login_required
@require_POST
def member_role(request,pk):
    if not request.user.is_superuser: raise PermissionDenied
    member = get_object_or_404(get_user_model(),pk=pk)
    if member.is_superuser or member.pk == request.user.pk: raise PermissionDenied
    from django.contrib.auth.models import Group, Permission
    from django.db import transaction
    with transaction.atomic():
        group,_ = Group.objects.get_or_create(name='FRAME editors')
        group.permissions.set(Permission.objects.filter(content_type__app_label='cinema'))
        if request.POST.get('role') == 'editor':
            member.groups.add(group)
            member.is_staff = True
        elif request.POST.get('role') == 'viewer':
            member.groups.remove(group)
            member.is_staff = False
        else: raise PermissionDenied
        member.save(update_fields=['is_staff'])
    messages.success(request,'Account role updated.')
    return redirect('studio')
