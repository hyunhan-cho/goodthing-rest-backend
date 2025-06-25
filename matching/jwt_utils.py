# matching/jwt_utils.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # JWT 페이로드에 사용자 정보 추가
        token['userId'] = user.id
        token['role'] = user.role
        token['name'] = user.name
        token['mileagePoints'] = user.mileagePoints
        
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
