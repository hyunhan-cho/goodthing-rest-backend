# matching/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 인증 관련
    path('auth/signup/', views.SignupView.as_view(), name='signup'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/verify-phone/', views.verify_phone, name='verify_phone'),
    path('auth/verify-code/', views.verify_code, name='verify_code'),
    
    # 사용자 프로필
    path('users/me/', views.UserProfileView.as_view(), name='user_profile'),
    
    # 팀 및 경기 정보
    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('games/', views.GameListView.as_view(), name='game_list'),
    
    # 요청 관련
    path('requests/', views.RequestListView.as_view(), name='request_list'),
    path('requests/create/', views.RequestCreateView.as_view(), name='request_create'),
    path('requests/<int:requestId>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:requestId>/update/', views.RequestUpdateView.as_view(), name='request_update'),
    path('requests/<int:requestId>/delete/', views.RequestDeleteView.as_view(), name='request_delete'),
    path('requests/<int:request_id>/complete/', views.complete_request, name='complete_request'),
    
    # 제안 관련
    path('requests/<int:request_id>/proposals/', views.ProposalListView.as_view(), name='proposal_list'),
    path('requests/<int:request_id>/proposals/create/', views.ProposalCreateView.as_view(), name='proposal_create'),
    path('proposals/<int:proposalId>/', views.ProposalDetailView.as_view(), name='proposal_detail'),
    path('proposals/<int:proposal_id>/accept/', views.accept_proposal, name='accept_proposal'),
    path('proposals/<int:proposal_id>/reject/', views.reject_proposal, name='reject_proposal'),
    
    # 마이페이지
    path('mypage/requests/', views.MyRequestsView.as_view(), name='my_requests'),
    path('mypage/proposals/', views.MyProposalsView.as_view(), name='my_proposals'),
    path('mypage/stats/', views.my_stats, name='my_stats'),
]