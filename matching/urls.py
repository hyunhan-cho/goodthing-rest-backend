# matching/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 인증 (Authentication)
    path('auth/signup/', views.SignupView.as_view(), name='signup'), # registration -> signup
    path('auth/login/', views.login_view, name='login'),
    path('auth/user/', views.UserProfileView.as_view(), name='user_profile'),
    
    # KBO 팀 및 경기 정보
    path('kbo-teams/', views.TeamListView.as_view(), name='kbo_team_list'),
    path('games/', views.GameListView.as_view(), name='game_list'),
    
    # 도움 요청 (시니어 -> 헬퍼)
    path('reservation-requests/', views.RequestCreateView.as_view(), name='request_create'),
    path('help-requests/', views.HelpRequestListView.as_view(), name='help_request_list'),
    path('requests/<int:requestId>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:requestId>/update/', views.RequestUpdateView.as_view(), name='request_update'),
    path('requests/<int:requestId>/delete/', views.RequestDeleteView.as_view(), name='request_delete'),
    path('requests/<int:request_id>/complete/', views.complete_request, name='complete_request'),
    
    # 제안 (헬퍼 -> 시니어)
    path('requests/<int:request_id>/proposals/', views.ProposalListView.as_view(), name='proposal_list'),
    path('requests/<int:request_id>/proposals/create/', views.ProposalCreateView.as_view(), name='proposal_create'),
    path('proposals/<int:proposalId>/', views.ProposalDetailView.as_view(), name='proposal_detail'),
    path('proposals/<int:proposal_id>/accept/', views.accept_proposal, name='accept_proposal'),
    path('proposals/<int:proposal_id>/reject/', views.reject_proposal, name='reject_proposal'),
    
    # 마이페이지
    path('senior/requests/', views.MyRequestsView.as_view(), name='senior_my_requests'),
    path('helper/activities/', views.MyProposalsView.as_view(), name='helper_my_activities'),
    path('helper/stats/', views.my_stats, name='helper_my_stats'),
    path('mypage/stats/', views.my_stats, name='my_stats'),

    # 시니어 티켓 확인 및 확정
    path('senior/requests/<int:requestId>/proposed-ticket/', views.get_proposed_ticket_details, name='get_proposed_ticket_details'),
    path('senior/requests/<int:requestId>/confirm-ticket/', views.confirm_proposed_ticket, name='confirm_proposed_ticket'),
]
