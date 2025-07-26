from rest_framework import serializers
from .models import User, Profile, Request, Proposal, Team, Game
import re

# -------------------- User 관련 Serializer --------------------

class UserSerializer(serializers.ModelSerializer):
    """
    User 모델의 기본 정보 Serializer.
    - 주로 다른 Serializer 안에서 User를 보여줄 때 사용.
    """
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'mileagePoints']
        # read_only_fields → 수정 불가 필드 (id, 마일리지)
        read_only_fields = ['id', 'mileagePoints']


class ProfileSerializer(serializers.ModelSerializer):
    """
    User의 Profile (닉네임, 관심팀 등) 정보 Serializer
    """
    class Meta:
        model = Profile
        fields = ['nickname', 'favorite_team', 'verification_info']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User + Profile을 합쳐서 업데이트 가능하게 만든 Serializer
    - profile: 중첩된 Serializer(ProfileSerializer)
    - update: profile까지 같이 업데이트 가능하도록 커스텀
    """
    profile = ProfileSerializer()
    
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'mileagePoints', 'profile']
        read_only_fields = ['id', 'phone', 'role', 'mileagePoints']
    
    def update(self, instance, validated_data):
        """
        user와 profile을 함께 업데이트
        """
        profile_data = validated_data.pop('profile', {})  # profile 데이터 추출
        # User 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Profile 필드 업데이트
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """
    회원가입용 Serializer
    - password, nickname, favorite_team 등을 함께 저장
    """
    password = serializers.CharField(write_only=True, min_length=6)
    nickname = serializers.CharField(write_only=True, max_length=50, required=False)
    favorite_team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), required=False, allow_null=True, write_only=True
    )
    
    class Meta:
        model = User
        fields = ['name', 'phone', 'role', 'password', 'nickname', 'favorite_team']
    
    def create(self, validated_data):
        """
        User 생성 시 profile 정보도 함께 설정
        """
        favorite_team_obj = validated_data.pop('favorite_team', None)
        nickname = validated_data.pop('nickname', '')
        user = User.objects.create_user(**validated_data)

        # profile 저장
        if nickname:
            user.profile.nickname = nickname
        if favorite_team_obj:
            user.profile.favorite_team = favorite_team_obj
        user.profile.save()
        return user


# -------------------- Team / Game 관련 Serializer --------------------

class TeamSerializer(serializers.ModelSerializer):
    """
    Team 모델 Serializer (프론트 요구에 맞춰 필드명 변경)
    - teamId → id
    - name → shortName (별칭), name(실제 이름)
    - stadium → homeStadium
    - logo → logoUrl
    """
    id = serializers.IntegerField(source='teamId', read_only=True)
    name = serializers.CharField(source='name', read_only=True)
    shortName = serializers.CharField(source='name', read_only=True)
    logoUrl = serializers.CharField(source='logo', read_only=True)
    homeStadium = serializers.CharField(source='stadium', read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'shortName', 'logoUrl', 'homeStadium']


class GameSerializer(serializers.ModelSerializer):
    """
    Game 모델 Serializer
    - homeTeam, awayTeam은 TeamSerializer로 상세 정보 포함
    """
    homeTeam = TeamSerializer(read_only=True)
    awayTeam = TeamSerializer(read_only=True)
    
    class Meta:
        model = Game
        fields = ['gameId', 'date', 'time', 'homeTeam', 'awayTeam', 'stadium']


# -------------------- Request 관련 Serializer --------------------

class RequestSerializer(serializers.ModelSerializer):
    """
    Request(티켓 요청) Serializer
    - userId → UserSerializer로 보여줌
    - game → GameSerializer로 상세 정보 포함
    """
    userId = UserSerializer(read_only=True)
    game = GameSerializer(read_only=True)
    
    class Meta:
        model = Request
        fields = [
            'requestId', 'userId', 'game', 'accompanyType', 'additionalInfo', 'status',
            'numberOfTickets', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['requestId', 'userId', 'status', 'createdAt', 'updatedAt']


class RequestCreateSerializer(serializers.Serializer):
    """
    Request 생성 전용 Serializer
    - 단순 필드 검증용 (RequestSerializer는 읽기 전용 필드가 많아서 분리)
    """
    teamId = serializers.IntegerField()
    gameDate = serializers.DateField()
    numberOfTickets = serializers.IntegerField(min_value=1, max_value=4)


class HelpRequestSerializer(serializers.ModelSerializer):
    """
    Helper(도우미)가 볼 수 있는 Request 리스트 Serializer
    - user 이름, 팀 이름, 경기 시간 등만 간략하게 보여줌
    """
    id = serializers.IntegerField(source='requestId', read_only=True)
    seniorFanName = serializers.CharField(source='userId.name', read_only=True)
    teamName = serializers.CharField(source='game.homeTeam.name', read_only=True)
    gameDate = serializers.DateField(source='game.date', read_only=True)
    gameTime = serializers.TimeField(source='game.time', read_only=True, format='%H:%M')

    class Meta:
        model = Request
        fields = [
            'id', 'seniorFanName', 'teamName', 'gameDate', 'gameTime',
            'numberOfTickets', 'status'
        ]


# -------------------- Proposal 관련 Serializer --------------------

class ProposalSerializer(serializers.ModelSerializer):
    """
    Proposal(도우미 제안) Serializer
    - helperId → UserSerializer로 표시
    - requestId → RequestSerializer로 표시
    """
    helperId = UserSerializer(read_only=True)
    requestId = RequestSerializer(read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'proposalId', 'requestId', 'helperId', 'seatType', 'totalPrice', 'message',
            'status', 'createdAt', 'updatedAt'
        ]


class ProposalCreateSerializer(serializers.ModelSerializer):
    """
    Proposal 생성 전용 Serializer
    """
    class Meta:
        model = Proposal
        fields = ['seatType', 'totalPrice', 'message']


# -------------------- MyPage(내 요청 / 내 제안) --------------------

class MyPageRequestSerializer(serializers.ModelSerializer):
    """
    시니어의 '내 요청' 리스트 Serializer
    - 팀 이름, 날짜, 도우미 이름(매칭된 경우) 표시
    """
    teamName = serializers.CharField(source='game.homeTeam.name', read_only=True)
    matchDate = serializers.DateField(source='game.date', read_only=True)
    helperName = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = [
            'id', 'teamName', 'matchDate', 'numberOfTickets', 'status', 'helperName'
        ]
        extra_kwargs = {'id': {'source': 'requestId'}}
    
    def get_helperName(self, obj):
        """
        accepted 상태인 Proposal이 있으면 헬퍼 이름 가져옴
        """
        accepted_proposal = obj.proposals.filter(status='accepted').first()
        return accepted_proposal.helperId.name if accepted_proposal else None


class ProposedTicketDetailsSerializer(serializers.ModelSerializer):
    """
    도우미가 제안한 티켓 정보 상세보기 Serializer
    - pending 상태의 제안 중 가장 최신 제안을 가져옴
    """
    id = serializers.IntegerField(source='requestId', read_only=True)
    seniorFanName = serializers.CharField(source='userId.name', read_only=True)
    teamName = serializers.CharField(source='game.homeTeam.name', read_only=True)
    matchDate = serializers.DateField(source='game.date', read_only=True)
    helperName = serializers.SerializerMethodField()
    seatType = serializers.SerializerMethodField()
    totalPrice = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = ['id', 'seniorFanName', 'teamName', 'matchDate', 'numberOfTickets', 'seatType', 'totalPrice', 'helperName']

    def get_proposal(self, obj):
        """
        pending 상태 중 최신 proposal 하나 가져오기
        """
        return obj.proposals.filter(status='pending').order_by('-createdAt').first()

    def get_helperName(self, obj):
        proposal = self.get_proposal(obj)
        return proposal.helperId.name if proposal else "헬퍼 정보 없음"

    def get_seatType(self, obj):
        proposal = self.get_proposal(obj)
        return proposal.seatType if proposal else "좌석 정보 없음"

    def get_totalPrice(self, obj):
        proposal = self.get_proposal(obj)
        return proposal.totalPrice if proposal else "가격 정보 없음"


class MyPageProposalSerializer(serializers.ModelSerializer):
    """
    헬퍼의 '내 제안' 리스트 Serializer
    - 내가 제안한 Request 정보 + 제안 상태 보여줌
    """
    request = RequestSerializer(source='requestId', read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'proposalId', 'request', 'seatType', 'totalPrice', 'message',
            'status', 'createdAt', 'updatedAt'
        ]
