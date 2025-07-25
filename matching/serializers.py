from rest_framework import serializers
from .models import User, Profile, Request, Proposal, Team, Game
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'mileagePoints']
        read_only_fields = ['id', 'mileagePoints']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['nickname', 'favorite_team', 'verification_info']


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'mileagePoints', 'profile']
        read_only_fields = ['id', 'phone', 'role', 'mileagePoints']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    nickname = serializers.CharField(write_only=True, max_length=50, required=False)
    favorite_team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), required=False, allow_null=True, write_only=True
    )
    
    class Meta:
        model = User
        fields = ['name', 'phone', 'role', 'password', 'nickname', 'favorite_team']
    
    def create(self, validated_data):
        favorite_team_obj = validated_data.pop('favorite_team', None)
        nickname = validated_data.pop('nickname', '')
        user = User.objects.create_user(**validated_data)
        if nickname:
            user.profile.nickname = nickname
        if favorite_team_obj:
            user.profile.favorite_team = favorite_team_obj
        user.profile.save()
        return user


class TeamSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='teamId', read_only=True)
    shortName = serializers.CharField(source='name', read_only=True)
    logoUrl = serializers.URLField(source='logo', read_only=True)
    homeStadium = serializers.CharField(source='stadium', read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'shortName', 'logoUrl', 'homeStadium']


class GameSerializer(serializers.ModelSerializer):
    homeTeam = TeamSerializer(read_only=True)
    awayTeam = TeamSerializer(read_only=True)
    
    class Meta:
        model = Game
        fields = ['gameId', 'date', 'time', 'homeTeam', 'awayTeam', 'stadium']


class RequestSerializer(serializers.ModelSerializer):
    userId = UserSerializer(read_only=True)
    
    class Meta:
        model = Request
        fields = [
            'requestId', 'userId', 'game', 'accompanyType', 'additionalInfo', 'status',
            'numberOfTickets', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['requestId', 'userId', 'status', 'createdAt', 'updatedAt']


class RequestCreateSerializer(serializers.Serializer):
    teamId = serializers.IntegerField()
    gameDate = serializers.DateField()
    numberOfTickets = serializers.IntegerField(min_value=1, max_value=4)


class HelpRequestSerializer(serializers.ModelSerializer):
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


class ProposalSerializer(serializers.ModelSerializer):
    helperId = UserSerializer(read_only=True)
    requestId = RequestSerializer(read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'proposalId', 'requestId', 'helperId', 'seatType', 'totalPrice', 'message',
            'status', 'createdAt', 'updatedAt'
        ]


class ProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ['seatType', 'totalPrice', 'message']


class MyPageRequestSerializer(serializers.ModelSerializer):
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
        accepted_proposal = obj.proposals.filter(status='accepted').first()
        return accepted_proposal.helperId.name if accepted_proposal else None


class ProposedTicketDetailsSerializer(serializers.ModelSerializer):
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
        # 최신 제안을 가져오도록 정렬 로직 추가
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
    request = RequestSerializer(source='requestId', read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'proposalId', 'request', 'seatType', 'totalPrice', 'message',
            'status', 'createdAt', 'updatedAt'
        ]
