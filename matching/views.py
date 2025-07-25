from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Request, Proposal, Team, Game
from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    RequestSerializer, RequestCreateSerializer, ProposalSerializer,
    ProposalCreateSerializer, TeamSerializer, GameSerializer,
    MyPageRequestSerializer, MyPageProposalSerializer, HelpRequestSerializer,
    ProposedTicketDetailsSerializer
)
from .permissions import (
    IsSeniorUser, IsHelperUser, IsOwnerOrReadOnly,
    IsRequestOwnerOrHelper, IsProposalOwnerOrRequestOwner
)

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone or not password:
            return Response({'detail': '전화번호와 비밀번호를 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, phone=phone)

        if not user.check_password(password):
            return Response({'detail': '비밀번호가 올바르지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token['role'] = user.role
        access_token['userId'] = user.id
        access_token['name'] = user.name
        access_token['mileagePoints'] = user.mileagePoints

        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'detail': '존재하지 않는 사용자입니다.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'서버 오류: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

class TeamListView(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [AllowAny]

class GameListView(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 쿼리 파라미터에서 gameId, date, team을 가져옵니다.
        game_id = self.request.query_params.get('gameId', None)
        date = self.request.query_params.get('date', None)
        team_id = self.request.query_params.get('team', None) # 'team' 파라미터는 팀의 ID로 가정

        # gameId로 필터링 (단일 경기 조회 시)
        if game_id:
            # gameId는 일반적으로 PK이므로 get()을 사용하여 단일 객체를 가져오는 것이 더 명확할 수 있으나,
            # list view의 get_queryset에서는 filter()를 유지하는 것이 일반적입니다.
            queryset = queryset.filter(gameId=game_id)
            # 단일 객체만 원한다면 .first()를 여기서 호출하거나, 프론트엔드에서 [0]을 사용하는 방식 유지
            
        # 날짜로 필터링 (특정 날짜의 모든 경기 조회 시)
        if date:
            queryset = queryset.filter(date=date)

        # 팀 ID로 필터링 (특정 팀이 홈 또는 어웨이인 경기 조회 시)
        if team_id:
            queryset = queryset.filter(Q(homeTeam__teamId=team_id) | Q(awayTeam__teamId=team_id))

        return queryset

class RequestCreateView(generics.CreateAPIView):
    serializer_class = RequestCreateSerializer
    permission_classes = [IsSeniorUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            team = get_object_or_404(Team, pk=data['teamId'])
            game_date = data['gameDate']
            game = Game.objects.filter(Q(homeTeam=team) | Q(awayTeam=team), date=game_date).first()
            if not game:
                return Response({"detail": "해당 날짜에 요청하신 팀의 경기가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
            request_obj = Request.objects.create(
                userId=request.user, game=game, numberOfTickets=data['numberOfTickets']
            )
            response_serializer = RequestSerializer(request_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Team.DoesNotExist:
            return Response({"detail": "존재하지 않는 팀 ID입니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"요청 생성 중 오류 발생: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HelpRequestListView(generics.ListAPIView):
    serializer_class = HelpRequestSerializer
    permission_classes = [IsHelperUser]
    def get_queryset(self):
        return Request.objects.filter(status='WAITING_FOR_HELPER').order_by('-createdAt')

class RequestDetailView(generics.RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated, IsRequestOwnerOrHelper]
    lookup_field = 'requestId'

class RequestUpdateView(generics.UpdateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestCreateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'requestId'

class RequestDeleteView(generics.DestroyAPIView):
    queryset = Request.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'requestId'

class ProposalListView(generics.ListAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        request_obj = get_object_or_404(Request, requestId=self.kwargs['request_id'])
        if request_obj.userId != self.request.user:
            return Proposal.objects.none()
        return Proposal.objects.filter(requestId=request_obj).order_by('-createdAt')

class ProposalCreateView(generics.CreateAPIView):
    serializer_class = ProposalCreateSerializer
    permission_classes = [IsHelperUser]
    def perform_create(self, serializer):
        request_obj = get_object_or_404(Request, requestId=self.kwargs['request_id'])
        if Proposal.objects.filter(requestId=request_obj, helperId=self.request.user).exists():
            raise serializers.ValidationError("이미 제안하신 요청입니다.")
        serializer.save(requestId=request_obj, helperId=self.request.user)
        request_obj.status = 'TICKET_PROPOSED'
        request_obj.save()

class ProposalDetailView(generics.RetrieveAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated, IsProposalOwnerOrRequestOwner]
    lookup_field = 'proposalId'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, proposalId=proposal_id)
    if proposal.requestId.userId != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    if proposal.requestId.status != 'TICKET_PROPOSED':
        return Response({'detail': '이미 처리된 요청입니다.'}, status=status.HTTP_400_BAD_REQUEST)
    proposal.status = 'accepted'
    proposal.save()
    proposal.requestId.status = 'HELPER_MATCHED' 
    proposal.requestId.save()
    Proposal.objects.filter(requestId=proposal.requestId).exclude(proposalId=proposal.proposalId).update(status='rejected')
    return Response({'message': '제안이 수락되었습니다.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, proposalId=proposal_id)
    if proposal.requestId.userId != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    proposal.status = 'rejected'
    proposal.save()
    return Response({'message': '제안이 거절되었습니다.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_request(request, request_id):
    request_obj = get_object_or_404(Request, requestId=request_id)
    if request_obj.userId != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    if request_obj.status != 'SEAT_CONFIRMED':
        return Response({'detail': '좌석이 확정된 요청만 완료 처리할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    request_obj.status = 'COMPLETED'
    request_obj.save()
    accepted_proposal = request_obj.proposals.filter(status='accepted').first()
    if accepted_proposal:
        accepted_proposal.helperId.mileagePoints += 20
        accepted_proposal.helperId.save()
    request_obj.userId.mileagePoints += 10
    request_obj.userId.save()
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
@permission_classes([IsAuthenticated])
def my_stats(request):
    user = request.user
    if user.role == 'senior':
        stats = {
            'totalRequests': Request.objects.filter(userId=user).count(),
            'completedRequests': Request.objects.filter(userId=user, status='COMPLETED').count(),
        }
    else: # helper
        stats = {
            'totalSessionsCompleted': Proposal.objects.filter(helperId=user, status='accepted', requestId__status='COMPLETED').count(),
            'mileagePoints': user.mileagePoints
        }
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_proposed_ticket_details(request, requestId):
    request_obj = get_object_or_404(Request, requestId=requestId)
    if request_obj.userId != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ProposedTicketDetailsSerializer(request_obj)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_proposed_ticket(request, requestId):
    request_obj = get_object_or_404(Request, requestId=requestId)
    if request_obj.userId != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    if request_obj.status != 'TICKET_PROPOSED':
         return Response({'detail': f'좌석을 확정할 수 있는 상태가 아닙니다. 현재 상태: {request_obj.status}'}, status=status.HTTP_400_BAD_REQUEST)
    request_obj.status = 'SEAT_CONFIRMED'
    request_obj.save()
    
    proposal_to_accept = request_obj.proposals.order_by('-createdAt').first()
    if proposal_to_accept:
        proposal_to_accept.status = 'accepted'
        proposal_to_accept.save()

    return Response({'message': '좌석이 확정되었습니다.'}, status=status.HTTP_200_OK)
