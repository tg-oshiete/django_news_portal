from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, NEWS

class NewsList(ListView):
    # model = Post
    # ordering = "-creation"
    queryset = Post.objects.filter(type_post=NEWS).order_by('-creation')
    template_name = 'news.html'
    context_object_name = 'news'

class NewDetail(DetailView):
    queryset = Post.objects.filter(type_post=NEWS)
    # model = Post
    template_name = 'new.html'
    context_object_name = 'new'