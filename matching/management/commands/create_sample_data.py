# matching/management/commands/create_sample_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from matching.models import Team, Game, Request, Proposal
from datetime import date, time, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = '샘플 데이터 생성'

    def handle(self, *args, **options):
        self.stdout.write('샘플 데이터 생성 중...')

        # 1. 기존 데이터 삭제 (선택사항, 하지만 클린한 상태에서 시작하는 것을 추천)
        Proposal.objects.all().delete()
        Request.objects.all().delete()
        Game.objects.all().delete()
        Team.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # 1. 팀 데이터 생성 (string_id, logo 추가)
        teams_data = [
            {'string_id': 'lg', 'name': 'LG 트윈스', 'logo': 'https://i.imgur.com/wG5G2C3.png', 'stadium': '잠실야구장'},
            {'string_id': 'doosan', 'name': '두산 베어스', 'logo': 'https://i.imgur.com/agB85z5.png', 'stadium': '잠실야구장'},
            {'string_id': 'kt', 'name': 'KT 위즈', 'logo': 'https://i.imgur.com/uF1a2R4.png', 'stadium': '수원KT위즈파크'},
            {'string_id': 'hanwha', 'name': '한화 이글스', 'logo': 'https://i.imgur.com/L4zzF2x.png', 'stadium': '대전한화생명이글스파크'},
            {'string_id': 'samsung', 'name': '삼성 라이온즈', 'logo': 'https://i.imgur.com/R3d4J4f.png', 'stadium': '대구삼성라이온즈파크'},
            {'string_id': 'lotte', 'name': '롯데 자이언츠', 'logo': 'https://i.imgur.com/rS2jA5M.png', 'stadium': '사직야구장'},
            {'string_id': 'kia', 'name': 'KIA 타이거즈', 'logo': 'https://i.imgur.com/E85b7gT.png', 'stadium': '광주-기아챔피언스필드'},
            {'string_id': 'nc', 'name': 'NC 다이노스', 'logo': 'https://i.imgur.com/zSg3gZ2.png', 'stadium': '창원NC파크'},
            {'string_id': 'ssg', 'name': 'SSG 랜더스', 'logo': 'https://i.imgur.com/lZH3G4R.png', 'stadium': '인천SSG랜더스필드'},
            {'string_id': 'kiwoom', 'name': '키움 히어로즈', 'logo': 'https://i.imgur.com/2s3Fq3h.png', 'stadium': '고척스카이돔'},
        ]
        
        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                string_id=team_data['string_id'],
                defaults={
                    'name': team_data['name'],
                    'logo': team_data['logo'],
                    'stadium': team_data['stadium']
                }
            )
            if created:
                self.stdout.write(f'팀 생성: {team.name} (ID: {team.string_id})')

        # 2. 테스트 사용자 생성
        senior_user, created = User.objects.get_or_create(
            phone='01012345678',
            defaults={
                'name': '김시니어',
                'role': 'senior',
                'mileagePoints': 50
            }
        )
        if created:
            senior_user.set_password('testpass123')
            senior_user.save()
            self.stdout.write('시니어 사용자 생성: 김시니어 (01012345678)')
        
        helper_user, created = User.objects.get_or_create(
            phone='01087654321',
            defaults={
                'name': '이도우미',
                'role': 'helper',
                'mileagePoints': 120
            }
        )
        if created:
            helper_user.set_password('testpass123')
            helper_user.save()
            self.stdout.write('도우미 사용자 생성: 이도우미 (01087654321)')
        
        # 3. 경기 데이터 생성
        teams = list(Team.objects.all())
        if len(teams) >= 2:
            for i in range(5):
                game_date = date.today() + timedelta(days=i+1)
                home_team = teams[i % len(teams)]
                away_team = teams[(i+1) % len(teams)]
                
                game, created = Game.objects.get_or_create(
                    date=game_date,
                    homeTeam=home_team,
                    defaults={
                        'awayTeam': away_team,
                        'time': time(18, 30),
                        'stadium': home_team.stadium
                    }
                )
                if created:
                    self.stdout.write(f'경기 생성: {home_team.name} vs {away_team.name} ({game_date})')
        
        # 4. 요청 데이터 생성
        if Game.objects.exists():
            first_game = Game.objects.order_by('date').first()
            request_data = {
                'userId': senior_user,
                'gameDate': first_game.date,
                'gameTime': first_game.time,
                'homeTeam': first_game.homeTeam.name,
                'awayTeam': first_game.awayTeam.name,
                'stadium': first_game.stadium,
                'seatType': '1루 블루석',
                'accompanyType': 'with',
                'additionalInfo': '휠체어 접근 가능한 좌석 희망',
                'status': 'pending',
                'numberOfTickets': 2
            }
            
            request_obj, created = Request.objects.get_or_create(
                userId=senior_user,
                gameDate=request_data['gameDate'],
                defaults=request_data
            )
            if created:
                self.stdout.write(f'요청 생성: {request_obj.homeTeam} vs {request_obj.awayTeam}')
                
                # 5. 제안 데이터 생성
                proposal_data = {
                    'requestId': request_obj,
                    'helperId': helper_user,
                    'ticketInfo': '1루 블루석 205블록 G열 7, 8번',
                    'message': '좋은 자리 구했습니다! 휠체어 접근 가능한 좌석입니다.',
                    'status': 'pending'
                }
                
                proposal, p_created = Proposal.objects.get_or_create(
                    requestId=request_obj,
                    helperId=helper_user,
                    defaults=proposal_data
                )
                if p_created:
                    self.stdout.write(f'제안 생성: {proposal.helperId.name}이 제안함')
        
        self.stdout.write(self.style.SUCCESS('샘플 데이터 생성 완료!'))