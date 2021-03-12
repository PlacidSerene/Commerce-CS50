from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Auction(models.Model):
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_created")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    image =  models.URLField(max_length=512, blank=True)
    categories = models.CharField(max_length=64, blank=True)
    start_bid = models.FloatField()
    active = models.BooleanField(default=True, blank=False)
    current_winner = models.OneToOneField(User, blank=True, on_delete = models.CASCADE, related_name="winner", null=True)
class Bid(models.Model):
    price = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bid_autions")
    def __str__(self):
        return f"{self.price}"

class Comment(models.Model):
    comment = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_autions")
    def __str__(self):
        return f"{self.id}: {self.comment}"

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="watchlist")





