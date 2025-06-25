# matching/permissions.py
from rest_framework import permissions




class IsSeniorUser(permissions.BasePermission):
    """
    시니어 사용자만 접근 가능한 권한
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'senior'


class IsHelperUser(permissions.BasePermission):
    """
    도우미 사용자만 접근 가능한 권한
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'helper'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체의 소유자만 수정 가능하고, 다른 사용자는 읽기만 가능한 권한
    """
    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모든 인증된 사용자에게 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 쓰기 권한은 객체의 소유자에게만 허용
        return obj.userId == request.user


class IsRequestOwnerOrHelper(permissions.BasePermission):
    """
    요청의 소유자이거나 도우미인 경우 접근 가능한 권한
    """
    def has_object_permission(self, request, view, obj):
        # 요청 소유자는 모든 권한
        if hasattr(obj, 'userId') and obj.userId == request.user:
            return True
        
        # 도우미는 읽기 권한만
        if request.user.role == 'helper' and request.method in permissions.SAFE_METHODS:
            return True
        
        return False


class IsProposalOwnerOrRequestOwner(permissions.BasePermission):
    """
    제안의 소유자이거나 요청의 소유자인 경우 접근 가능한 권한
    """
    def has_object_permission(self, request, view, obj):
        # 제안 작성자
        if hasattr(obj, 'helperId') and obj.helperId == request.user:
            return True
        
        # 요청 작성자
        if hasattr(obj, 'requestId') and obj.requestId.userId == request.user:
            return True
        
        return False


