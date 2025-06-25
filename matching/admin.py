from django.contrib import admin
from .models import User, Profile, Team, Game, Request, Proposal

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'name', 'role', 'mileagePoints', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('phone', 'name')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'favorite_team')
    search_fields = ('user__name', 'nickname')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('teamId', 'name', 'stadium')
    search_fields = ('name', 'stadium')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('gameId', 'date', 'time', 'homeTeam', 'awayTeam', 'stadium')
    list_filter = ('date', 'homeTeam', 'awayTeam')
    search_fields = ('homeTeam__name', 'awayTeam__name', 'stadium')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('requestId', 'userId', 'get_game_info', 'status', 'numberOfTickets', 'createdAt')
    list_filter = ('status', 'game__date')
    search_fields = ('userId__name', 'game__homeTeam__name', 'game__awayTeam__name')
    readonly_fields = ('createdAt', 'updatedAt')
    
    @admin.display(description='Game Info')
    def get_game_info(self, obj):
        if obj.game:
            return f"{obj.game.homeTeam.name} vs {obj.game.awayTeam.name} ({obj.game.date})"
        return "N/A"

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('proposalId', 'requestId', 'helperId', 'status', 'createdAt')
    list_filter = ('status',)
    search_fields = ('requestId__userId__name', 'helperId__name')

