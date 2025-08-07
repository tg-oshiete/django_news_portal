from django_filters import FilterSet, ChoiceFilter, CharFilter, DateFilter
from django import forms
from .models import Post, ARTICLE, NEWS
from django.db.models import Q


class NewsFilter(FilterSet):
    type_post = ChoiceFilter(
        field_name = 'type_post',
        choices = [(NEWS, 'News'), (ARTICLE, 'Article')],
        label = 'Type Post',
        empty_label = 'Any',
        widget=forms.Select(attrs={'class': 'form-control'}))

    title_search = CharFilter(
        field_name = 'title',
        lookup_expr='icontains',
        label = 'Заголовок публикации',
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    author_search = CharFilter(
        method = 'filter_by_author_name',
        label = 'Автор (имя, фамилия или логин)',
        widget =  forms.TextInput(attrs={
            'placeholder':'Поиск по имени или логину автора...',
            'class': 'form-control'
        })
    )

    publish_date = DateFilter(
        field_name='creation',
        lookup_expr='gte',
        label = 'Опубликовано после',
        widget = forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control datepicker'
            }
        )
    )

    def filter_by_author_name(self, queryset, name, value):
        search_parts = value.split()

        conditions = Q()
        for part in search_parts:
            conditions |= (
                Q(author__user__first_name__icontains=part) |
                Q(author__user__last_name__icontains=part) |
                Q(author__user__username__icontains=part)
            )
        if len(search_parts) >= 2:
            first_last = Q(
                author__user__first__name__icontains=search_parts[0],
                author__user__last__name__icontaints=search_parts[1]
            )
            last_first = Q(
                author__user__last__name__icontains=search_parts[1],
                author__user__first__name_icontains=search_parts[0]
            )
            conditions |= (first_last | last_first)

        return queryset.filter(conditions).distinct()