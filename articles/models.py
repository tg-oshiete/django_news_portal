from django.db import models
from django.contrib.auth.models import User

ARTICLE = 'Article'
NEWS = 'News'

post_types = [(ARTICLE, 'Статья'),
              (NEWS, 'Новость')]

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_rating = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False) # для функционала мягкого удаления автора

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def update_rating(self):
        post_rating = sum(post.rating for post in self.post_set.all())*3
        comment_rating = sum(comment.rating for comment in Comment.objects.filter(user=self.user))
        post_comments_rating = sum(comment.rating
                                   for post in self.post_set.all()
                                   for comment in post.comment_set.all())
        self.user_rating = post_rating+comment_rating+post_comments_rating
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=125, unique=True)


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING)
    type_post = models.CharField(max_length=50, choices=post_types)
    creation = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.TextField()
    content = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.content[:124]}...'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    creation = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()