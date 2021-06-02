from django.test import TestCase
from network.models import *

class TestModels(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test1", email="test1@t.com", password="test1")
        self.user2 = User.objects.create_user(username="test2", email="test2@t.com", password="test2")
        self.post1 = Post.objects.create(created_by=self.user1, content="test1")
        self.post2 = Post.objects.create(created_by=self.user2, content="test2")

    def test_auto_profile_create(self):
        """ Create new user -> create new profile test """
        self.assertEqual(Profile.objects.count(), 2)

    def test_default_image_create(self):
        """ New profile created -> create default image test """
        image_path = Profile.objects.first().image.path[-11:]
        self.assertEqual(image_path, "default.jpg")

    def test_likes_a_post(self):
        """ Add two likes to a post """
        self.assertEquals(Post.objects.first().liker.count(), 0)
        Post.objects.first().liker.add(self.user1)
        self.assertEquals(Post.objects.first().liker.count(), 1)
        Post.objects.first().liker.add(self.user2)
        self.assertEquals(Post.objects.first().liker.count(), 2)

    def test_unlikes_a_post(self):
        """ Remove one like to a post """
        Post.objects.first().liker.add(self.user1)
        self.assertEquals(Post.objects.first().liker.count(), 1)
        Post.objects.first().liker.remove(self.user1)
        self.assertEquals(Post.objects.first().liker.count(), 0)

    def test_user_follow_method(self):
        """ user1 can follows user2 """
        UserFollowing.objects.create(user_id=self.user1, following_user_id=self.user2)
        self.assertEqual(self.user1.following.count(), 1)
        self.assertEqual(self.user2.followers.count(), 1)

    def test_user_unfollow_method(self):
        """ user1 can unfollows user2 """
        f = UserFollowing.objects.create(user_id=self.user1, following_user_id=self.user2)
        f.delete()
        self.assertEqual(self.user1.following.count(), 0)
        self.assertEqual(self.user2.followers.count(), 0)

    def test_users_unable_follow_themselves(self):
        """ users should not follow themselves """
        with self.assertRaises(ValidationError):
            f = UserFollowing.objects.create(user_id=self.user1, following_user_id=self.user1)
            f.full_clean()
