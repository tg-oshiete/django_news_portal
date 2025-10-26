from django import forms
from .models import Post, Category
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class PostForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset = Category.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required = True,
        label = 'Categories'
    )


    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'category',
        ]

        # def __init__(self, *args, **kwargs):
        #     user = kwargs.pop('user')
        #     super().__init__(*args, **kwargs)
        #
        #



class BasicSignupForm(SignupForm):
    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user