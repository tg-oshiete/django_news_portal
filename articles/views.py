from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .filters import NewsFilter
from .models import Post, NEWS, ARTICLE
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required


class NewsList(ListView):
    # model = Post
    # ordering = "-creation"
    # queryset = Post.objects.filter(type_post=NEWS).order_by('-creation') # прошлая реализация с выводом только новостей
    queryset = Post.objects.all().order_by('-creation')
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class NewDetail(DetailView):
    # queryset = Post.objects.filter(type_post=NEWS)
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'


class NewsSearch(ListView):
    queryset = Post.objects.all().order_by('-creation')
    template_name = 'news_search.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class NewsCreate(PermissionRequiredMixin ,CreateView):
    permission_required = ('articles.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        form.instance.type_post = NEWS
        return super().form_valid(form)


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('articles.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'article_edit.html'

    def form_valid(self, form):
        form.instance.type_post = ARTICLE
        return super().form_valid(form)


class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('articles.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def get_queryset(self):
        return super().get_queryset().filter(type_post=NEWS)


class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('articles.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'article_edit.html'

    def get_queryset(self):
        return super().get_queryset().filter(type_post=ARTICLE)


class NewsDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return super().get_queryset().filter(type_post=NEWS)


class ArticleDelete(DeleteView):
    model = Post
    template_name = 'article_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return super().get_queryset().filter(type_post=ARTICLE)

class Profile(LoginRequiredMixin, TemplateView): # перенести в приложение для профиля
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context

@login_required()
def upgrade_author(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')