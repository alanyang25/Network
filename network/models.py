from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")

    def __str__(self):
        return f'{self.user.username} Profile'

class UserFollowing(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    follow_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user_id', 'following_user_id']

    def __str__(self):
        return f"{self.user_id} followed {self.following_user_id}"

class Post(models.Model):
    content = models.CharField(max_length=600)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='created_by')
    created_on = models.DateTimeField(auto_now_add = True, null=True)
    liker = models.ManyToManyField(User, blank=True, related_name='like')
    
    def __str__(self):
        return f"A post by {self.created_by}"

