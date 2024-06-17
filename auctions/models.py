from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from uuid import uuid4


# Models: Your application should have at least three models in addition to the User model:
# one for auction listings, one for bids, and one for comments made on auction listings.

class User(AbstractUser):
    pass

class Listing(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default="Dr. Elsey's Precious Cat Ultra Unscented Clumping Clay Cat Litter, 20 lb. Box")
    description = models.TextField(default="Transitioning my cat to brand and type. So far so good!")
    image_url = models.URLField(default="https://i5.walmartimages.com/asr/3c7f1879-793e-48da-a985-dc48e15e88fb_1.c12de5d7cee4f71f77860d9366525b09.jpeg?odnHeight=768&odnWidth=768&odnBg=FFFFFF")
    watchlist = models.ManyToManyField(User, blank=True, null=True,related_name="watchlist")

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

    timestamp = models.DateTimeField(default=timezone.now)

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