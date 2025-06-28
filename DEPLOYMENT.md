# Cloudtype 배포 가이드

## 환경 변수 설정

Cloudtype 대시보드에서 다음 환경 변수들을 설정해주세요:

### 필수 환경 변수
- `SECRET_KEY`: Django 시크릿 키 (랜덤한 50자 이상의 문자열)
- `DEBUG`: False
- `ALLOWED_HOSTS`: 배포될 도메인 (예: your-app.cloudtype.app)
- `CORS_ALLOWED_ORIGINS`: 프론트엔드 도메인

### 선택적 환경 변수
- `DATABASE_URL`: PostgreSQL 사용시 (Cloudtype에서 자동 설정)
- `JWT_ACCESS_TOKEN_LIFETIME`: JWT 액세스 토큰 만료 시간 (기본: 60분)
- `JWT_REFRESH_TOKEN_LIFETIME`: JWT 리프레시 토큰 만료 시간 (기본: 7일)

## 배포 명령어

Cloudtype에서 다음 명령어들이 자동으로 실행됩니다:

1. 의존성 설치: `pip install -r requirements.txt`
2. 데이터베이스 마이그레이션: `python manage.py migrate`
3. 정적 파일 수집: `python manage.py collectstatic --noinput`
4. 서버 시작: `gunicorn config.wsgi --log-file -`

## 수동 설정이 필요한 경우

만약 수동으로 명령어를 실행해야 한다면:

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 파일 생성 (로컬 개발시)
cp .env.example .env
# .env 파일을 수정하여 실제 값으로 변경

# 데이터베이스 마이그레이션
python manage.py migrate

# 슈퍼유저 생성 (선택사항)
python manage.py createsuperuser

# 정적 파일 수집
python manage.py collectstatic --noinput

# 개발 서버 실행 (로컬)
python manage.py runserver

# 프로덕션 서버 실행
gunicorn config.wsgi --log-file -
```

## 보안 개선 사항

1. ✅ SECRET_KEY 환경 변수화
2. ✅ DEBUG 모드 비활성화
3. ✅ ALLOWED_HOSTS 제한
4. ✅ CORS 설정 환경 변수화
5. ✅ 보안 헤더 추가 (HTTPS 환경에서)
6. ✅ 정적 파일 WhiteNoise로 서빙
7. ✅ 환경 변수로 JWT 설정 관리
