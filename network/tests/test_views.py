# Standard
import json
import os
# Django
from django.test import TestCase, Client
from django.contrib import auth
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
# Local
from network.models import *
from network.forms import *

class TestViews(TestCase):
    """ 
    1. Login view
    2. Logout view
    3. Register view
    4. Index view
    5. Post view
    6. Profile view
    7. Following view
    """
    def setUp(self):

        self.user = User.objects.create_user(username="test", email="test@t.com", password="test")
        self.c = Client()

    # 1. ==========Login view==========
    # Login view - GET
    def test_GET_login_status_code(self):
        """ Make sure status code for GET login is 200 """
        response = self.c.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_GET_login_correct_redirection(self):
        """ Check redirection to index for logged users """
        # Login user and Get the response
        response = self.c.post('/login', {'username': 'test', 'password': 'test'})
        # Check redirect status code and redirection url
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    # Login view - POST
    def test_POST_login_correct_user(self):
        """ Check login basic behaviour - status code, redirection, login status """
        # Get user logged out info
        c_logged_out = auth.get_user(self.c)
        # Try to login
        response = self.c.post('/login', {'username': 'test', 'password': 'test'})
        # Get user logged in info
        c_logged_in = auth.get_user(self.c)

        self.assertFalse(c_logged_out.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertTrue(c_logged_in.is_authenticated)

    def test_POST_login_invalid_password(self):
        """ Check invalid password login behaviour """
        response = self.c.post('/login', {'username': 'test', 'password': '123'})

        self.assertEqual(response.context["message"], "Invalid username and/or password.")


    # 2. ==========Logout view==========
    # Logout view
    def test_logout_view(self):
        """ Check all logout behaviour - status code, redirection, login status """
        # Login user
        self.c.login(username='test', password="test")
        # Get user logged in info
        c_logged_in = auth.get_user(self.c)
        # Try to logout
        response = self.c.get('/logout')
        # Get user logged out info
        c_logged_out = auth.get_user(self.c)

        self.assertTrue(c_logged_in.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertFalse(c_logged_out.is_authenticated)


    # 3. ==========Register view==========
    # Register view - GET
    def test_GET_register_status_code(self):
        """ Make sure status code for GET register is 200 """
        response = self.c.get("/register")
        self.assertEqual(response.status_code, 200)

    # Register view - POST
    def test_POST_register_correct(self):
        """ Check register basic behaviour - status code, redirection, login status, new profile created """
        # Get user logged out info
        c_logged_out = auth.get_user(self.c)
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': 'correct@gmail.com',
            'password': 'correct',
            'confirmation': 'correct'
            })
        # Get user registered info
        c_registered = auth.get_user(self.c)
        # Get the new user
        new_user = User.objects.filter(username='correct')

        self.assertFalse(c_logged_out.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertTrue(c_registered.is_authenticated)
        self.assertEqual(new_user.count(), 1)

    def test_POST_register_empty_username(self):
        """ If username empty -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': '',
            'email': 'correct@gmail.com',
            'password': 'correct',
            'confirmation': 'correct'
            })

        self.assertEqual(response.context['message'], "You must fill out all fields.")

    def test_POST_register_empty_email(self):
        """ If email empty -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': '',
            'password': 'correct',
            'confirmation': 'correct'
            })

        self.assertEqual(response.context['message'], "You must fill out all fields.")

    def test_POST_register_empty_password(self):
        """ If password empty -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': 'correct@gmail.com',
            'password': '',
            'confirmation': ''
            })

        self.assertEqual(response.context['message'], "You must fill out all fields.")

    def test_POST_register_passwords_dont_match(self):
        """ If password != confirmation -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': 'correct@gmail.com',
            'password': 'test',
            'confirmation': 'correct'
            })

        self.assertEqual(response.context['message'], "Passwords must match.")

    def test_POST_register_username_taken(self):
        """ If user already exists -> make sure error msg is correct """
        # Try to register
        response = self.c.post('/register', {
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'test',
            'confirmation': 'test'
            })

        self.assertEqual(response.context['message'], "Username already taken.")


    # 4. ==========Index view==========
    # Index view
    def test_index_1_page(self):
        """ Make sure status code is correct and 1 page is displayed """
        response = self.c.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)

    def test_index_2_pages(self):
        """ Make sure status code is correct and 2 pages are displayed """
        for _ in range(11):
            Post.objects.create(created_by=self.user, content="test")

        response = self.c.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)


    # 5. ==========Post view==========
    # Post view - POST
    def test_POST_post_create_post(self):
        """ Create a post -> check if post exists """
        # Login user
        self.c.login(username="test", password="test")

        # Post a post
        response = self.c.post('/', {"content": "post create test"})

        self.assertEqual(Post.objects.filter(content="post create test").count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    # Post view - PUT
    def test_PUT_edit_post(self):
        """ Test editing of a post """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        old_post = Post.objects.create(created_by=self.user, content="old content")
        # Edit post's content
        response = self.c.put('/post', json.dumps({
            "post_id": old_post.id,
            "editedpost": "new content"
        }))
        # Get the post after editing
        new_post = Post.objects.get(id=old_post.id)

        self.assertEqual(old_post.content, "old content")
        self.assertEqual(new_post.content, "new content")
        self.assertEqual(response.status_code, 201)

    def test_POST_like_post(self):
        """ Test like a post """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        p_old = Post.objects.create(created_by=self.user, content="content")
        # Add one like to the post
        response = self.c.put('/post', json.dumps({
            "clicked": True,
            "post_id": p_old.id
        }))
        # Get the post after like
        p_new = Post.objects.get(id=p_old.id)

        self.assertEqual(p_new.liker.count(), 1)
        self.assertEqual(response.status_code, 201)

    def test_POST_unlike_post(self):
        """ Test unlike a post """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        p_old = Post.objects.create(created_by=self.user, content="content")
        p_old.liker.add(self.user) # Like the post first
        # Remove one like to the post
        response = self.c.put('/post', json.dumps({
            "clicked": True,
            "post_id": p_old.id
        }))
        # Get the post after like
        p_new = Post.objects.get(id=p_old.id)

        self.assertEqual(p_new.liker.count(), 0)
        self.assertEqual(response.status_code, 201)

    
    # 6. ==========Profile view==========
    # User-profile view
    def test_user_profile_login_required(self):
        """ Make sure login required restriction works -> redirect to login """
        response = self.c.get(f'/profile/{self.user.username}')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/profile/test")

    def test_GET_user_profile_status_code(self):
        """ Make sure status code for GET user profile is 200 (logged in user) """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get(f'/profile/{self.user.username}')
        self.assertEqual(response.status_code, 200)

    def test_user_profile_1_page(self):
        """ Make sure 1 page of posts is displayed """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get(f'/profile/{self.user.username}')

        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)

    def test_user_profile_2_pages(self):
        """ Make sure status 2 pages of posts are displayed """
        # Login user
        self.c.login(username="test", password="test")

        # Create posts (more than can be on 1 page)
        for _ in range(11):
            Post.objects.create(created_by=self.user, content="test")

        response = self.c.get(f'/profile/{self.user.username}')

        self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)

    def test_user_profile_show_only_users_posts(self):
        """ Make sure only posts created by the currently viewed user are visible """
        # Login user
        self.c.login(username="test", password="test")

        # Create a second user
        user_2 = User.objects.create_user(username="test_2", password="test_2")

        # Create user's post
        post_user = Post.objects.create(created_by=self.user, content="user")
        # Create user_2's post
        post_user_2 = Post.objects.create(created_by=user_2, content="user_2")

        # Get all posts count
        all_posts = Post.objects.all()

        # Get response from user and user_2 profile
        response = self.c.get(f'/profile/{self.user.username}')
        response_user_2 = self.c.get(f'/profile/{user_2.username}')

        # Get context paginator posts
        post_list_user = response.context['page_obj'].object_list
        post_list_user_2 = response_user_2.context['page_obj'].object_list

        self.assertEqual(all_posts.count(), 2)
        # User profile - check if only one post exists
        self.assertEqual(len(post_list_user), 1)
        # User profile - check if post's author is user
        self.assertEqual(post_list_user[0].created_by, post_user.created_by)
        # User_2 profile - check if only one post exists
        self.assertEqual(len(post_list_user_2), 1)
        # User_2 profile - check if post's author is user_2
        self.assertEqual(post_list_user_2[0].created_by, post_user_2.created_by)

    def test_user_profile_followers(self):
        """ Follow by 5 users -> make sure that correct number is send as a context """
        # Login user
        self.c.login(username="test", password="test")

        # Create 5 users
        for i in range(3):
            UserFollowing.objects.create(
                user_id = User.objects.create_user(username=str(i), password=str(i)),
                following_user_id = self.user
            )

        response = self.c.get(f'/profile/{self.user.username}')

        self.assertEqual(response.context["current_user"].followers.count(), 3)

    def test_user_profile_following(self):
        """ Follow 5 users -> make sure that correct number is send as a context """
        # Login user
        self.c.login(username="test", password="test")

        # Create 5 users
        for i in range(3):
            UserFollowing.objects.create(
                user_id = self.user,
                following_user_id = User.objects.create_user(username=str(i), password=str(i))
            )

        response = self.c.get(f'/profile/{self.user.username}')

        self.assertEqual(response.context["current_user"].following.count(), 3)

    # Edit-profile view
    def test_edit_profile_login_required(self):
        """ Make sure login required restriction works -> redirect to login """
        response = self.c.get(f'/profile/{self.user.username}')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/profile/test")

    # Edit-profile view - GET
    def test_GET_edit_profile_status_code(self):
        """ Make sure reponse status code for GET request is 200 (logged user) """
        # Login user
        self.c.login(username="test", password="test")
        response = self.c.get(f'/profile/{self.user.username}')

        self.assertEqual(response.status_code, 200)

    # Edit-profile view - POST
    def test_POST_edit_profile(self):
        """ Test POST request -> update user profile pic """
        # Login user
        self.c.login(username="test", password="test")

        # Get test image path
        test_img_path = os.path.join(settings.MEDIA_ROOT, 'tests', 'test.jpg')

        # Open the image
        with open(test_img_path, "rb") as infile:
            # create SimpleUploadedFile object from the image
            img_file = SimpleUploadedFile("test.jpg", infile.read())
 
            # Send the POST request
            response = self.c.post(f'/profile/{self.user.username}', {
                "image": img_file
            })

        # Get the new user profile data
        new_user_profile = Profile.objects.get(user=self.user)

        # Prepare image file path to comparison
        # 1. Normalize it
        new_img_path = os.path.normpath(new_user_profile.image.path)
        # Get the last part of the path and discard django's additional chars
        img_name = os.path.basename(new_img_path)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(img_name, "test.jpg")

        # Delete new image file
        if os.path.exists(new_img_path):
            os.remove(new_img_path)


    # 7. ==========Following view==========
    # Following view
    def test_following_login_required(self):
        """ Make sure login required restriction works -> redirect to login """
        response = self.c.get('/following')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login?next=/following')

    def test_GET_following_status_code(self):
        """ Make sure status code for GET user profile is 200 (logged in user) """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get('/following')
        self.assertEqual(response.status_code, 200)

    def test_following_1_page(self):
        """ Make sure 1 page of posts is displayed """
        # Login user
        self.c.login(username="test", password="test")

        # Create a user
        new_user = User.objects.create_user(username="1", password="1")

        # Create posts by user which is not followed
        for _ in range(11):
            Post.objects.create(created_by=new_user, content="test")

        response = self.c.get('/following')

        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)

    def test_following_2_pages(self):
        """ Make sure status 2 pages of posts are displayed """
        # Login user
        self.c.login(username="test", password="test")

        # Create 3 users, follow them and create 5 posts for each user
        for i in range(3):
            new_user = User.objects.create_user(username=str(i), password=str(i))

            UserFollowing.objects.create(
                user_id=self.user,
                following_user_id=new_user
            )

            for _ in range(4):
                Post.objects.create(created_by=new_user, content="test")

        response = self.c.get('/following')

        self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)

    def test_following_show_only_users_posts(self):
        """ Make sure only posts created by the followed user are visible """
        # Login user
        self.c.login(username="test", password="test")

        # Create a second user
        user_2 = User.objects.create_user(username="test_2", password="test_2")
        # Follow the new user
        UserFollowing.objects.create(user_id=self.user, following_user_id=user_2)

        # Create user's post
        Post.objects.create(created_by=self.user, content="user")
        # Create user_2's post
        post_user_2 = Post.objects.create(created_by=user_2, content="user_2")

        # Get all posts
        all_posts = Post.objects.all()

        response = self.c.get('/following')

        # Get context paginator posts
        post_list = response.context['page_obj'].object_list

        self.assertEqual(all_posts.count(), 2)
        # Following - check if only one post exists
        self.assertEqual(len(post_list), 1)
        # Following - check if post's author is user_2
        self.assertEqual(post_list[0].created_by, post_user_2.created_by)