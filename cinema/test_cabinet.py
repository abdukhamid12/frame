from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from tempfile import TemporaryDirectory
from .models import Movie, Genre
from .youtube import youtube_video_id

class CabinetTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_superuser('owner',password='strong-test-password')
        self.viewer = User.objects.create_user('viewer',password='strong-test-password')
        self.genre = Genre.objects.create(name='Drama',slug='drama')
        self.data = {'title':'A new story','synopsis':'A movie synopsis','year':2026,'runtime':120,'age_rating':'PG','director':'Director','language':'English','genres':[self.genre.pk],'youtube_url':'https://youtu.be/Way9Dexny3w?si=example','published':'on'}

    def test_link_formats_and_rejection(self):
        for link in ['https://youtu.be/Way9Dexny3w?si=123','https://www.youtube.com/watch?v=Way9Dexny3w&t=20s','https://m.youtube.com/shorts/Way9Dexny3w','https://www.youtube.com/embed/Way9Dexny3w']:
            self.assertEqual(youtube_video_id(link),'Way9Dexny3w')
        for link in ['https://youtube.com.evil.com/watch?v=Way9Dexny3w','https://evil.com/Way9Dexny3w','https://youtube.com/playlist?list=123','Way9Dexny3w']:
            with self.assertRaises(ValidationError): youtube_video_id(link)

    def test_viewer_cannot_publish_or_grant_access(self):
        self.assertEqual(self.client.get('/account/').status_code,302)
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get('/account/').status_code,200)
        for url in ['/account/studio/','/account/studio/movies/new/','/account/studio/genres/new/']:
            self.assertEqual(self.client.get(url).status_code,403)
            self.assertEqual(self.client.post(url,self.data).status_code,403)
        self.assertEqual(self.client.post(f'/account/studio/members/{self.viewer.pk}/role/',{'role':'editor'}).status_code,403)
        self.assertFalse(Movie.objects.exists())

    def test_owner_publishes_and_updates_draft(self):
        self.client.force_login(self.owner)
        response = self.client.post('/account/studio/movies/new/',self.data)
        self.assertRedirects(response,'/account/studio/')
        movie = Movie.objects.get()
        self.assertEqual(movie.youtube_id,'Way9Dexny3w')
        self.assertContains(self.client.get(f'/movie/{movie.slug}/'),'youtube-nocookie.com/embed/Way9Dexny3w')
        self.assertContains(self.client.get(f'/account/studio/movies/{movie.pk}/'),'YouTube trailer link')
        data = dict(self.data); data.pop('published')
        self.client.post(f'/account/studio/movies/{movie.pk}/',data)
        self.assertEqual(self.client.get(f'/movie/{movie.slug}/').status_code,404)
        self.assertContains(self.client.get('/account/studio/'),'Draft')

    def test_invalid_link_does_not_save(self):
        self.client.force_login(self.owner)
        response = self.client.post('/account/studio/movies/new/',dict(self.data,youtube_url='https://example.com/watch?v=Way9Dexny3w'))
        self.assertContains(response,'Paste a valid YouTube video link')
        self.assertEqual(Movie.objects.count(),0)

    def test_genre_create_edit_and_delete_confirmation(self):
        self.client.force_login(self.owner)
        self.client.post('/account/studio/genres/new/',{'name':'Comedy'})
        genre = Genre.objects.get(slug='comedy')
        self.client.post(f'/account/studio/genres/{genre.pk}/',{'name':'Romantic Comedy'})
        genre.refresh_from_db(); self.assertEqual(genre.slug,'romantic-comedy')
        url = f'/account/studio/genre/{genre.pk}/delete/'
        self.assertEqual(self.client.get(url).status_code,200)
        self.assertTrue(Genre.objects.filter(pk=genre.pk).exists())
        self.client.post(url)
        self.assertFalse(Genre.objects.filter(pk=genre.pk).exists())

    def test_roles_and_model_permissions(self):
        self.client.force_login(self.owner)
        self.client.post(f'/account/studio/members/{self.viewer.pk}/role/',{'role':'editor'})
        self.viewer.refresh_from_db()
        self.assertTrue(self.viewer.is_staff)
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get('/account/studio/movies/new/').status_code,200)
        self.assertEqual(self.client.post(f'/account/studio/members/{self.owner.pk}/role/',{'role':'viewer'}).status_code,403)
        self.viewer.groups.clear()
        self.assertEqual(self.client.post('/account/studio/movies/new/',self.data).status_code,403)

    def test_local_upload_and_clear_to_youtube(self):
        self.client.force_login(self.owner)
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            data = dict(self.data,trailer=SimpleUploadedFile('trailer.mp4',b'test-video',content_type='video/mp4'))
            self.client.post('/account/studio/movies/new/',data)
            movie = Movie.objects.get()
            self.assertTrue(movie.trailer.name)
            self.assertContains(self.client.get(f'/movie/{movie.slug}/'),'<video')
            self.client.post(f'/account/studio/movies/{movie.pk}/',dict(self.data,**{'trailer-clear':'on'}))
            movie.refresh_from_db(); self.assertFalse(movie.trailer)
            self.assertContains(self.client.get(f'/movie/{movie.slug}/'),'youtube-nocookie.com/embed/')
