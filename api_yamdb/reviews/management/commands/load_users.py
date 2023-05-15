from csv import DictReader
from django.core.management import BaseCommand
from reviews.models import User


class Command(BaseCommand):
    help = "Загрузка из users.csv"

    def handle(self, *args, **options):
        for row in DictReader(open('./static/data/users.csv',
                                   encoding='utf-8')):
            user = User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
                first_name=row['first_name'],
                last_name=row['last_name']
            )
            user.save()
