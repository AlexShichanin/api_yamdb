from csv import DictReader
from django.core.management import BaseCommand
from reviews.models import Comment, User, Review


class Command(BaseCommand):
    help = "Загрузка из comments.csv"

    def handle(self, *args, **options):
        for row in DictReader(open('./static/data/comments.csv',
                                   encoding='utf-8')):
            comment = Comment(
                id=row['id'],
                review=Review.objects.get(id=row['review_id']),
                text=row['text'],
                author=User.objects.get(id=row['author']),
                pub_date=row['pub_date']
            )
            comment.save()
