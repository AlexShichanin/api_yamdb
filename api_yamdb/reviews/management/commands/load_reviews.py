from csv import DictReader
from django.core.management import BaseCommand
from reviews.models import User, Title, Review


class Command(BaseCommand):
    help = "Загрузка из review.csv"

    def handle(self, *args, **options):
        if Review.objects.exists():
            print('Данные уже загружены.')
            return

        for row in DictReader(open('./static/data/review.csv',
                                   encoding='utf-8')):
            review = Review(
                id=row['id'],
                title=Title.objects.get(id=row['title_id']),
                text=row['text'],
                author=User.objects.get(id=row['author']),
                score=row['score'],
                pub_date=row['pub_date']
            )
            review.save()
