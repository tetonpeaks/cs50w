import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Exists, OuterRef
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

from .models import User, Posts, Likes
from .forms import PostForm

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

liked_tags = {}

#@login_required(login_url='/login')
def index(request):

    global liked_tags

    if (request.user.is_authenticated):
        # Decending order
        user = request.user
        posts = Posts.objects.all().order_by('-timestamp')

        for post in posts:
            liked_tags[post.id] = Likes.objects.filter(user=user, post=post).exists()
            print("post.post_likes: ", post.post_likes)

        liked_tags_json = json.dumps(liked_tags)

        ##print("liked_tags: ", liked_tags)
        ##print("liked_tags_json: ", liked_tags_json)

        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_posts = paginator.get_page(page_number)

        return render(request, "network/index.html", {
            "posts": posts,
            "form": PostForm(),
            "page_posts": page_posts,
            "liked_tags": liked_tags_json,
        })
    else:
        return render(request, "network/login.html")

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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def post(request):
    if request.method == "POST":
        postform = PostForm(request.POST)
        if postform.is_valid():
            # probably will need user.followers or user.following
            post = Posts(user=request.user, **postform.cleaned_data)
            post.timestamp = timezone.now()
            post.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            print(f"{bcolors.FAIL}postform.errors: {bcolors.ENDC}{postform.errors}")
    else:
        postform = PostForm()

    return render(request, "network/index.html", {
        "form": postform,
    })

@login_required
def profile(request, username):

    user = request.user

    print(f"{bcolors.WARNING}user (/profile): ", user)
    print(f"{bcolors.WARNING}request.user (/profile): ", request.user)

    profile_user = get_object_or_404(User, username=username)
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    user_posts = Posts.objects.filter(user=profile_user).order_by('-timestamp')

    is_following = False
    if request.user != profile_user:
        is_following = request.user.following.filter(username=profile_user.username).exists()

    return render(request, "network/profile.html", {
        "user": user,
        "profile_user": profile_user,
        "followers_count": followers_count,
        "following_count": following_count,
        "user_posts": user_posts,
        "is_following": is_following,
    })

@login_required
def follow_user(request, username):
    if request.method == 'POST':
        profile_user = get_object_or_404(User, username=username)
        request.user.following.add(profile_user)
        return redirect('profile', username=username)

@login_required
def unfollow_user(request, username):
    if request.method == 'POST':
        profile_user = get_object_or_404(User, username=username)
        request.user.following.remove(profile_user)
        return redirect('profile', username=username)

@login_required
def following_posts(request):
    if (request.user.is_authenticated):
        followed_users = request.user.following.all()
        posts = Posts.objects.filter(user__in=followed_users).order_by('-timestamp')
        return render(request, "network/following_posts.html", {"posts": posts})
    else:
        return HttpResponseRedirect(reverse("login"))

@login_required
def edit(request, id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Posts.objects.get(pk=id)
        edit_post.text = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change successful", "data": data["content"]})

@login_required
def toggle_likes(request, pid):
    post = get_object_or_404(Posts, id=pid)
    user = request.user

    # Check if user already liked w/ exists method
    if Likes.objects.filter(user=user, post=post).exists():
        # Unlike with delete method
        Likes.objects.filter(user=user, post=post).delete()
        liked = False

        post.post_likes.remove(user)
    else:
        # Like with create method
        Likes.objects.create(user=user, post=post)
        liked = True
        post.post_likes.add(user)

    # Save post
    post.save()

    # Current like count
    current_likes = post.post_likes.count()

    # Return JSON response with updated like status and count
    return JsonResponse({'liked': liked, 'likes': current_likes})

@login_required
def get_like_count(request, pid):
    try:
        post = Posts.objects.get(pk=pid)
        return JsonResponse({'likes': post.post_likes.count()})
    except Posts.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)