from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Profile, MatchRequest, Match
from datetime import datetime, timedelta
from django.utils import timezone
import json


class AuthenticationAPITestCase(APITestCase):
    """인증 관련 API 테스트"""
    
    def setUp(self):
        """테스트 전 준비 작업"""
        self.client = APIClient()
        self.register_url = reverse('signup')
        self.login_url = reverse('token_obtain_pair')
        self.profile_url = reverse('user-profile')
        
        # 기존 사용자 생성
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        Profile.objects.create(
            user=self.test_user,
            nickname='테스트유저',
            favorite_team='LG 트윈스'
        )

    def test_user_registration(self):
        """회원가입 테스트"""
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'nickname': '새유저',
            'favorite_team': '두산 베어스'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Profile.objects.filter(nickname='새유저').exists())

    def test_user_login(self):
        """로그인 테스트"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_profile_access_without_auth(self):
        """인증 없이 프로필 접근 테스트"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile_access_with_auth(self):
        """인증 후 프로필 접근 테스트"""
        # 로그인
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']
        
        # 인증 헤더 설정
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # 프로필 조회
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')


class HelpRequestAPITestCase(APITestCase):
    """도움 요청 관련 API 테스트"""
    
    def setUp(self):
        """테스트 전 준비 작업"""
        self.client = APIClient()
        
        # 테스트 사용자 생성
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        Profile.objects.create(user=self.user1, nickname='유저1', favorite_team='LG 트윈스')
        Profile.objects.create(user=self.user2, nickname='유저2', favorite_team='두산 베어스')
        
        # 테스트용 도움 요청 생성
        self.match_request = MatchRequest.objects.create(
            elderly_user=self.user1,
            game_date=timezone.now() + timedelta(days=7),
            location='잠실야구장',
            status='waiting'
        )
        
        # URL 설정
        self.help_requests_url = reverse('help-request-list-create')
        self.help_request_detail_url = reverse('help-request-detail', kwargs={'pk': self.match_request.pk})
        self.my_requests_url = reverse('my-help-request-status')
        self.login_url = reverse('token_obtain_pair')

    def get_auth_token(self, username, password):
        """인증 토큰 획득"""
        login_data = {'username': username, 'password': password}
        response = self.client.post(self.login_url, login_data, format='json')
        return response.data['access']

    def test_help_request_creation(self):
        """도움 요청 생성 테스트"""
        token = self.get_auth_token('user1', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        data = {
            'game_date': (timezone.now() + timedelta(days=10)).isoformat(),
            'location': '고척돔'
        }
        response = self.client.post(self.help_requests_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_help_request_list(self):
        """도움 요청 목록 조회 테스트"""
        token = self.get_auth_token('user1', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        response = self.client.get(self.help_requests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_help_request_detail(self):
        """도움 요청 상세 조회 테스트"""
        token = self.get_auth_token('user1', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        response = self.client.get(self.help_request_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.match_request.id)

    def test_my_help_requests(self):
        """내 도움 요청 목록 조회 테스트"""
        token = self.get_auth_token('user1', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        response = self.client.get(self.my_requests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # user1이 만든 요청 1개

    def test_unauthorized_access(self):
        """인증 없이 접근 테스트"""
        response = self.client.get(self.help_requests_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TeamAndGameAPITestCase(APITestCase):
    """팀 및 게임 관련 API 테스트"""
    
    def setUp(self):
        """테스트 전 준비 작업"""
        self.client = APIClient()
        self.teams_url = reverse('kbo-teams')
        self.games_url = reverse('game-list')

    def test_teams_list(self):
        """팀 목록 조회 테스트"""
        response = self.client.get(self.teams_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('teams', response.data)
        self.assertTrue(len(response.data['teams']) == 10)  # KBO 10개 팀

    def test_games_list(self):
        """게임 목록 조회 테스트"""
        response = self.client.get(self.games_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)


class ModelTestCase(TestCase):
    """모델 테스트"""
    
    def setUp(self):
        """테스트 전 준비 작업"""
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = Profile.objects.create(
            user=self.user,
            nickname='테스트유저',
            favorite_team='LG 트윈스'
        )

    def test_profile_creation(self):
        """프로필 생성 테스트"""
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.nickname, '테스트유저')
        self.assertEqual(self.profile.favorite_team, 'LG 트윈스')
        self.assertEqual(self.profile.points, 0)  # 기본값

    def test_match_request_creation(self):
        """매칭 요청 생성 테스트"""
        match_request = MatchRequest.objects.create(
            elderly_user=self.user,
            game_date=timezone.now() + timedelta(days=7),
            location='잠실야구장'
        )
        self.assertEqual(match_request.elderly_user, self.user)
        self.assertEqual(match_request.status, 'waiting')  # 기본값

    def test_profile_str_method(self):
        """프로필 __str__ 메소드 테스트"""
        expected_str = f"{self.user.username}의 프로필"
        self.assertEqual(str(self.profile), expected_str)


class IntegrationTestCase(APITestCase):
    """통합 테스트 - 전체 워크플로우 테스트"""
    
    def test_complete_user_workflow(self):
        """전체 사용자 워크플로우 테스트"""
        # 1. 회원가입
        register_data = {
            'username': 'integration_user',
            'password': 'testpass123',
            'nickname': '통합테스트유저',
            'favorite_team': 'KIA 타이거즈'
        }
        register_response = self.client.post(
            reverse('signup'), 
            register_data, 
            format='json'
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # 2. 로그인
        login_data = {
            'username': 'integration_user',
            'password': 'testpass123'
        }
        login_response = self.client.post(
            reverse('token_obtain_pair'), 
            login_data, 
            format='json'
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data['access']

        # 3. 인증 설정
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # 4. 프로필 조회
        profile_response = self.client.get(reverse('user-profile'))
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)

        # 5. 도움 요청 생성
        help_request_data = {
            'game_date': (timezone.now() + timedelta(days=5)).isoformat(),
            'location': '대구삼성라이온즈파크'
        }
        help_response = self.client.post(
            reverse('help-request-list-create'), 
            help_request_data, 
            format='json'
        )
        self.assertEqual(help_response.status_code, status.HTTP_201_CREATED)

        # 6. 내 요청 목록 확인
        my_requests_response = self.client.get(reverse('my-help-request-status'))
        self.assertEqual(my_requests_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(my_requests_response.data), 1)

        # 7. 팀 목록 조회
        teams_response = self.client.get(reverse('kbo-teams'))
        self.assertEqual(teams_response.status_code, status.HTTP_200_OK)
        self.assertIn('KIA 타이거즈', teams_response.data['teams'])
