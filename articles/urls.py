from django.urls import path
from .views import NewsList, NewDetail

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>/', NewDetail.as_view()) # доступ к странице осуществляется по id самого поста с новостью
]