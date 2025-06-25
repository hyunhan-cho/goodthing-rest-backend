import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from matching.models import Team, Game

class Command(BaseCommand):
    help = 'Create sample KBO teams and games'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Deleting existing teams and games...'))
        Team.objects.all().delete()
        Game.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Done.'))

        self.stdout.write(self.style.SUCCESS('Creating KBO teams...'))
        
        teams_data = [
            {'name': '두산 베어스', 'stadium': '서울종합운동장 야구장', 'logo': 'https://www.doosanbears.com/images/common/logo_bears.png'},
            {'name': 'LG 트윈스', 'stadium': '서울종합운동장 야구장', 'logo': 'https://www.lgtwins.com/images/common/logo.png'},
            {'name': 'KT 위즈', 'stadium': '수원케이티위즈파크', 'logo': 'https://www.ktwiz.co.kr/images/common/logo.png'},
            {'name': 'SSG 랜더스', 'stadium': '인천SSG랜더스필드', 'logo': 'https://www.ssglanders.com/images/common/emblem.png'},
            {'name': 'NC 다이노스', 'stadium': '창원NC파크', 'logo': 'https://www.ncdinos.com/images/common/logo.png'},
            {'name': 'KIA 타이거즈', 'stadium': '광주기아챔피언스필드', 'logo': 'https://www.tigers.co.kr/images/common/logo.png'},
            {'name': '롯데 자이언츠', 'stadium': '사직 야구장', 'logo': 'https://www.giantsclub.com/images/common/logo.png'},
            {'name': '삼성 라이온즈', 'stadium': '대구삼성라이온즈파크', 'logo': 'https://www.samsunglions.com/images/common/logo.png'},
            {'name': '한화 이글스', 'stadium': '대전한화생명이글스파크', 'logo': 'https://www.hanwhaeagles.co.kr/images/common/logo.png'},
            {'name': '키움 히어로즈', 'stadium': '고척스카이돔', 'logo': 'https://www.heroesbaseball.co.kr/images/common/logo_emblem.png'},
        ]

        teams = []
        for team_data in teams_data:
            team = Team.objects.create(**team_data)
            teams.append(team)
            self.stdout.write(self.style.SUCCESS(f'Successfully created team: {team.name}'))

        self.stdout.write(self.style.SUCCESS('Creating sample games for the next 7 days...'))
        
        today = date.today()
        for i in range(7):
            current_date = today + timedelta(days=i)
            shuffled_teams = random.sample(teams, len(teams))
            
            for j in range(0, len(shuffled_teams), 2):
                if j + 1 < len(shuffled_teams):
                    home_team = shuffled_teams[j]
                    away_team = shuffled_teams[j+1]
                    
                    Game.objects.create(
                        date=current_date,
                        time='18:30:00',
                        homeTeam=home_team,
                        awayTeam=away_team,
                        stadium=home_team.stadium
                    )
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
