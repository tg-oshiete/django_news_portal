from django.urls import path
from .views import NewsList, NewDetail, NewsSearch, NewsCreate, ArticleCreate, NewsUpdate, ArticleUpdate, ArticleDelete, NewsDelete


# Некоторые имена было бы корректнее назвать иначе, но т.к. по тз стоят конкретные ссылки, но при этом не указаны
# ссылки для статей, то функционал статей включен в /news, путем выбора категории публикации.

urlpatterns = [
    path('news/', NewsList.as_view(), name='news_list'),
    path('news/<int:pk>/', NewDetail.as_view(), name='news_detail'), # доступ к странице осуществляется по id самого поста с новостью
    path('news/search/', NewsSearch.as_view(), name='news_search'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('article/create/', ArticleCreate.as_view(), name='article_create'),
    path('news/<int:pk>/edit/', NewsUpdate.as_view(), name='news_update'),
    path('article/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_update'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('article/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete')
]
