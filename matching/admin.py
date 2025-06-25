# matching/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Request, Proposal, Team, Game


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = '프로필'


class UserAdmin(BaseUserAdmin):
    list_display = ('phone', 'name', 'role', 'mileagePoints', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('phone', 'name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('개인정보', {'fields': ('name', 'role', 'mileagePoints')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요한 일정', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'role', 'password1', 'password2'),
        }),
    )
    
    inlines = [ProfileInline]


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('requestId', 'userId', 'homeTeam', 'awayTeam', 'gameDate', 'status', 'createdAt')
    list_filter = ('status', 'gameDate', 'homeTeam', 'awayTeam', 'accompanyType')
    search_fields = ('userId__name', 'userId__phone', 'homeTeam', 'awayTeam')
    ordering = ('-createdAt',)
    readonly_fields = ('requestId', 'createdAt', 'updatedAt')
    
    fieldsets = (
        ('기본 정보', {'fields': ('requestId', 'userId', 'status')}),
        ('경기 정보', {'fields': ('gameDate', 'gameTime', 'homeTeam', 'awayTeam', 'stadium', 'seatType')}),
        ('요청 상세', {'fields': ('accompanyType', 'additionalInfo')}),
        ('시간 정보', {'fields': ('createdAt', 'updatedAt')}),
    )


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('proposalId', 'requestId', 'helperId', 'status', 'createdAt')
    list_filter = ('status', 'createdAt')
    search_fields = ('helperId__name', 'helperId__phone', 'requestId__userId__name')
    ordering = ('-createdAt',)
    readonly_fields = ('proposalId', 'createdAt', 'updatedAt')
    
    fieldsets = (
        ('기본 정보', {'fields': ('proposalId', 'requestId', 'helperId', 'status')}),
        ('제안 내용', {'fields': ('ticketInfo', 'message')}),
        ('시간 정보', {'fields': ('createdAt', 'updatedAt')}),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('teamId', 'name', 'stadium')
    search_fields = ('name', 'stadium')
    ordering = ('name',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('gameId', 'homeTeam', 'awayTeam', 'date', 'time', 'stadium')
    list_filter = ('date', 'homeTeam', 'awayTeam')
    search_fields = ('homeTeam__name', 'awayTeam__name', 'stadium')
    ordering = ('-date', '-time')


# 커스텀 User 모델 등록
admin.site.register(User, UserAdmin)