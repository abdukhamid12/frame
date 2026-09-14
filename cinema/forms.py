from django import forms
from django.utils.text import slugify
from .models import Movie, Genre

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title','tagline','synopsis','year','runtime','age_rating','director','cast','country','language','genres','poster','poster_url','backdrop','backdrop_url','trailer','youtube_url','featured','published']
        widgets = {'synopsis':forms.Textarea(attrs={'rows':5}),'cast':forms.Textarea(attrs={'rows':2}),'genres':forms.CheckboxSelectMultiple(),'youtube_url':forms.URLInput(attrs={'placeholder':'https://www.youtube.com/watch?v=…'})}
    def save(self,commit=True):
        if not self.instance.slug:
            base = slugify(self.cleaned_data['title'])[:180] or 'movie'
            slug,index = base,2
            while Movie.objects.filter(slug=slug).exists(): slug,index = f'{base}-{index}',index+1
            self.instance.slug = slug
        return super().save(commit)

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']
    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        slug = slugify(name) or 'genre'
        if Genre.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A genre with this name already exists.')
        self.instance.slug = slug
        return name
