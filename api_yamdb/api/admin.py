from django.contrib import admin
from reviews.models import (Category, Comment, Genre, Review, Title,
                            TitleGenre, User)

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(TitleGenre)
admin.site.register(Review)
admin.site.register(Comment)
