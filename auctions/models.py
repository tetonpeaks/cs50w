from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from uuid import uuid4


# Models: Your application should have at least three models in addition to the User model:
# one for auction listings, one for bids, and one for comments made on auction listings.

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', related_name='watchlist', blank=True)
    pass

class Listing(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(default='https://scx2.b-cdn.net/gfx/news/hires/2019/apple.jpg')

    class CategoryChoices(models.TextChoices):
        PROTEIN = 'protein'
        PRODUCE = 'produce'
        FATS = 'fats'
        PET = 'pet'
        JUNKFOOD = 'junkfood'

    category = models.CharField(max_length=100, choices=CategoryChoices.choices, blank=True)

    current_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='user')
    active = models.BooleanField(default=True)
    winner = models.CharField(max_length=100, blank=True, null=True)

    is_watched = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.uuid}'

class Bid(models.Model):
    bid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')

    def __str__(self):
        return f'{self.bid}'

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True,)
    text = models.TextField(max_length=500)

    def __str__(self):
        return f'{self.user}: {self.text}'