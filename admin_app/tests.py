from django.test import TestCase
from django.contrib.auth import get_user_model
from artist.models import Artist, Song, SongPurchase

User = get_user_model()

class AdminAppTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="adminuser", password="password", is_staff=True)
        self.artist_user = User.objects.create_user(username="artist1", password="password")
        self.artist = Artist.objects.create(user=self.artist_user, stage_name="Stage1")
        self.song = Song.objects.create(artist=self.artist, title="Song1", price=0.00)
        self.purchase = SongPurchase.objects.create(song=self.song, buyer=self.user, price_paid=0.00)

    def test_dashboard_access(self):
        self.client.login(username="adminuser", password="password")
        response = self.client.get("/admin_app/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Top Artists")
        self.assertContains(response, "Liked Songs")