from django.contrib import admin
from .models import Bid, Comment, User, Auction
# Register your models here.


admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Auction)
admin.site.register(User)
