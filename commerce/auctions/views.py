from django.contrib.auth import authenticate, login, logout
from django.core.validators import MinValueValidator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm, TextInput, Textarea, Select, NumberInput
from .models import User, Auction, Bid, Comment, WatchList
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# ////////////////////////// Form /////////////////////////////

CATEGORY_CHOICES = [
    ("", "No Category"),
    ("fashion","Fashion"),
    ("toy","Toy"),
    ("electronic","Electronic"),
    ("home","Home"),
    ("education","Education"),
    ("general","General")
]

class Listing(ModelForm):
    class Meta:
        model = Auction
        fields = ["title", "description", "image", "categories", "start_bid"]
        widgets = {
            "title": TextInput(attrs={'class':'form-control'}),
            "description": Textarea(attrs={'class':'form-control'}),
            "image": TextInput(attrs={'class':'form-control'}),
            "categories": Select(choices=CATEGORY_CHOICES, attrs={'class':'form-control'}),
            "start_bid": NumberInput(attrs={'class':'form-control'}),
        }

    def clean_start_bid(self, *args, **kwargs):
        start_bid = self.cleaned_data.get("start_bid")
        if float(start_bid) < 1:
            raise forms.ValidationError("Should be at least $1")
        return start_bid
    
class Bid_Form(ModelForm):
    class Meta:
        model = Bid
        fields = ["price"]
        widgets = {
            "price": NumberInput(attrs={'class':'form-control'}),
        }
    def clean_price(self, *args, **kwargs):
        price = self.cleaned_data.get("price")
        if float(price) < 1:
            raise forms.ValidationError("Should be at least $1")
        return price

class Comment_Form(ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment": TextInput(attrs={'class':'form-control'}),
        }

    

# ////////////////////// Helping functions /////////////////////

## Getting the highest bid in an auction:
def highest(auction):
    all_bids = auction.bid_auctions.all()
    highest_bid = ""
    if len(all_bids) != 0:
        highest_bid = all_bids[0]
        for bid in all_bids:
            if bid.price > highest_bid.price:
                highest_bid = bid
    return highest_bid


#////////////////////// Views Functions /////////////////////
def index(request):
    
    return render(request, "auctions/index.html",{
        "auctions": Auction.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="login")
def create(request):
    if request.method == "POST":

        form = Listing(request.POST)
        
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_user = request.user
            listing.save()
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing.id}))
        else:
            return render(request, "auctions/create.html",{
            "form": Listing(request.POST),
            "error": "Something is wrong"
        })

    else:

        return render(request, "auctions/create.html",{
            "form": Listing(),
        })


def listing(request, listing_id):
    
    try:
        auction = Auction.objects.get(id=listing_id)
    except Auction.DoesNotExist:
        raise Http404("Auction not found")
    
    if request.user.is_authenticated:
        # Get all autions from watchlist 
        watchlist = [item.auction for item in request.user.watchlist.all()]
    return render(request, "auctions/listing.html",{
        "auction":auction,
        "bid_form": Bid_Form(),
        "highest_bid": highest(auction),
        "watchlist": watchlist,
        "comment_form": Comment_Form(),
        "comments": auction.comment_auctions.all()
    })


def bid(request, listing_id):
    auction = Auction.objects.get(id=listing_id)
    bid_price = float(request.POST.get('price'))
    
    if highest(auction): #If there's at least 1 bid
        if bid_price > highest(auction).price:
            Bid.objects.create(price=bid_price, user=request.user, auction=auction)
            auction.current_winner = request.user
            auction.save()
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
        else:
            error = "Your bid must be greater than the current highest bid"
            return render(request, "auctions/listing.html",{
                "auction":auction,
                "bid_form": Bid_Form(request.POST),
                "highest_bid": highest(auction),
                "watchlist": watchlist,
                "comment_form": Comment_Form(),
                "comment": auction.comment_auctions.all(),
                "error": error,
                }
                )
    # If currently there is no bid 
    else:
        if bid_price > auction.start_bid:
            Bid.objects.create(price=bid_price, user=request.user, auction=auction)
            auction.current_winner = request.user
            auction.save()
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

    

def comment(request, listing_id):
    auction = Auction.objects.get(id=listing_id)
    comment = request.POST.get('comment')
    if comment != None:
        Comment.objects.create(comment=comment, user=request.user, auction=auction)
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
    return render(request, "auctions/listing.html", {
        "auction":auction,
        "bid_form": Bid_Form(request.POST),
        "highest_bid": highest(auction),
        "watchlist": watchlist,
        "comment_form": Comment_Form(),
        "comment": auction.comment_auctions.all(),
    })
    


        

def categories(request):
    auctions = Auction.objects.all()
    categories = []
    for auction in auctions:

        if auction.categories not in categories:
            if (auction.categories == "") and ("No Category" not in categories):
                categories.append("No Category")
            else:
                categories.append(auction.categories)
    
    return render(request, "auctions/categories.html",{
        "categories":categories
    })

def category(request, category):
    if category == "No Category":
        auctions = Auction.objects.filter(categories="")
        return render(request, "auctions/category.html", {
        "auctions": auctions,
        "title": "No Category"
    })
    else:
        auctions = Auction.objects.filter(categories=category)
        return render(request, "auctions/category.html", {
            "auctions": auctions,
            "category": category
        })


def watchlist(request, user_id):
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
    })

def toggle_watchlist(request, user_id, listing_id):
    if request.method == "POST":
        value = request.POST.get("check")
        user = User.objects.get(id=user_id)
        auction = Auction.objects.get(id=listing_id)
        if value == "notInList":
            # add to watchlist
            WatchList.objects.create(user=user, auction= auction)
        if value == "inList":
            # remove from watchlist
            instance = WatchList.objects.get(user=user, auction=auction)
            instance.delete()
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))



        
