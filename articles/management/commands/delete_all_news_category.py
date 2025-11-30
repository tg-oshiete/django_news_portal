from django.core.management.base import BaseCommand, CommandError
from articles.models import Category, Post

class Command(BaseCommand):
    help = 'Удаляет все новости по заданной категории'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        category_name = options['category']
        try:
            category = Category.objects.get(name=category_name)

            posts = Post.objects.filter(category=category)
            if not posts.exists():
                self.stdout.write(self.style.ERROR(f'Новости в {category_name} не найдены!'))
                return

            self.stdout.write(f'Вы действительно хотите удалить все новости в {category_name}. Напишите yes/no') # вписать категорию
            if input().lower() == 'yes':
                posts.delete()
                self.stdout.write(self.style.SUCCESS(f'All news in {category_name} deleted.'))
            else:
                self.stdout.write('Action cancelled.')

        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Категория {category_name} не найдена!'))