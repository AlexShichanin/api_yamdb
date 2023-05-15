from csv import DictReader
from django.core.management import BaseCommand
from reviews.models import Category


class Command(BaseCommand):
    help = "Загрузка category.csv"

    def handle(self, *args, **options):
        if Category.objects.exists():
            print('Данные уже загружены.')
            return

        for row in DictReader(open('./static/data/category.csv',
                                   encoding='utf-8')):
            category = Category(id=row['id'], name=row['name'],
                                slug=row['slug'])
            category.save()
