# Generated by Django 5.2.3 on 2025-06-25 14:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('gameId', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(verbose_name='경기일')),
                ('time', models.TimeField(verbose_name='경기 시간')),
                ('stadium', models.CharField(max_length=100, verbose_name='경기장')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('teamId', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='팀명')),
                ('logo', models.URLField(blank=True, verbose_name='로고 URL')),
                ('stadium', models.CharField(max_length=100, verbose_name='홈구장')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone', models.CharField(max_length=20, unique=True, verbose_name='전화번호')),
                ('name', models.CharField(max_length=100, verbose_name='이름')),
                ('role', models.CharField(choices=[('senior', '시니어'), ('helper', '도우미')], max_length=10, verbose_name='역할')),
                ('mileagePoints', models.PositiveIntegerField(default=0, verbose_name='마일리지 포인트')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('requestId', models.AutoField(primary_key=True, serialize=False)),
                ('accompanyType', models.CharField(choices=[('with', '함께 관람'), ('ticket_only', '티켓만 전달')], default='ticket_only', max_length=20, verbose_name='동행 유형')),
                ('additionalInfo', models.TextField(blank=True, verbose_name='추가 정보')),
                ('status', models.CharField(choices=[('WAITING_FOR_HELPER', '헬퍼 배정 대기 중'), ('HELPER_MATCHED', '헬퍼 매칭! 티켓 찾는 중'), ('TICKET_PROPOSED', '헬퍼가 티켓을 찾았어요!'), ('SEAT_CONFIRMED', '좌석 확정! 경기 당일 만나요'), ('COMPLETED', '관람 완료'), ('CANCELLED', '요청 취소됨')], default='WAITING_FOR_HELPER', max_length=50, verbose_name='상태')),
                ('numberOfTickets', models.IntegerField(default=1, verbose_name='티켓 수량')),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='matching.game')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('proposalId', models.AutoField(primary_key=True, serialize=False)),
                ('seatType', models.CharField(default='좌석 정보 없음', max_length=100, verbose_name='좌석 정보')),
                ('totalPrice', models.CharField(default='가격 정보 없음', max_length=50, verbose_name='총 가격')),
                ('message', models.TextField(blank=True, verbose_name='메시지')),
                ('status', models.CharField(choices=[('pending', '대기중'), ('accepted', '수락됨'), ('rejected', '거절됨')], default='pending', max_length=20, verbose_name='상태')),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('helperId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to=settings.AUTH_USER_MODEL)),
                ('requestId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to='matching.request')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(blank=True, max_length=50, verbose_name='닉네임')),
                ('verification_info', models.CharField(blank=True, max_length=100, verbose_name='SNS 연동 or 팬클럽 ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('favorite_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='matching.team', verbose_name='관심 구단')),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='awayTeam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_games', to='matching.team'),
        ),
        migrations.AddField(
            model_name='game',
            name='homeTeam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_games', to='matching.team'),
        ),
    ]
