import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import datetime

from .models import *
from .forms import *


def index(request):
    form = PostModelForm()
    current_user = request.user
    
    # POST method: post the form
    if request.method == 'POST':
        form = PostModelForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            creater = current_user
            date_time = datetime.datetime.now() 
            p = Post(content=content, created_by=creater, created_on=date_time)
            p.save()       
        return HttpResponseRedirect(reverse("index"))

    posts = Post.objects.all().order_by("-created_on")

    # pagination
    paginator = Paginator(posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # GET method: show blank form
    return render(request, "network/index.html", {
        'form': form,
        'current_user': current_user,
        "posts": posts,
        "paginator": paginator,
        'page_obj': page_obj
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
        elif not username or not email or not password:
            return render(request, "network/register.html", {
                "message": "You must fill out all fields."
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

@csrf_exempt
@login_required
def post(request):

    # Update whether post is edited or the number of likes is changed
    if request.method == "PUT":
        data = json.loads(request.body)
        post_id = data.get("post_id")
        post = Post.objects.get(id=post_id)
        if not post:
            return JsonResponse({
                "error": "Post does not exist."
            }, status=400)
        content = data.get("editedpost")

        clicked = data.get("clicked")

        if content:
            post.content = content
        
        if clicked:
            if request.user in post.liker.all():
                post.liker.remove(request.user)
            else:
                post.liker.add(request.user)

        post.save()

        return JsonResponse({"message": "You edit the post successfully", "likes_number": str(post.liker.count())}, status=201) 
    # Post must be via PUT
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)

@login_required(login_url="login")
def profile(request, user_name):
    profile_user = User.objects.get(username = user_name)
    current_user = request.user
    
    # Upload profile pic
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    # [others]Follow / Unfollow
    if profile_user != current_user:
        if request.method == "POST":
            if "unfollow" in request.POST:
                UserFollowing.objects.get(user_id=current_user, following_user_id=profile_user).delete()
            elif "follow" in request.POST:
                f = UserFollowing(user_id=current_user, following_user_id=profile_user)
                f.save()

            return HttpResponseRedirect(reverse("profile", args=(user_name, )))
    # [self]Upload profile picture
    else:
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES,instance=profile)
            if form.is_valid():
                form.save()
                form = ProfileForm() # 清空 form
    
    is_following = False
    if profile_user.followers.filter(user_id=current_user, following_user_id=profile_user).exists():
        is_following = True

    posts = Post.objects.filter(created_by = profile_user).order_by("-created_on")# the most recent posts first

    # pagination
    paginator = Paginator(posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "current_user": current_user,
        "posts": posts,
        "is_following": is_following,
        "paginator": paginator,
        "page_obj": page_obj,
        "form": form,
    })

@login_required(login_url="login")
def following(request):
    # Behave just as the “All Posts”(index) page does
    form = PostModelForm()
    current_user = request.user
    
    # POST method: post the form
    if request.method == 'POST':
        form = PostModelForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            creater = current_user
            date_time = datetime.datetime.now() 
            p = Post(content=content, created_by=creater, created_on=date_time)
            p.save()       
        return HttpResponseRedirect(reverse("index"))

    following = [UserFollowing.following_user_id for UserFollowing in current_user.following.all()] # a list of following users
    posts = Post.objects.filter(created_by__in=following).order_by("-created_on") # __in: usage when check if in list
    
    # pagination
    paginator = Paginator(posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # GET method: show blank form
    return render(request, "network/following.html", {
        'form': form,
        'name': current_user,
        "posts": posts,
        "paginator": paginator,
        "page_obj": page_obj
    })
