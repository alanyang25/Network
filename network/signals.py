from django.db.models.signals import post_save
from .models import *

def customer_profile(sender, instance, created, **kwargs):
	"""After a user is created, create its user profile"""
	if created:
		Profile.objects.create(
			user=instance,
			)
		# print('Profile created!')

post_save.connect(customer_profile, sender=User)

