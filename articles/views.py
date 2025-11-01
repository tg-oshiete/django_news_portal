from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .filters import NewsFilter
from .models import Post, NEWS, ARTICLE, Author, Category, Notifications
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import os
from django.conf import settings
from django.utils import timezone
from .tasks import send_notification


POSTS_PER_DAY = 3


class NewsList(ListView):
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
        context['categories'] = Category.objects.all()
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
        if not hasattr(self.request.user, 'author'):
            form.add_error(None, "Только авторы могут создавать посты")
            return self.form_invalid(form)

        author = self.request.user.author
        form.instance.author = author

        if Post.objects.filter(creation__date=timezone.now().date(), author_id = author).count() >= POSTS_PER_DAY:
            form.add_error(None, f"Вы превысили дневной лимит постов! Максимум {POSTS_PER_DAY} в день")
            return self.form_invalid(form)


        form.instance.type_post = NEWS
        response = super().form_valid(form)
        send_notification.delay(self.object.id)
        self.send_email_to_subscribers(form.instance)

        return response

    def send_email_to_subscribers(self, post):
        categories = post.category.all()
        all_subscribers_emails = set()

        for category in categories:
            subscribers = category.subscribers.all()
            for subscriber in subscribers:
                if subscriber.email:
                    all_subscribers_emails.add(subscriber.email)


        if all_subscribers_emails:
            subject = f"Новая новость: {post.title}"
            html_content = render_to_string('email/new_post_notification.html',{
                'post': post, 'category': categories })

            msg = EmailMultiAlternatives(
                subject=subject,
                body=post.preview(),  # Текстовая версия
                from_email=settings.EMAIL_HOST_USER ,
                to=list(all_subscribers_emails),
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('articles.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'article_edit.html'

    def form_valid(self, form):
        if not hasattr(self.request.user, 'author'):
            form.add_error(None, "Только авторы могут создавать посты")
            return self.form_invalid(form)

        author = self.request.user.author
        form.instance.author = author

        if Post.objects.filter(creation__date=timezone.now().date(), author_id = author).count() >= POSTS_PER_DAY:
            form.add_error(None, f"Вы превысили дневной лимит постов!\nМаксимум {POSTS_PER_DAY} в день")
            return self.form_invalid(form)

        form.instance.type_post = ARTICLE
        response = super().form_valid(form)

        return response


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
        context['is_author'] = hasattr(self.request.user, 'author')
        return context

@login_required()
def upgrade_author(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)

    Author.objects.get_or_create(user=user)

    return redirect('/')

@login_required
def subscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.user not in category.subscribers.all():
        category.subscribers.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))

@login_required
def unsubscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.user in category.subscribers.all():
        category.subscribers.remove(request.user)

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))


class CategoryList(ListView):
    model = Category
    queryset = Category.objects.all()
    template_name = 'categories.html'
    context_object_name = 'categories'


class CategoryPosts(ListView):
    template_name = 'categories_posts.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        return Post.objects.filter(category=self.category).order_by('-creation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        # context['user'] = self.request.user
        return context


class CeleryTest(View):
    def get(self, request):
        printer.apply_async([10], countdown=5)
        hello.delay()
        return HttpResponse('Hello!')


class NotificationsList(ListView, LoginRequiredMixin):
    model = Notifications
    template_name = 'notifications.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        return Notifications.objects.filter(users=self.request.user).order_by("-creation")