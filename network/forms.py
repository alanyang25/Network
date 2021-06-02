from django import forms
from .models import *

class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'What is happening?',
                                                'style': 'box-shadow:none; resize:none; overflow: hidden; border-radius: 8px;',
                                                 'rows': 3})
        }
        labels = {
            'content':'',
        }

class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = '__all__'
		exclude = ['user']