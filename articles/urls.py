from django.urls import path
from .views import (NewsList, NewDetail, NewsSearch, NewsCreate, ArticleCreate, NewsUpdate,
                    ArticleUpdate, ArticleDelete, NewsDelete, Profile, upgrade_author, subscribe_category,
                    unsubscribe_category, CategoryList, CategoryPosts, CeleryTest, NotificationsList)
from django.views.generic.base import RedirectView
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', RedirectView.as_view(url='/news/')),
    path('news/', cache_page(60)(NewsList.as_view()), name='news_list'),
    path('news/<int:pk>/', NewDetail.as_view(), name='news_detail'), # доступ к странице осуществляется по id самого поста с новостью
    path('news/search/', NewsSearch.as_view(), name='news_search'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('article/create/', ArticleCreate.as_view(), name='article_create'),
    path('news/<int:pk>/edit/', NewsUpdate.as_view(), name='news_update'),
    path('article/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_update'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('article/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
    path('profile/', Profile.as_view(), name='profile'), # перенести этот функционал в отдельное приложение для профиля
    path('profile/notifications/', NotificationsList.as_view(), name='notifications'),
    path('profile/upgrade/', upgrade_author, name='upgrade_author'),
    path('category/<int:category_id>/subscribe', subscribe_category, name='subscribe_category'),
    path('category/<int:category_id>/unsubscribe', unsubscribe_category, name='unsubscribe_category'),
    path('category/', CategoryList.as_view(), name='category_list'),
    path('category/<int:pk>/', CategoryPosts.as_view(), name='category_detail'),
    path('celery_test/', CeleryTest.as_view()),
]
