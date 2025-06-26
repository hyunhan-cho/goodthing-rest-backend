# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('matching.urls')), # 우리가 만든 API들
    path('api/auth/', include('dj_rest_auth.urls')), # dj-rest-auth의 로그인, 로그아웃, 유저 정보 등
]