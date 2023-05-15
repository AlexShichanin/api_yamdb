from csv import DictReader
from django.core.management import BaseCommand

from reviews.models import Title, Genre, TitleGenre


class Command(BaseCommand):
    help = "Загрузка genre_title.csv"

    def handle(self, *args, **options):
        if TitleGenre.objects.exists():
            print('Данные уже загружены.')
            return

        for row in DictReader(open('./static/data/genre_title.csv')):
            titlegenre = TitleGenre(
                id=row['id'],
                title=Title.objects.get(id=row['title_id']),
                genre=Genre.objects.get(id=row['genre_id'])
            )
            titlegenre.save()
