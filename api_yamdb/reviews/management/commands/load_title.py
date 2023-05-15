from csv import DictReader
from django.core.management import BaseCommand
from reviews.models import Title, Category


class Command(BaseCommand):
    help = "Загрузка из titles.csv"

    def handle(self, *args, **options):
        if Title.objects.exists():
            print('Данные уже загружены.')
            return

        for row in DictReader(open('./static/data/titles.csv',
                                   encoding='utf-8')):
            title = Title(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                category=Category.objects.get(id=row['category'])
            )
            title.save()
