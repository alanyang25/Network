from django.test import TestCase
from network.forms import *

class TestForms(TestCase):
    def test_post_form_valid_data(self):
        """ Post with valid content """
        form = PostModelForm(data={
            'content': 'test_content'
        })

        self.assertTrue(form.is_valid())

    def test_post_form_invalid_data(self):
        """ Post with invalid content """
        form = PostModelForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)