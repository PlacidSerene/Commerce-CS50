from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
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

class Listing(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows":"1", "columns":"2"}))
    image = forms.URLField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    categories = forms.CharField(required=False, widget=forms.Select(choices=CATEGORY_CHOICES, attrs={"class": "form-control"}))
    start_bid = forms.FloatField(widget=forms.TextInput(attrs={"class": "form-control"}))

# ////////////////////// Helping function /////////////////////

## Getting the highest bid in an auction:
def highest(auction):
    all_bids = auction.bid_autions.all()
    highest_bid = ""
    if len(all_bids) != 0:
        highest_bid = all_bids[0].price
        for bid in all_bids:
            if bid.price > highest_bid:
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
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            categories = form.cleaned_data["categories"]
            start_bid = form.cleaned_data["start_bid"]
            Auction.objects.create(created_user=request.user, title=title, description=description, image=image, categories=categories, start_bid=start_bid)
            return HttpResponseRedirect(reverse("title", kwargs={"title":title}))

    else:

        return render(request, "auctions/create.html",{
            "form": Listing()
        })

def listing(request):
    pass

def title(request, title):
    try:
        auction = Auction.objects.get(title=title)
    except Auction.DoesNotExist:
        raise Http404("Auction not found")
    return render(request, "auctions/title.html",{
        "auction":auction,
        "highest_bid": highest(auction),
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

def category(request, title):
    if title == "No Category":
        auctions = Auction.objects.filter(categories="")
        return render(request, "auctions/category.html", {
        "auctions": auctions,
        "title": "No Category"
    })
    else:
        auctions = Auction.objects.filter(categories=title)
        return render(request, "auctions/category.html", {
            "auctions": auctions,
            "title": title
        })
    # return render(request, "auctions/category.html")
    


