from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from api_yamdb.settings import DEFAULT_FROM_EMAIL

from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdminOrSuperUser, IsModerator,
                          IsOwner)
from .serializers import (CategorySerializer, CommentSerializer,
                          ForUserAndAdminSerializer, GenreSerializer,
                          ReviewSerializer, SendCodeUserSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          TokenSerializer, UsersMeSerializer)


class CreateDesListViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateDesListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateDesListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadSerializer

        return TitleWriteSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        avg = Review.objects.filter(title=instance).aggregate(Avg('score'))
        instance.rating = avg['score__avg']
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwner, ]
    permission_classes_by_action = {'list': [AllowAny],
                                    'create': [IsOwner | IsAdminOrReadOnly
                                               | IsModerator],
                                    'retrieve': [AllowAny],
                                    'partial_update': [IsOwner],
                                    'destroy': [IsOwner]}

    def get_permissions(self):
        try:
            return [permission() for permission
                    in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        queryset = Review.objects.filter(title__id=self.kwargs.get('title_id'))

        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwner, ]
    permission_classes_by_action = {'list': [AllowAny],
                                    'create': [IsOwner | IsAdminOrSuperUser
                                               | IsModerator],
                                    'retrieve': [AllowAny],
                                    'partial_update': [IsOwner],
                                    'destroy': [IsAdminOrReadOnly
                                                | IsModerator]}

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title__id=title_id)
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        queryset = Comment.objects.filter(
            review__id=self.kwargs.get('review_id')
        )
        return queryset


class APIToken(APIView):
    """Выдача токена."""

    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = get_object_or_404(
                User, username=serializer.data['username'])
            # проверяем confirmation code, если верный, выдаем токен
            if default_token_generator.check_token(
               user, serializer.data['confirmation_code']):
                token = AccessToken.for_user(user)
                user.is_active = True
                user.save()
                return Response(
                    {'token': str(token)}, status=status.HTTP_200_OK)
            return Response({
                'confirmation code': 'Некорректный код подтверждения!'},
                status=status.HTTP_400_BAD_REQUEST)


class UserViewSetForAdmin(ModelViewSet):
    """Работа с пользователями для администратора."""

    queryset = User.objects.all()
    serializer_class = ForUserAndAdminSerializer
    # поиск по эндпоинту users/{username}/
    lookup_field = 'username'
    permission_classes = (IsAdminOrSuperUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            raise MethodNotAllowed(request.method)
        return super().update(request, *args, **kwargs)


class APIUser(APIView):
    """Работа со своими данными для пользователя."""

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UsersMeSerializer(user, many=False)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UsersMeSerializer(
            user, data=request.data, partial=True, many=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def create_confirmation_code_and_send_email(username, to_email):
    """Создаем confirmation code и отправляем по email."""
    user = get_object_or_404(User, username=username)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения {confirmation_code}',
        DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )


class APISignUp(APIView):
    """Регистрация пользователя."""

    permission_classes = (AllowAny,)

    def post(self, request):
        code_serializer = SendCodeUserSerializer(data=request.data)
        code_serializer.is_valid(raise_exception=True)
        serializer = ForUserAndAdminSerializer(data=request.data)
        data = code_serializer.data
        if not User.objects.filter(username=data['username'],
                                   email=data['email']).exists():
            serializer.is_valid(raise_exception=True)
            serializer.save(is_active=False)
        # создаем confirmation code и отправляем на почту
        create_confirmation_code_and_send_email(
            data['username'], data['email'])
        return Response(
            {'email': data['email'],
             'username': data['username']},
            status=status.HTTP_200_OK)
