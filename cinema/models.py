from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from .youtube import youtube_video_id, validate_youtube_url

def trailer_size(file):
    if file.size > 200 * 1024 * 1024:
        raise ValidationError('Trailer files must be under 200 MB.')

class Genre(models.Model):
    name = models.CharField(max_length=60,unique=True)
    slug = models.SlugField(unique=True)
    def __str__(self): return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=200,blank=True)
    synopsis = models.TextField()
    year = models.PositiveIntegerField()
    runtime = models.PositiveIntegerField(help_text='Full movie runtime in minutes; playback is trailers only.')
    age_rating = models.CharField(max_length=12,default='PG-13')
    director = models.CharField(max_length=120)
    cast = models.TextField(blank=True)
    country = models.CharField(max_length=80,blank=True)
    language = models.CharField(max_length=80,default='English')
    genres = models.ManyToManyField(Genre)
    poster = models.ImageField(upload_to='posters/',blank=True)
    backdrop = models.ImageField(upload_to='backdrops/',blank=True)
    poster_url = models.URLField(blank=True)
    backdrop_url = models.URLField(blank=True)
    trailer = models.FileField(upload_to='trailers/',blank=True,validators=[FileExtensionValidator(['mp4','webm']),trailer_size],help_text='Upload a trailer only, MP4 or WebM, maximum 200 MB. No full movies.')
    youtube_url = models.URLField('YouTube trailer link',blank=True,max_length=500,validators=[validate_youtube_url],help_text='Paste the YouTube watch or share link. Uploaded video takes priority; clear the upload to use this link.')
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return self.title
    @property
    def youtube_id(self): return youtube_video_id(self.youtube_url)
    @property
    def poster_image(self): return self.poster.url if self.poster else self.poster_url
    @property
    def backdrop_image(self): return self.backdrop.url if self.backdrop else self.backdrop_url

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='ratings')
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(10)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','movie'],name='one_rating_per_user'),models.CheckConstraint(condition=models.Q(score__gte=1,score__lte=10),name='rating_range')]

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='saved_by')
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','movie'],name='one_save_per_user')]
