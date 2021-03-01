from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Bid(models.Model):
    price = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_autions")
    def __str__(self):
        return f"{self.id}: {self.price}"

class Comment(models.Model):
    comment = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_autions")
    def __str__(self):
        return f"{self.id}: {self.comment}"


class Auction(models.Model):
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_created")
    





