# KBO 야구 관람 매칭 서비스 Backend API

이 프로젝트는 KBO 야구 경기 관람에 어려움을 겪는 **어르신(Senior)**과 예매 및 동행을 도와주는 **도우미(Helper)**를 연결해주는 서비스의 백엔드 API입니다.

## 🏗️ 기술 스택

- **Backend**: Django + Django REST Framework
- **Database**: SQLite (개발환경) / PostgreSQL (프로덕션)
- **Authentication**: JWT (JSON Web Token)
- **API Documentation**: Django REST Framework Browsable API

## 📋 주요 기능

### 사용자 역할
- **시니어(Senior)**: 야구 경기 관람 도움을 요청하는 사용자
- **도우미(Helper)**: 티켓 예매 및 동행을 제공하는 봉사자

### 핵심 기능
1. **사용자 인증**: 회원가입, 로그인, JWT 토큰 기반 인증
2. **도움 요청**: 시니어가 원하는 경기의 티켓 예매 도움 요청
3. **제안 시스템**: 도우미가 찾은 티켓 정보를 시니어에게 제안
4. **매칭 관리**: 제안 수락/거절, 매칭 완료 처리
5. **마일리지 시스템**: 활동에 따른 포인트 적립
6. **마이페이지**: 개인 활동 내역 및 통계 조회

## 🚀 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd goodthing-be
```

### 2. 가상환경 설정
```bash
python -m venv myvenv
source myvenv/bin/activate  # Linux/Mac
# 또는
myvenv\Scripts\activate     # Windows
```

### 3. 환경변수 설정
```bash
# .env.example 파일을 .env로 복사
copy .env.example .env

# .env 파일을 열어서 실제 값으로 수정
# SECRET_KEY는 새로 생성하세요
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. 의존성 설치
```bash
pip install -r requirements.txt
```

### 5. 데이터베이스 설정
```bash
python manage.py migrate
```

### 6. 샘플 데이터 생성 (선택사항)
```bash
python manage.py create_sample_data
```

### 7. 개발 서버 실행
```bash
python manage.py runserver
```

API는 `http://localhost:8000/api/` 에서 접근 가능합니다.

## 🔒 보안 설정

### 환경변수 관리
- **절대 .env 파일을 Git에 커밋하지 마세요!**
- `.env.example` 파일을 참고하여 `.env` 파일을 생성하세요
- 프로덕션 환경에서는 더 강력한 SECRET_KEY를 사용하세요

### SECRET_KEY 생성
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 프로덕션 배포시 주의사항
1. `DEBUG=False` 설정
2. `ALLOWED_HOSTS`에 실제 도메인 추가
3. HTTPS 사용 강제 설정
4. 데이터베이스를 PostgreSQL 등으로 변경
5. 정적 파일 서빙 설정

## 📊 데이터 모델

### User (사용자)
```python
{
    "id": "integer",
    "name": "string (이름)",
    "phone": "string (전화번호, 로그인 ID)",
    "role": "senior | helper",
    "mileagePoints": "integer (마일리지 포인트)"
}
```

### Request (도움 요청)
```python
{
    "requestId": "integer",
    "userId": "User ID",
    "gameDate": "date",
    "gameTime": "time",
    "homeTeam": "string",
    "awayTeam": "string",
    "stadium": "string",
    "seatType": "string",
    "accompanyType": "with | ticket_only",
    "additionalInfo": "string",
    "status": "pending | accepted | completed | cancelled"
}
```

### Proposal (제안)
```python
{
    "proposalId": "integer",
    "requestId": "Request ID",
    "helperId": "User ID",
    "ticketInfo": "string",
    "message": "string",
    "status": "pending | accepted | rejected | completed"
}
```

## 🔗 API 엔드포인트

### 인증 관련
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/api/auth/signup/` | 회원가입 | Public |
| POST | `/api/auth/login/` | 로그인 (JWT 토큰 발급) | Public |
| POST | `/api/auth/verify-phone/` | 전화번호 인증 | Public |
| POST | `/api/auth/verify-code/` | 인증번호 확인 | Public |

### 사용자 프로필
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET/PUT | `/api/users/me/` | 내 정보 조회/수정 | Authenticated |

### 팀 및 경기 정보
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/teams/` | KBO 팀 목록 | Public |
| GET | `/api/games/` | 경기 일정 | Public |

### 요청 관리 (시니어 + 도우미)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/requests/` | 요청 목록 (도우미용) | Helper |
| POST | `/api/requests/create/` | 요청 생성 | Senior |
| GET | `/api/requests/{id}/` | 요청 상세 조회 | Owner or Helper |
| PUT | `/api/requests/{id}/update/` | 요청 수정 | Owner |
| DELETE | `/api/requests/{id}/delete/` | 요청 삭제 | Owner |
| POST | `/api/requests/{id}/complete/` | 요청 완료 처리 | Owner |

### 제안 관리
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/requests/{id}/proposals/` | 특정 요청의 제안 목록 | Request Owner |
| POST | `/api/requests/{id}/proposals/create/` | 제안 생성 | Helper |
| GET | `/api/proposals/{id}/` | 제안 상세 조회 | Owner or Request Owner |
| POST | `/api/proposals/{id}/accept/` | 제안 수락 | Request Owner |
| POST | `/api/proposals/{id}/reject/` | 제안 거절 | Request Owner |

### 마이페이지
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/mypage/requests/` | 내 요청 목록 | Senior |
| GET | `/api/mypage/proposals/` | 내 제안 목록 | Helper |
| GET | `/api/mypage/stats/` | 내 통계 정보 | Authenticated |

## 🔐 인증 방식

### JWT 토큰 구조
로그인 성공 시 반환되는 JWT 토큰에는 다음 정보가 포함됩니다:

```json
{
  "userId": 1,
  "role": "senior",
  "name": "김시니어",
  "mileagePoints": 50,
  "exp": 1703987654,
  "iat": 1703984054
}
```

### API 요청 방법
인증이 필요한 API 호출 시 Authorization 헤더에 토큰을 포함하세요:

```bash
curl -H "Authorization: Bearer <your-jwt-token>" \
     http://localhost:8000/api/users/me/
```

## 📱 프론트엔드와의 연동

### 회원가입 API 예시
```javascript
// POST /api/auth/signup/
const signupData = {
  name: "김시니어",
  phone: "01012345678",
  role: "senior",
  password: "securepassword123",
  nickname: "경기장할아버지",
  favorite_team: "LG 트윈스"
};

const response = await fetch('/api/auth/signup/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(signupData)
});
```

### 로그인 API 예시
```javascript
// POST /api/auth/login/
const loginData = {
  phone: "01012345678",
  password: "securepassword123"
};

const response = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(loginData)
});

const { access, refresh } = await response.json();
// access 토큰을 로컬 스토리지에 저장하여 이후 API 호출에 사용
```

## 🧪 테스트 사용자

샘플 데이터 생성 후 다음 계정으로 테스트할 수 있습니다:

### 시니어 계정
- **전화번호**: 01012345678
- **비밀번호**: testpass123
- **이름**: 김시니어

### 도우미 계정
- **전화번호**: 01087654321
- **비밀번호**: testpass123
- **이름**: 이도우미

## 🛠️ 개발 환경 설정

### 환경변수 설정 (.env 파일)
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# JWT 설정
JWT_ACCESS_TOKEN_LIFETIME=60  # 분
JWT_REFRESH_TOKEN_LIFETIME=7  # 일

# CORS 설정
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 개발 도구 설치
```bash
pip install -r requirements-dev.txt  # 개발용 의존성 (linting, testing 등)
```

## 🚀 배포

### 프로덕션 환경 설정
1. PostgreSQL 데이터베이스 설정
2. 환경변수를 프로덕션 값으로 변경
3. `DEBUG=False` 설정
4. 정적 파일 수집: `python manage.py collectstatic`
5. Gunicorn 등을 사용하여 WSGI 서버 실행

## 📞 문의 및 지원

프로젝트 관련 문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해 주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
