# matching/serializers.py
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
    password = serializers.CharField(write_only=True, min_length=6)
    nickname = serializers.CharField(write_only=True, max_length=50, required=False)
    favorite_team = serializers.CharField(write_only=True, max_length=50, required=False)
    
    class Meta:
        model = User
        fields = ['name', 'phone', 'role', 'password', 'nickname', 'favorite_team']
    
    def validate_phone(self, value):
        phone_number = re.sub(r'[^0-9]', '', value)
        if not (10 <= len(phone_number) <= 11) or not phone_number.startswith('01'):
            raise serializers.ValidationError("올바른 휴대폰 번호 형식이 아닙니다.")
        if User.objects.filter(phone=phone_number).exists():
            raise serializers.ValidationError("이미 가입된 전화번호입니다.")
        return phone_number
    
    def validate_role(self, value):
        if value not in ['senior', 'helper']:
            raise serializers.ValidationError("역할은 'senior' 또는 'helper'여야 합니다.")
        return value
    
    def create(self, validated_data):
        nickname = validated_data.pop('nickname', '')
        favorite_team = validated_data.pop('favorite_team', '')
        
        user = User.objects.create_user(
            phone=validated_data['phone'],
            name=validated_data['name'],
            role=validated_data['role'],
            password=validated_data['password']
        )
        
        # Profile 업데이트 (signals에서 자동 생성됨)
        if nickname or favorite_team:
            user.profile.nickname = nickname
            user.profile.favorite_team = favorite_team
            user.profile.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()


class TeamSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='string_id', read_only=True)
    shortName = serializers.CharField(source='name', read_only=True)
    logoUrl = serializers.URLField(source='logo', read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'shortName', 'logoUrl', 'stadium']


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
            'requestId', 'userId', 'gameDate', 'gameTime', 'homeTeam', 'awayTeam',
            'stadium', 'seatType', 'accompanyType', 'additionalInfo', 'status',
            'numberOfTickets', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['requestId', 'userId', 'status', 'createdAt', 'updatedAt']


class RequestCreateSerializer(serializers.Serializer):
    teamId = serializers.CharField(max_length=50)
    gameDate = serializers.DateField()
    numberOfTickets = serializers.IntegerField(min_value=1, max_value=4)
    accompanyType = serializers.ChoiceField(choices=[('with', '함께 관람'), ('ticket_only', '티켓만 전달')], default='ticket_only')
    additionalInfo = serializers.CharField(required=False, allow_blank=True)


class RequestListSerializer(serializers.ModelSerializer):
    """요청 목록을 위한 Serializer (game 필드 있을 때)"""
    homeTeamName = serializers.CharField(source='game.homeTeam.name', read_only=True)
    awayTeamName = serializers.CharField(source='game.awayTeam.name', read_only=True)
    homeTeamLogo = serializers.URLField(source='game.homeTeam.logo', read_only=True)
    awayTeamLogo = serializers.URLField(source='game.awayTeam.logo', read_only=True)
    gameDate = serializers.DateField(source='game.date', read_only=True)
    gameTime = serializers.TimeField(source='game.time', read_only=True)
    stadium = serializers.CharField(source='game.stadium', read_only=True)

    class Meta:
        model = Request
        fields = [
            'requestId', 'userId', 'gameDate', 'gameTime', 'stadium',
            'seatType', 'numberOfTickets', 'accompanyType', 'status',
            'homeTeamName', 'awayTeamName', 'homeTeamLogo', 'awayTeamLogo',
            'createdAt'
        ]


class ProposalSerializer(serializers.ModelSerializer):
    helperId = UserSerializer(read_only=True)
    requestId = RequestSerializer(read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'proposalId', 'requestId', 'helperId', 'ticketInfo', 'message',
            'status', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['proposalId', 'requestId', 'helperId', 'status', 'createdAt', 'updatedAt']


class ProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ['ticketInfo', 'message']


class MyPageRequestSerializer(serializers.ModelSerializer):
    proposalCount = serializers.SerializerMethodField()
    
    class Meta:
        model = Request
        fields = [
            'requestId', 'gameDate', 'gameTime', 'homeTeam', 'awayTeam',
            'stadium', 'status', 'proposalCount', 'createdAt'
        ]
    
    def get_proposalCount(self, obj):
        return obj.proposals.count()


class MyPageProposalSerializer(serializers.ModelSerializer):
    request = RequestSerializer(source='requestId', read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'proposalId', 'request', 'ticketInfo', 'message',
            'status', 'createdAt', 'updatedAt'
        ]