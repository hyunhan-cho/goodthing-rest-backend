# matching/views.py
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import User, Request, Proposal, Team, Game
from .serializers import (
    RegisterSerializer, LoginSerializer, UserProfileSerializer,
    RequestSerializer, RequestCreateSerializer, ProposalSerializer,
    ProposalCreateSerializer, TeamSerializer, GameSerializer,
    MyPageRequestSerializer, MyPageProposalSerializer
)
from .permissions import (
    IsSeniorUser, IsHelperUser, IsOwnerOrReadOnly,
    IsRequestOwnerOrHelper, IsProposalOwnerOrRequestOwner
)
from .jwt_utils import CustomTokenObtainPairView

# --- V V V RequestCreateView 로직 수정 V V V ---
class RequestCreateView(generics.CreateAPIView):
    """요청 생성 (시니어용)"""
    serializer_class = RequestCreateSerializer
    permission_classes = [IsSeniorUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            # 1. 프론트에서 받은 teamId ('lg', 'doosan' 등)로 Team 객체를 찾음
            team = get_object_or_404(Team, string_id=validated_data['teamId'])
            
            # 2. 찾은 Team 객체와 날짜로 Game 객체를 찾음
            game = Game.objects.filter(
                Q(homeTeam=team) | Q(awayTeam=team),
                date=validated_data['gameDate']
            ).first()

            if not game:
                return Response({"error": "해당 날짜에 요청하신 팀의 경기가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # 3. Request 객체 생성
            request_obj = Request.objects.create(
                userId=request.user,
                game=game,
                gameDate=game.date,
                gameTime=game.time,
                homeTeam=game.homeTeam.name,
                awayTeam=game.awayTeam.name,
                stadium=game.stadium,
                numberOfTickets=validated_data['numberOfTickets'],
                accompanyType=validated_data.get('accompanyType', 'ticket_only'),
                additionalInfo=validated_data.get('additionalInfo', ''),
                seatType='일반석'  # 기본값
            )            # 4. 생성된 Request를 RequestSerializer로 직렬화하여 응답
            response_serializer = RequestSerializer(request_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Team.DoesNotExist:
            return Response({"error": "존재하지 않는 팀입니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"요청 생성 중 서버 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- 이하 View들을 완성합니다 ---
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(CustomTokenObtainPairView):
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_phone(request):
    """전화번호 인증"""
    phone = request.data.get('phone')
    if not phone:
        return Response({'error': '전화번호가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 실제 구현에서는 SMS 인증 로직이 들어가야 함
    # 현재는 임시로 성공 응답만 반환
    return Response({
        'success': True,
        'message': '인증번호가 발송되었습니다.',
        'verificationCode': '123456'  # 개발용 고정값
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_code(request):
    """인증번호 확인"""
    phone = request.data.get('phone')
    code = request.data.get('code')
    
    if not phone or not code:
        return Response({'error': '전화번호와 인증번호가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 실제 구현에서는 인증번호 검증 로직이 들어가야 함
    # 현재는 임시로 성공 응답만 반환
    if code == '123456':  # 개발용 고정값
        return Response({'success': True, 'message': '인증이 완료되었습니다.'})
    else:
        return Response({'error': '잘못된 인증번호입니다.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class TeamListView(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]


class GameListView(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Game.objects.all()
        date = self.request.query_params.get('date')
        team = self.request.query_params.get('team')
        
        if date:
            queryset = queryset.filter(date=date)
        if team:
            queryset = queryset.filter(
                Q(homeTeam__name=team) | Q(awayTeam__name=team)
            )
        
        return queryset.order_by('date', 'time')


class RequestListView(generics.ListAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsHelperUser]
    
    def get_queryset(self):
        queryset = Request.objects.filter(status='pending')
        
        # 필터링 옵션
        game_date = self.request.query_params.get('gameDate')
        team = self.request.query_params.get('team')
        stadium = self.request.query_params.get('stadium')
        accompany_type = self.request.query_params.get('accompanyType')
        
        if game_date:
            queryset = queryset.filter(gameDate=game_date)
        if team:
            queryset = queryset.filter(Q(homeTeam=team) | Q(awayTeam=team))
        if stadium:
            queryset = queryset.filter(stadium=stadium)
        if accompany_type:
            queryset = queryset.filter(accompanyType=accompany_type)
        
        return queryset.order_by('-createdAt')


class RequestDetailView(generics.RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsRequestOwnerOrHelper]
    lookup_field = 'requestId'


class RequestUpdateView(generics.UpdateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'requestId'


class RequestDeleteView(generics.DestroyAPIView):
    queryset = Request.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'requestId'


class ProposalListView(generics.ListAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        request_id = self.kwargs['request_id']
        request_obj = get_object_or_404(Request, requestId=request_id)
        
        # 요청 소유자만 제안 목록을 볼 수 있음
        if request_obj.userId != self.request.user:
            return Proposal.objects.none()
        
        return Proposal.objects.filter(requestId=request_obj).order_by('-createdAt')


class ProposalCreateView(generics.CreateAPIView):
    serializer_class = ProposalCreateSerializer
    permission_classes = [IsHelperUser]
    
    def perform_create(self, serializer):
        request_id = self.kwargs['request_id']
        request_obj = get_object_or_404(Request, requestId=request_id)
        
        # 이미 제안했는지 확인
        if Proposal.objects.filter(requestId=request_obj, helperId=self.request.user).exists():
            from rest_framework import serializers
            raise serializers.ValidationError("이미 제안하신 요청입니다.")
        
        serializer.save(requestId=request_obj, helperId=self.request.user)


class ProposalDetailView(generics.RetrieveAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated, IsProposalOwnerOrRequestOwner]
    lookup_field = 'proposalId'


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_proposal(request, proposal_id):
    """제안 수락"""
    proposal = get_object_or_404(Proposal, proposalId=proposal_id)
    
    # 요청 소유자만 수락 가능
    if proposal.requestId.userId != request.user:
        return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    # 이미 수락된 제안이 있는지 확인
    if proposal.requestId.status != 'pending':
        return Response({'error': '이미 처리된 요청입니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 제안 수락 처리
    proposal.status = 'accepted'
    proposal.save()
    
    # 요청 상태 변경
    proposal.requestId.status = 'accepted'
    proposal.requestId.save()
    
    # 다른 제안들은 자동으로 거절 처리
    Proposal.objects.filter(
        requestId=proposal.requestId
    ).exclude(
        proposalId=proposal.proposalId
    ).update(status='rejected')
    
    return Response({'message': '제안이 수락되었습니다.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_proposal(request, proposal_id):
    """제안 거절"""
    proposal = get_object_or_404(Proposal, proposalId=proposal_id)
    
    # 요청 소유자만 거절 가능
    if proposal.requestId.userId != request.user:
        return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    proposal.status = 'rejected'
    proposal.save()
    
    return Response({'message': '제안이 거절되었습니다.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_request(request, request_id):
    """요청 완료 처리"""
    request_obj = get_object_or_404(Request, requestId=request_id)
    
    # 요청 소유자만 완료 처리 가능
    if request_obj.userId != request.user:
        return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    if request_obj.status != 'accepted':
        return Response({'error': '수락된 요청만 완료 처리할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 요청 완료 처리
    request_obj.status = 'completed'
    request_obj.save()
    
    # 수락된 제안도 완료 처리
    Proposal.objects.filter(
        requestId=request_obj,
        status='accepted'
    ).update(status='completed')
    
    # 마일리지 적립 (시니어 +10, 도우미 +20)
    request_obj.userId.mileagePoints += 10
    request_obj.userId.save()
    
    accepted_proposal = Proposal.objects.filter(
        requestId=request_obj,
        status='completed'
    ).first()
    
    if accepted_proposal:
        accepted_proposal.helperId.mileagePoints += 20
        accepted_proposal.helperId.save()
    
    return Response({'message': '요청이 완료되었습니다.'})


class MyRequestsView(generics.ListAPIView):
    serializer_class = MyPageRequestSerializer
    permission_classes = [IsSeniorUser]
    
    def get_queryset(self):
        return Request.objects.filter(userId=self.request.user).order_by('-createdAt')


class MyProposalsView(generics.ListAPIView):
    serializer_class = MyPageProposalSerializer
    permission_classes = [IsHelperUser]
    
    def get_queryset(self):
        return Proposal.objects.filter(helperId=self.request.user).order_by('-createdAt')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_stats(request):
    """내 통계 정보"""
    user = request.user
    
    if user.role == 'senior':
        total_requests = Request.objects.filter(userId=user).count()
        completed_requests = Request.objects.filter(userId=user, status='completed').count()
        pending_requests = Request.objects.filter(userId=user, status='pending').count()
        
        stats = {
            'totalRequests': total_requests,
            'completedRequests': completed_requests,
            'pendingRequests': pending_requests,
            'mileagePoints': user.mileagePoints
        }
    else:  # helper
        total_proposals = Proposal.objects.filter(helperId=user).count()
        accepted_proposals = Proposal.objects.filter(helperId=user, status='accepted').count()
        completed_proposals = Proposal.objects.filter(helperId=user, status='completed').count()
        
        stats = {
            'totalProposals': total_proposals,
            'acceptedProposals': accepted_proposals,
            'completedProposals': completed_proposals,
            'mileagePoints': user.mileagePoints
        }
    
    return Response(stats)