from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Auction, Bid, Comment
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class Listing(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows":"1", "columns":"2"}))
    image = forms.URLField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    categories = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    start_bid = forms.FloatField(widget=forms.TextInput(attrs={"class": "form-control"}))


def index(request):
    return render(request, "auctions/index.html")


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

# def message(request):
    
#     if request.user.is_anonymous:
#         messages.warning(request, 'You must login to use this feature')
#     return create(request)


# @login_required(login_url="login")
def create(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return render(request, "auctions/create.html",{
            "message": "You need to login to use this feature"
        }) 
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
        raise Http404("Flight not found")
    return render(request, "auctions/title.html",{
        "auction_title":auction.title,
        "auction_image": auction.image,
        "auction_desc": auction.description,

    })
    # Check if title is in the database using queries