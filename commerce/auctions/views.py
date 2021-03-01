from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Auction, Bid, Comment
from django.contrib.auth.decorators import login_required

class Listing(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    content = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows":"1", "columns":"2"}))
    image = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", 'required': False}))
    categories = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", 'required': False}))
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

@login_required
def create(request):
    if request.method == "POST":
        form = Listing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            image = form.cleaned_data["image"]
            categories = form.cleaned_data["categories"]
            start_bid = form.cleaned_data["start_bid"]
            auction = Auction.objects.create(title=title, content=content, image=image, categories=categories, start_bid=start_bid)
            return HttpResponseRedirect(reverse("title", kwargs={"title":title}))
        else:
            render(request, "auctions/create.html", {
                "error": True
            })
    else:

        return render(request, "auctions/create.html",{
            "form": Listing()
        })

def listing(request):
    pass

def title(request, title):
    pass
    # Check if title is in the database using queries