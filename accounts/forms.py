from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from accounts.models import Post

class UserCreationForm(UserCreationForm):
    class Meta:
        model= User
        fields=['username','first_name','password1','password2']



class HomeForm(forms.ModelForm):
	post=forms.CharField()

	class Meta():
		model=Post
		fields=('post',)


class EditProfileForm(UserChangeForm):
	class Meta:
		model=User
		fields=(
			'email',
			'first_name',
			'last_name',
			'password'
        )