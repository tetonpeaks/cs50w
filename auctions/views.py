from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import User, Listing, Bid, Comment
from .forms import ListingForm, CommentForm

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Active Listings Page: The default route of your web application should let users view
# all of the currently active auction listings. For each active listing, this page should
# display (at minimum) the title, description, current price, and photo (if one exists for the listing).

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all().order_by('-timestamp'),
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

# Create Listing: Users should be able to visit a page to create a new listing.
# They should be able to specify a title for the listing, a text-based description,
# and what the starting bid should be. Users should also optionally be able to
# provide a URL for an image for the listing and/or a category (e.g. Fashion, Toys, Electronics, Home, etc.).

@login_required
def createlisting(request):
    if request.method == "POST":
        listingform = ListingForm(request.POST)
        if listingform.is_valid():
            listing = Listing(user=request.user, **listingform.cleaned_data)
            listing.owner = request.user # set creator to owner
            listing.active = True # activate listing
            listing.winner = ''
            listing.timestamp = timezone.now()
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        listingform = ListingForm()

    return render(request, "auctions/createlisting.html", {
        "form": listingform,
    })

# Listing Page: Clicking on a listing should take users to a page specific to that listing.
# On that page, users should be able to view all details about the listing, including the current price for the listing.

#@login_required()
def listing(request, id):
    if (request.user.is_authenticated):
        listing = Listing.objects.get(pk=id)
        is_watched = request.user in listing.watchlist.all()

        bid = Bid.objects.filter(pk=id)

        user = User.objects.get(username=request.user)

        print("user: ", user)
        print("is_watched: ", is_watched)
        #print("user.watchlist: ", user.watchlist)

        comments = Comment.objects.filter(listing=listing)
        for comment in comments:
            print(f"{bcolors.WARNING}comment: {bcolors.ENDC}{comment}")

        winner = listing.winner

        print(f"{bcolors.WARNING}request.user: {bcolors.ENDC}{request.user}")
        print(f"{bcolors.WARNING}listing.owner: {bcolors.ENDC}{listing.owner}")
        print(f"{bcolors.WARNING}request.user == listing.owner: {bcolors.ENDC}{request.user == listing.owner}")
        print(f"{bcolors.WARNING}listing.active: {bcolors.ENDC}{listing.active}")

        isOwner = request.user == listing.owner

        if not listing.active: messages.info(request, f"You are the winner of {listing.title.lower()}!")

        return render(request, 'auctions/listing.html', {
            'listing': listing,
            'user': request.user,
            'is_watched': is_watched,
            'bid': bid,
            'comments': comments,
            'comment_form': CommentForm(),
            'isOwner': isOwner,
            'winner': winner,
        })
    else:
        messages.error(request, "Please login or register for an account to view products.")
        return render(request, "auctions/index.html", {
            "listings": Listing.objects.all()
        })

@login_required
def comment(request, id):
    listing = Listing.objects.get(pk=id)

    comment = Comment(
        user = request.user,
        listing = listing,
        text = request.POST['comment'],
    )

    comment.save()

    messages.info(request, f"Your comment on item {listing.title.lower()} has been posted.")
    return HttpResponseRedirect(reverse("listing", args=(id,)))

@login_required
def closelisting(request, id):
    listing = get_object_or_404(Listing, pk=id)

    listing_bids = listing.bids.all()
    last_bid = listing_bids.last() if listing_bids.exists() else None

    if last_bid: winner = last_bid.user.username
    else: winner = None

    print(f"{bcolors.WARNING}listing_bids: {bcolors.ENDC}{listing_bids}")
    print(f"{bcolors.WARNING}last_bid: {bcolors.ENDC}{last_bid}")
    print(f"{bcolors.WARNING}winner: {bcolors.ENDC}{winner}")

    listing.winner = winner
    listing.active = False
    listing.save()
    isOwner = request.user.username == listing.owner.username
    bid = Bid.objects.filter(pk=id)
    comments = Comment.objects.filter(listing=listing)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        'user': request.user,
        'bid': bid,
        'comments': comments,
        'comment_form': CommentForm(),
        "isOwner": isOwner,
    })

@login_required
def bid(request, id):
    if request.method == 'POST':
        bid = request.POST.get('bid')
        if bid:
            bid = float(bid)
            listing = Listing.objects.get(pk=id)
            if bid > listing.current_price:

                # Create new Bid object associated w/ the listing instance
                new_bid = Bid(user=request.user, bid=bid, listing=listing)
                new_bid.save()

                # Ppdate current price of listing instance
                listing.current_price = bid
                listing.save()
                messages.success(request, "Your bid was successfully submitted.")

            else:
                messages.error(request, "Bid must be greater than current price.")
    return HttpResponseRedirect(reverse('listing', args=(id,)))

@login_required
def watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
    })

@login_required
def watch(request, id):
    user = request.user
    listing = Listing.objects.get(pk=id)
    listing.watchlist.add(user)
    listing.save()

    return HttpResponseRedirect(reverse("index"))

def unwatch(request, id):
    user = request.user
    listing = Listing.objects.get(pk=id)
    listing.watchlist.remove(user)
    listing.save()

    return HttpResponseRedirect(reverse("index"))


@login_required
def categories(request):
    categories = [choice[1] for choice in Listing.CategoryChoices.choices]
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })

@login_required
def category(request):
    if request.method == "POST":
        return render(request, 'auctions/category.html', {
            'listings': Listing.objects.filter(category=request.POST["category"].lower())
        })