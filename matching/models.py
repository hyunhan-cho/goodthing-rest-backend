from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def create_user(self, phone, name, role, password=None, **extra_fields):
        if not phone:
            raise ValueError('사용자는 반드시 전화번호를 가져야 합니다.')
        user = self.model(phone=phone, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, role, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, name, role, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (('senior', '시니어'), ('helper', '도우미'))
    phone = models.CharField(max_length=20, unique=True, verbose_name="전화번호")
    name = models.CharField(max_length=100, verbose_name="이름")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="역할")
    mileagePoints = models.PositiveIntegerField(default=0, verbose_name="마일리지 포인트")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = UserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name', 'role']
    
    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50, blank=True, verbose_name="닉네임")
    favorite_team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="관심 구단")
    verification_info = models.CharField(max_length=100, blank=True, verbose_name="SNS 연동 or 팬클럽 ID")
    
    def __str__(self):
        return f"{self.user.name}의 프로필"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Team(models.Model):
    teamId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="팀명")
    logo = models.URLField(blank=True, verbose_name="로고 URL")
    stadium = models.CharField(max_length=100, verbose_name="홈구장")
    
    def __str__(self):
        return self.name

class Game(models.Model):
    gameId = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name="경기일")
    time = models.TimeField(verbose_name="경기 시간")
    homeTeam = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_games")
    awayTeam = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_games")
    stadium = models.CharField(max_length=100, verbose_name="경기장")
    
    def __str__(self):
        return f"{self.homeTeam.name} vs {self.awayTeam.name} ({self.date})"

class Request(models.Model):
    REQUEST_STATUS_CHOICES = (
        ('WAITING_FOR_HELPER', '헬퍼 배정 대기 중'),
        ('HELPER_MATCHED', '헬퍼 매칭! 티켓 찾는 중'),
        ('TICKET_PROPOSED', '헬퍼가 티켓을 찾았어요!'),
        ('SEAT_CONFIRMED', '좌석 확정! 경기 당일 만나요'),
        ('COMPLETED', '관람 완료'),
        ('CANCELLED', '요청 취소됨'),
    )
    ACCOMPANY_TYPE_CHOICES = (
        ('with', '함께 관람'), 
        ('ticket_only', '티켓만 전달'),
    )
    
    requestId = models.AutoField(primary_key=True)
    userId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="requests")
    accompanyType = models.CharField(max_length=20, choices=ACCOMPANY_TYPE_CHOICES, verbose_name="동행 유형", default='ticket_only')
    additionalInfo = models.TextField(blank=True, verbose_name="추가 정보")
    status = models.CharField(max_length=50, choices=REQUEST_STATUS_CHOICES, default='WAITING_FOR_HELPER', verbose_name="상태")
    numberOfTickets = models.IntegerField(default=1, verbose_name="티켓 수량")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"[{self.get_status_display()}] {self.userId.name} - {self.game}"

class Proposal(models.Model):
    PROPOSAL_STATUS_CHOICES = (
        ('pending', '대기중'), 
        ('accepted', '수락됨'), 
        ('rejected', '거절됨'), 
    )
    
    proposalId = models.AutoField(primary_key=True)
    requestId = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="proposals")
    helperId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="proposals")
    seatType = models.CharField(max_length=100, verbose_name="좌석 정보", default="좌석 정보 없음")
    totalPrice = models.CharField(max_length=50, verbose_name="총 가격", default="가격 정보 없음")
    message = models.TextField(blank=True, verbose_name="메시지")
    status = models.CharField(max_length=20, choices=PROPOSAL_STATUS_CHOICES, default='pending', verbose_name="상태")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"[{self.get_status_display()}] {self.helperId.name} -> {self.requestId}"
