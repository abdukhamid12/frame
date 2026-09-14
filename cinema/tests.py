from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import Movie, Rating, Watchlist

class CinemaTests(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(title='Test movie',slug='test',year=2024,runtime=120,director='Director',synopsis='A story')
        self.user = get_user_model().objects.create_user('viewer',password='a-good-test-password')
    def test_public_pages_and_private_catalog(self):
        Movie.objects.create(title='Hidden',slug='hidden',year=2025,runtime=90,director='Director',synopsis='Secret',published=False)
        for url in ['/','/browse/','/movie/test/','/accounts/login/','/accounts/signup/']:
            self.assertEqual(self.client.get(url).status_code,200)
        self.assertNotContains(self.client.get('/browse/'),'Hidden')
        self.assertEqual(self.client.get('/movie/hidden/').status_code,404)
    def test_search_and_empty_results(self):
        self.assertContains(self.client.get('/browse/?q=Test'),'Test movie')
        self.assertContains(self.client.get('/browse/?q=nonexistent'),'No movies found')
    def test_watchlist_auth_and_toggle(self):
        self.assertEqual(self.client.post('/movie/test/save/').status_code,302)
        self.assertEqual(Watchlist.objects.count(),0)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/movie/test/save/').status_code,405)
        self.client.post('/movie/test/save/')
        self.assertContains(self.client.get('/my-list/'),'Test movie')
        self.client.post('/movie/test/save/')
        self.assertEqual(Watchlist.objects.count(),0)
    def test_rating_is_valid_and_updates(self):
        self.client.force_login(self.user)
        for score in ['0','11','abc']:
            self.client.post('/movie/test/rate/',{'score':score})
        self.assertEqual(Rating.objects.count(),0)
        self.client.post('/movie/test/rate/',{'score':8})
        self.client.post('/movie/test/rate/',{'score':9})
        self.assertEqual(Rating.objects.count(),1)
        self.assertEqual(Rating.objects.get().score,9)
        self.assertContains(self.client.get('/movie/test/'),'9.0')
    def test_trailer_extension_validation(self):
        self.movie.trailer = SimpleUploadedFile('bad.html',b'<script>bad</script>')
        with self.assertRaises(ValidationError): self.movie.full_clean()
    def test_signup(self):
        response = self.client.post('/accounts/signup/',{'username':'newviewer','password1':'A-random-strong-password-123','password2':'A-random-strong-password-123'})
        self.assertRedirects(response,'/')
        self.assertTrue(get_user_model().objects.filter(username='newviewer').exists())
