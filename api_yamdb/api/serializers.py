import datetime as dt

from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, User


RESERVED_NAME = 'me'
MESSAGE_FOR_RESERVED_NAME = 'Имя пользователя "me" использовать нельзя!'
MESSAGE_FOR_USER_NOT_FOUND = 'Пользователя с таким именем нет!'


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для Категорий."""

    class Meta:

        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для Жанров."""

    class Meta:

        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для  чтения Тайтлов."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(
        min_value=0,
        max_value=10,
        read_only=True,
        required=False
    )

    class Meta:
        """."""

        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для записи Тайтлов."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        """Метод валидации Времени."""

        year = dt.date.today().year
        if not (value <= year):
            raise serializers.ValidationError(
                'Год не должен быть больше текущего.'
            )

        return value


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для редактирования пользователя."""

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        model = User

    def validate_username(self, value):
        """Валидаиця username."""
        if RESERVED_NAME == value:
            raise serializers.ValidationError("Запрещенное имя")
        return value


class ForUserAndAdminSerializer(serializers.ModelSerializer):
    """Сериалайзер для пользователей со статусом user и admin."""

    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Этот адрес электроной почты уже используется'
        )]
    )

    class Meta:

        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        """Валидация username."""
        if value == RESERVED_NAME:
            raise serializers.ValidationError(MESSAGE_FOR_RESERVED_NAME)
        return value


class UsersMeSerializer(ForUserAndAdminSerializer):
    """Сериалайзер для редактирования обычного пользователя."""

    role = serializers.CharField(read_only=True)

    class Meta:

        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class SendCodeUserSerializer(serializers.ModelSerializer):
    """Сериалайзер для отправки сообщения на почту."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    class Meta:

        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(max_length=200, required=True)
    confirmation_code = serializers.CharField(max_length=200, required=True)

    def validate_username(self, value):
        """Метод валидации username."""
        if value == RESERVED_NAME:
            raise serializers.ValidationError(MESSAGE_FOR_RESERVED_NAME)
        if not User.objects.filter(username=value).exists():
            raise exceptions.NotFound(MESSAGE_FOR_USER_NOT_FOUND)
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Ревью сериализатор."""

    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:

        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')

    def validate(self, data):
        """Метод валидации."""
        super().validate(data)

        if self.context['request'].method != 'POST':
            return data

        user = self.context['request'].user
        title_id = (
            self.context['request'].parser_context['kwargs']['title_id']
        )
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на данное произведение')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для Комментариев."""

    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:

        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
