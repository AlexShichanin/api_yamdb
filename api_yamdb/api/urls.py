from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (APISignUp, APIToken, APIUser, CategoryViewSet,
                    CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet,
                    UserViewSetForAdmin)

router_v1 = DefaultRouter()

router_v1.register(r'users', UserViewSetForAdmin, basename='users')
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoryViewSet, basename='category')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/users/me/', APIUser.as_view(), name='me'),
    path('v1/auth/signup/',
         APISignUp.as_view(), name='signup'),
    path('v1/auth/token/',
         APIToken.as_view(), name='token'),
    path('v1/', include(router_v1.urls)),
]
