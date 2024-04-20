from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')

class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=6000)
    timestamp = models.DateTimeField(default=timezone.now)
    post_likes = models.ManyToManyField(User, related_name='post_likes', blank=True)

    def __str__(self):
        return f"{self.user}: {self.text} | posted {self.timestamp}"

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} liked {self.post} | posted {self.timestamp}"
