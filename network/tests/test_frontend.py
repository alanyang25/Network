# Standard
import json
import os
import time
from datetime import datetime
# Django
from django.test import TestCase, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib import auth
from django.conf import settings
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
# Selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
# Local
from network.models import *
from network.forms import *

class TestFrontEnd(StaticLiveServerTestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="test", password="password")
        self.c = Client()

        # Populate the user-profile with data
        # user_profile = self.user.profile
        # user_profile.name = "Tom"
        # user_profile.save()

        # Create a post
        post = Post.objects.create(created_by=self.user, content="post 1")

        options = webdriver.ChromeOptions()
        # Set chrome to be invisible
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        
        self.browser = webdriver.Chrome(executable_path=r'C:\webdrivers\chromedriver.exe', chrome_options=options)
        
        self.browser.implicitly_wait(5)

        super(TestFrontEnd, self).setUp() # this will call StaticLiveServerTestCase.setUp.

    def tearDown(self):
        time.sleep(2)
        # Close browser after testing
        self.browser.quit()
        super(TestFrontEnd, self).tearDown()

    def login_front_end(self, username="test", password="password"):
        """ Method to automate logging in usign login page form """
        time.sleep(1)
        # Go to login page
        self.browser.get(f"{self.live_server_url}/login")

        # Populate login form with username and password
        username_el = self.browser.find_element_by_name("username")
        password_el = self.browser.find_element_by_name("password")
        username_el.send_keys(username)
        password_el.send_keys(password)

        # Log in
        self.browser.find_element_by_css_selector("input[type='submit']").click()

    def login_quick(self, username="test", password="password"):
        """ Method to automate logging in using client.login method and cookies """
        self.c.login(username=username, password=password)
        cookie = self.c.cookies['sessionid']
        self.browser.get(self.live_server_url)
        self.browser.add_cookie({"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"})

    def is_element_present(self, element, css_locator):
        """ Method to check if element exists in HTML """
        try:
            element.find_element_by_css_selector(css_locator)
        except NoSuchElementException:
            return False
        else:
            return True


    # Index tests
    def test_frontend_create_post_from_form(self):
        """ Create a post using post form -> check if it exists """
        # Login user
        self.login_quick()
        # Get index page
        self.browser.get(self.live_server_url)

        # Get form element
        # form_el = self.browser.find_element_by_css_selector("#add-post form")
        form_el = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#add-post form"))
        )

        # Populate textarea
        form_el.find_element_by_id("id_content").send_keys("Selenium test")
        # Submit form
        form_el.submit()

        # Check if the post exists
        self.assertEqual(Post.objects.filter(content="Selenium test").count(), 1)

    def test_frontend_post_order(self):
        """ Create 2 posts -> check if they are in correct order (from newest to oldest) """
        # Create 2 posts
        post_1 = Post.objects.create(created_by=self.user, content="post 2")
        time.sleep(0.1)
        post_2 = Post.objects.create(created_by=self.user, content="post 3")

        # Login user
        self.login_quick()
        # Get index page
        self.browser.get(self.live_server_url)

        # Wait for page full load
        # WebDriverWait(self.browser, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, ".post-comment-element"))
        # )

        # Get posts
        posts_el = self.browser.find_elements_by_class_name("post")

        # Check is posts' id are in correct order: 3 -> 2 -> 1
        for i, post_el in zip(range(3, 0, -1), posts_el):
            # Get posts inner text
            post_content = post_el.find_elements_by_class_name("post-content")[0]
            # Get posts number
            post_number = post_content.text.split()[-1]
            self.assertEqual(post_number, str(i))

    # User profile tests
    def test_frontend_following_data(self):
        """ Followed by 5 other users, follow 2 users -> check if data in user profile is correct """
        users = []

        # Crete users and follow self.user
        for i in range(5):
            users.append(User.objects.create_user(username=str(i), password=str(i)))
            UserFollowing.objects.create(user_id=users[i], following_user_id=self.user)

        # Make self.user be followed by 2 users
        UserFollowing.objects.create(user_id=self.user, following_user_id=users[0])
        UserFollowing.objects.create(user_id=self.user, following_user_id=users[1])

        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/profile/{self.user.username}")

        # Get following data
        following_info_card = self.browser.find_element_by_id("user-profile")
        following = following_info_card.find_element_by_id("following").text.split(" ")[0]
        followers = following_info_card.find_element_by_id("followers").text.split(" ")[0]

        self.assertEqual(following, str(2))
        self.assertEqual(followers, str(5))

    def test_frontend_profile_picture_src(self):
        """ Check if profile picture is in images folder and is default """
        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/profile/{self.user.username}")

        # Get full profile picure src
        profile_picture = self.browser.find_element_by_css_selector(".profile-img > img").get_attribute("src")
        # Get short src - media/profile_pic/default.png
        profile_picture_short_src = profile_picture.split("/")[-2:]

        self.assertEqual(profile_picture_short_src[0], "images")
        self.assertEqual(profile_picture_short_src[1], "default.jpg")

    def test_frontend_follow_unfollow_button(self):
        """ Check if follow/unfollow button works """
        # Create a user
        new_user = User.objects.create_user(username="1", password="1")

        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/profile/{new_user.username}")

        # Try to follow new_user and check if it works
        follow_button = self.browser.find_element_by_name("follow")
        follow_button.click()
        time.sleep(0.1)
        self.assertEqual(UserFollowing.objects.filter(user_id=self.user, following_user_id=new_user).count(), 1)

        # Try to unfollow new_user and check it works
        unfollow_button = self.browser.find_element_by_name("unfollow")
        unfollow_button.click()
        time.sleep(0.1)
        self.assertEqual(UserFollowing.objects.filter(user_id=self.user, following_user_id=new_user).count(), 0)

    # Edit-profile tests
    def test_frontend_edit_profile_update_profile(self):
        """ Try to fill out and submit the edit-profile form and check if user's profile picture has changed """
        # Get test image path
        test_img_path = os.path.join(settings.MEDIA_ROOT, 'tests', 'test.jpg')

        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/profile/{self.user.username}")

        # Open edit-profile page
        edit_profile_button = self.browser.find_element_by_id("editProfileBtn")
        edit_profile_button.click()

        # Get form's image field
        form_el = self.browser.find_element_by_css_selector(".modal-body > form")
        image_el = form_el.find_element_by_id("id_image")

        # Upload a new photo
        image_el.send_keys(test_img_path)
        time.sleep(0.5)
        # Submit the form
        form_el.submit()
        time.sleep(0.5)

        # Get the new user profile data
        new_user_profile = Profile.objects.get(user=self.user)

        # Prepare image file path to comparison
        # 1. Normalize it
        new_img_path = os.path.normpath(new_user_profile.image.path)
        # 2. Get the last part of the path and discard django's additional chars
        img_name = os.path.basename(new_img_path)

        self.assertEqual(img_name, "test.jpg")

        # Delete new image file
        if os.path.exists(new_img_path):
            os.remove(new_img_path)

    # Posts tests
    def test_frontend_post_content(self):
        """ Check if post's content is equal to post created (index, user-profile, following) """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        UserFollowing.objects.create(user_id=self.user, following_user_id=new_user)
        # Creat a post by the second user
        Post.objects.create(created_by=new_user, content="new user post")

        # Login user
        self.login_quick()

        # Check **index view**
        self.browser.get(self.live_server_url)
        posts_content_el = self.browser.find_elements_by_class_name("post_content")

        self.assertEqual(len(posts_content_el), 2)
        self.assertEqual(posts_content_el[0].text, "new user post")
        self.assertEqual(posts_content_el[1].text, "post 1")

        # Check **user-profile view**
        self.browser.get(self.live_server_url + f"/profile/{self.user.username}")
        posts_content_el = self.browser.find_elements_by_class_name("post_content")

        self.assertEqual(len(posts_content_el), 1)
        self.assertEqual(posts_content_el[0].text, "post 1")

        # Check **following view**
        self.browser.get(self.live_server_url + "/following")
        posts_content_el = self.browser.find_elements_by_class_name("post_content")

        self.assertEqual(len(posts_content_el), 1)
        self.assertEqual(posts_content_el[0].text, "new user post")

    def test_frontend_post_creator_button(self):
        """ Check if post creator's name button redirects correctly to user profile """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        UserFollowing.objects.create(user_id=self.user, following_user_id=new_user)
        # Creat a post by the second user
        Post.objects.create(created_by=new_user, content="new user post")

        # Login user
        self.login_quick()

        # **Check index view**
        self.browser.get(self.live_server_url)
        post_user_link_el = self.browser.find_elements_by_class_name("post_username")
        self.assertEqual(len(post_user_link_el), 2)
        # The second post = self.user's post
        post_user_link_el[1].click()
        time.sleep(0.1)

        # Get current url
        current_url_list = self.browser.current_url.split("/")
        # Check if url is .../profile/{self.user.username}
        self.assertEqual(current_url_list[-2], "profile")
        self.assertEqual(current_url_list[-1], str(self.user.username))

        # **Check user-profile view**
        self.browser.get(self.live_server_url + f"/profile/{self.user.username}")
        post_user_link_el = self.browser.find_elements_by_class_name("post_username")
        self.assertEqual(len(post_user_link_el), 1)
        # The only post = self.user's post
        post_user_link_el[0].click()
        time.sleep(0.1)

        # Get current url
        current_url_list = self.browser.current_url.split("/")
        # Check if url is .../profile/{self.user.username}
        self.assertEqual(current_url_list[-2], "profile")
        self.assertEqual(current_url_list[-1], str(self.user.username))

        # **Check following view**
        self.browser.get(self.live_server_url + "/following")
        time.sleep(1)
        post_user_link_el = self.browser.find_elements_by_class_name("post_username")
        # The only post = new_user's post
        post_user_link_el[0].click()
        time.sleep(0.1)

        # Get current url
        current_url_list = self.browser.current_url.split("/")
        # Check if url is .../profile/{new_user.username}
        self.assertEqual(current_url_list[-2], "profile")
        self.assertEqual(current_url_list[-1], str(new_user.username))