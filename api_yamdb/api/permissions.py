from rest_framework import permissions


class IsAdminOrSuperUser(permissions.BasePermission):
    """Доступ админу и суперюзеру, для эндпоинта 'users'."""

    def has_permission(self, request, view):
        """Определяет права на уровне запроса и пользователя."""
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ только администратору или чтение."""

    def has_permission(self, request, view):
        """Определяет права на уровне запроса и пользователя."""
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin))


class IsModerator(permissions.BasePermission):
    """Доступ только модератору."""

    def has_permission(self, request, view):
        """Определяет права на уровне запроса и пользователя."""
        return request.user.is_authenticated and request.user.is_moderator


class IsUser(permissions.BasePermission):
    """Доступ только пользовавтелю."""

    def has_permission(self, request, view):
        """Определяет права на уровне запроса и пользователя."""
        return request.user.is_authenticated and request.user.is_user


class IsOwner(permissions.BasePermission):
    """Автор, модератор, админ или только чтение."""

    def has_permission(self, request, view):
        """Определяет права на уровне запроса и пользователя."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Определяет права на уровне запроса и пользователя."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
