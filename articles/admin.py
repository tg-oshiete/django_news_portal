from django.contrib import admin
from .models import Notifications, Post, Category, Author, Comment

def reset_rating(modeladmin, request, queryset):
    queryset.update(rating=0)
reset_rating.short_description = 'Reset rating'


class PostAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('title', 'author', 'rating') # генерируем список имён всех полей для более красивого отображения
    list_filter = ('author', 'category')
    search_fields = ('title', 'content')
    actions = [reset_rating]


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_rating', 'is_deleted')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_filter = ('is_deleted', )


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post__title', 'user__username', 'rating', 'creation')
    search_fields = ('post__title', 'content')
    list_filter = ('post', 'user')


class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'message', 'creation')
    search_fields = ('name', 'message')
    list_filter = ('users',)



admin.site.register(Notifications, NotificationsAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Comment, CommentAdmin)