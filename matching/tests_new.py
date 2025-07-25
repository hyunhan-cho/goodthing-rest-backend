# matching/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Profile, Request, Proposal, Team, Game
from datetime import date, time, timedelta
from django.utils import timezone
import json

User = get_user_model()


class AuthenticationAPITestCase(APITestCase):
    """인증 관련 API 테스트"""
    
    def setUp(self):
        """테스트 전 준비 작업"""
        self.client = APIClient()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        
        # 기존 사용자 생성
        self.test_user = User.objects.create_user(
            username='01012345678',
            phone='01012345678',
            password='testpass123',
            name='테스트유저',
            role='senior'
        )

    def test_user_registration(self):
        """회원가입 테스트"""
        data = {
            'name': '새유저',
            'phone': '01087654321',
            'role': 'helper',
            'password': 'newpass123',
            'nickname': '새도우미',
            'favorite_team': '두산 베어스'
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(phone='01087654321').exists())
        
        # 프로필 자동 생성 확인
        user = User.objects.get(phone='01087654321')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.nickname, '새도우미')

    def test_user_login(self):
        """로그인 테스트"""
        data = {
            'phone': '01012345678',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_phone_registration(self):
        """잘못된 전화번호로 회원가입 테스트"""
        data = {
            'name': '테스트',
            'phone': '1234567890',  # 잘못된 형식
            'role': 'senior',
            'password': 'testpass123'
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_phone_registration(self):
        """중복 전화번호로 회원가입 테스트"""
        data = {
            'name': '또다른유저',
            'phone': '01012345678',  # 이미 존재하는 번호
            'role': 'helper',
            'password': 'testpass123'
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileAPITestCase(APITestCase):
    """사용자 프로필 관련 API 테스트"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='01012345678',
            phone='01012345678',
            password='testpass123',
            name='테스트유저',
            role='senior'
        )
        
    def get_auth_token(self):
        """인증 토큰 획득"""
        login_data = {'phone': '01012345678', 'password': 'testpass123'}
        response = self.client.post(reverse('login'), login_data, format='json')
        return response.data['access']
    
    def test_profile_access_without_auth(self):
        """인증 없이 프로필 접근 테스트"""
        response = self.client.get(reverse('user_profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_access_with_auth(self):
        """인증 후 프로필 접근 테스트"""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        response = self.client.get(reverse('user_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '테스트유저')
        self.assertEqual(response.data['role'], 'senior')
    
    def test_profile_update(self):
        """프로필 수정 테스트"""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        update_data = {
            'name': '수정된이름',
            'profile': {
                'nickname': '수정된닉네임',
                'favorite_team': 'KIA 타이거즈'
            }
        }
        
        response = self.client.put(reverse('user_profile'), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 데이터 확인
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, '수정된이름')
        self.assertEqual(self.user.profile.nickname, '수정된닉네임')
        self.assertEqual(self.user.profile.favorite_team, 'KIA 타이거즈')


class RequestAPITestCase(APITestCase):
    """요청 관련 API 테스트"""
    
    def setUp(self):
        self.client = APIClient()
        
        # 시니어 사용자
        self.senior_user = User.objects.create_user(
            username='01012345678',
            phone='01012345678',
            password='testpass123',
            name='김시니어',
            role='senior'
        )
        
        # 도우미 사용자
        self.helper_user = User.objects.create_user(
            username='01087654321',
            phone='01087654321',
            password='testpass123',
            name='이도우미',
            role='helper'
        )
        
        # 팀 데이터
        self.team1 = Team.objects.create(name='LG 트윈스', stadium='잠실야구장')
        self.team2 = Team.objects.create(name='두산 베어스', stadium='잠실야구장')
    
    def get_auth_token(self, phone, password):
        """인증 토큰 획득"""
        login_data = {'phone': phone, 'password': password}
        response = self.client.post(reverse('login'), login_data, format='json')
        return response.data['access']
    
    def test_request_creation_by_senior(self):
        """시니어가 요청 생성 테스트"""
        token = self.get_auth_token('01012345678', 'testpass123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        request_data = {
            'gameDate': '2024-07-15',
            'gameTime': '18:30:00',
            'homeTeam': 'LG 트윈스',
            'awayTeam': '두산 베어스',
            'stadium': '잠실야구장',
            'seatType': '1루 블루석',
            'accompanyType': 'with',
            'additionalInfo': '휠체어 접근 가능한 좌석 희망'
        }
        
        response = self.client.post(reverse('request_create'), request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 요청 생성 확인
        request_obj = Request.objects.get(userId=self.senior_user)
        self.assertEqual(request_obj.homeTeam, 'LG 트윈스')
        self.assertEqual(request_obj.status, 'pending')
    
    def test_request_creation_by_helper_should_fail(self):
        """도우미가 요청 생성 시 실패 테스트"""
        token = self.get_auth_token('01087654321', 'testpass123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        request_data = {
            'gameDate': '2024-07-15',
            'gameTime': '18:30:00',
            'homeTeam': 'LG 트윈스',
            'awayTeam': '두산 베어스',
            'stadium': '잠실야구장',
            'seatType': '1루 블루석',
            'accompanyType': 'with'
        }
        
        response = self.client.post(reverse('request_create'), request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_request_list_by_helper(self):
        """도우미가 요청 목록 조회 테스트"""
        # 요청 생성
        Request.objects.create(
            userId=self.senior_user,
            gameDate=date.today() + timedelta(days=1),
            gameTime=time(18, 30),
            homeTeam='LG 트윈스',
            awayTeam='두산 베어스',
            stadium='잠실야구장',
            seatType='1루 블루석',
            accompanyType='with'
        )
        
        token = self.get_auth_token('01087654321', 'testpass123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        response = self.client.get(reverse('request_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['homeTeam'], 'LG 트윈스')


class ModelTestCase(TestCase):
    """모델 테스트"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='01012345678',
            phone='01012345678',
            password='testpass123',
            name='테스트유저',
            role='senior'
        )
    
    def test_user_creation(self):
        """사용자 생성 테스트"""
        self.assertEqual(self.user.phone, '01012345678')
        self.assertEqual(self.user.name, '테스트유저')
        self.assertEqual(self.user.role, 'senior')
        self.assertEqual(self.user.mileagePoints, 0)
    
    def test_profile_auto_creation(self):
        """프로필 자동 생성 테스트"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)
    
    def test_request_creation(self):
        """요청 생성 테스트"""
        request_obj = Request.objects.create(
            userId=self.user,
            gameDate=date.today() + timedelta(days=1),
            gameTime=time(18, 30),
            homeTeam='LG 트윈스',
            awayTeam='두산 베어스',
            stadium='잠실야구장',
            seatType='1루 블루석',
            accompanyType='with'
        )
        
        self.assertEqual(request_obj.userId, self.user)
        self.assertEqual(request_obj.status, 'pending')
        self.assertEqual(str(request_obj), f'[대기중] {self.user.name} - LG 트윈스 vs 두산 베어스 ({request_obj.gameDate})')
