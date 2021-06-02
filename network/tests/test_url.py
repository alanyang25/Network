from django.test import TestCase
from django.urls import reverse, resolve
from network.views import *

class TestUrls(TestCase):

    def test_index_url_is_resolved(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, index)
    
    def test_login_url_is_resolved(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, login_view)
    
    def test_logout_url_is_resolved(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, logout_view)
    
    def test_register_url_is_resolved(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, register)
    
    def test_profile_url_is_resolved(self):
        url = reverse('profile', kwargs={"user_name": "testname"})
        self.assertEquals(resolve(url).func, profile)
    
    def test_following_url_is_resolved(self):
        url = reverse('following')
        self.assertEquals(resolve(url).func, following)

    def test_post_url_is_resolved(self):
        url = reverse('post')
        self.assertEquals(resolve(url).func, post)
    