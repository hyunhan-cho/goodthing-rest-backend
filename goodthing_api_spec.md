# GoodThing REST API 명세서

---

## 1. 인증/회원

### 회원가입
- **POST** `/api/auth/signup/`
- Request
  ```json
  {
    "name": "홍길동",
    "phone": "01012345678",
    "role": "senior", // 또는 "helper"
    "password": "비밀번호",
    "nickname": "닉네임",
    "favorite_team": 1
  }
  ```
- Response
  ```json
  {
    "id": 1,
    "name": "홍길동",
    "phone": "01012345678",
    "role": "senior",
    "mileagePoints": 0,
    "profile": {
      "nickname": "닉네임",
      "favorite_team": 1,
      "verification_info": ""
    }
  }
  ```

### 로그인
- **POST** `/api/auth/login/`
- Request
  ```json
  {
    "phone": "01012345678",
    "password": "비밀번호"
  }
  ```
- Response
  ```json
  {
    "access": "<JWT_ACCESS_TOKEN>",
    "refresh": "<JWT_REFRESH_TOKEN>"
  }
  ```

### 내 정보 조회/수정
- **GET/PUT** `/api/auth/user/`
- 헤더: `Authorization: Bearer <access_token>`
- Response
  ```json
  {
    "id": 1,
    "name": "홍길동",
    "phone": "01012345678",
    "role": "senior",
    "mileagePoints": 0,
    "profile": {
      "nickname": "닉네임",
      "favorite_team": 1,
      "verification_info": ""
    }
  }
  ```

---

## 2. 팀/경기 정보

### KBO 팀 목록
- **GET** `/api/teams/`
- Response
  ```json
  [
    { "id": 1, "shortName": "두산 베어스", "homeStadium": "서울종합운동장 야구장" },
    ...
  ]
  ```

### 경기 목록
- **GET** `/api/games/`
- Response
  ```json
  [
    {
      "gameId": 1,
      "date": "2025-07-25",
      "time": "18:30:00",
      "homeTeam": { "id": 1, "shortName": "두산 베어스", ... },
      "awayTeam": { "id": 2, "shortName": "KT 위즈", ... },
      "stadium": "서울종합운동장 야구장"
    },
    ...
  ]
  ```

---

## 3. 요청/매칭

### 요청 생성 (시니어)
- **POST** `/api/reservation-requests/`
- 헤더: `Authorization: Bearer <access_token>`
- Request
  ```json
  {
    "teamId": 1,
    "gameDate": "2025-07-25",
    "numberOfTickets": 2
  }
  ```
- Response
  ```json
  {
    "requestId": 1,
    "userId": { ... },
    "game": { ... },
    "numberOfTickets": 2,
    "status": "WAITING_FOR_HELPER",
    ...
  }
  ```

### 요청 상세 조회
- **GET** `/api/requests/{requestId}/`
- 헤더: `Authorization: Bearer <access_token>`
- Response
  ```json
  {
    "requestId": 1,
    "userId": { ... },
    "game": {
      "gameId": 1,
      "date": "2025-07-25",
      "time": "18:30:00",
      "homeTeam": { "id": 1, "shortName": "두산 베어스", ... },
      "awayTeam": { "id": 2, "shortName": "KT 위즈", ... },
      "stadium": "서울종합운동장 야구장"
    },
    "numberOfTickets": 2,
    "status": "WAITING_FOR_HELPER",
    ...
  }
  ```

### 요청 목록 (헬퍼)
- **GET** `/api/help-requests/`
- 헤더: `Authorization: Bearer <access_token>`
- Response
  ```json
  [
    {
      "id": 1,
      "seniorFanName": "홍길동",
      "teamName": "두산 베어스",
      "gameDate": "2025-07-25",
      "gameTime": "18:30",
      "numberOfTickets": 2,
      "status": "WAITING_FOR_HELPER"
    },
    ...
  ]
  ```

---

## 4. 제안/매칭

### 제안 생성 (헬퍼)
- **POST** `/api/requests/{request_id}/proposals/create/`
- 헤더: `Authorization: Bearer <access_token>`
- Request
  ```json
  {
    "seatType": "1루 블루석",
    "totalPrice": "50000",
    "message": "티켓 구했습니다!"
  }
  ```
- Response
  ```json
  {
    "proposalId": 1,
    "requestId": { ... },
    "helperId": { ... },
    "seatType": "1루 블루석",
    "totalPrice": "50000",
    "message": "티켓 구했습니다!",
    "status": "pending",
    ...
  }
  ```

### 제안 목록 (시니어)
- **GET** `/api/requests/{request_id}/proposals/`
- 헤더: `Authorization: Bearer <access_token>`
- Response
  ```json
  [
    {
      "proposalId": 1,
      "helperId": { ... },
      "seatType": "1루 블루석",
      "totalPrice": "50000",
      "message": "티켓 구했습니다!",
      "status": "pending",
      ...
    },
    ...
  ]
  ```

### 제안 수락/거절
- **POST** `/api/proposals/{proposal_id}/accept/`
- **POST** `/api/proposals/{proposal_id}/reject/`
- 헤더: `Authorization: Bearer <access_token>`
- Response
  ```json
  { "message": "제안이 수락되었습니다." }
  ```

---

## 5. 마이페이지

### 시니어 내 요청 목록
- **GET** `/api/senior/requests/`
- 헤더: `Authorization: Bearer <access_token>`
- Response
  ```json
  [
    {
      "id": 1,
      "teamName": "두산 베어스",
      "matchDate": "2025-07-25",
      "numberOfTickets": 2,
      "status": "HELPER_MATCHED",
      "helperName": "이도우미"
    },
    ...
  ]
  ```

### 헬퍼 내 활동 목록
- **GET** `/api/helper/activities/`
- 헤더: `Authorization: Bearer <access_token>`
- Response
  ```json
  [
    {
      "proposalId": 1,
      "request": { ... },
      "seatType": "1루 블루석",
      "totalPrice": "50000",
      "message": "티켓 구했습니다!",
      "status": "accepted",
      ...
    },
    ...
  ]
  ```

### 마이페이지 통계
- **GET** `/api/mypage/stats/`
- 헤더: `Authorization: Bearer <access_token>`
- Response (role별로 다름)
  ```json
  // 시니어
  {
    "totalRequests": 5,
    "completedRequests": 2
  }
  // 헬퍼
  {
    "totalSessionsCompleted": 3,
    "mileagePoints": 40
  }
  ```

---

## 6. 티켓 제안 상세/확정

### 티켓 제안 상세
- **GET** `/api/senior/requests/{requestId}/proposed-ticket/`
- 헤더: `Authorization: Bearer <access_token>`
- Response
  ```json
  {
    "id": 1,
    "seniorFanName": "홍길동",
    "teamName": "두산 베어스",
    "matchDate": "2025-07-25",
    "numberOfTickets": 2,
    "seatType": "1루 블루석",
    "totalPrice": "50000",
    "helperName": "이도우미"
  }
  ```

### 티켓 확정
- **POST** `/api/senior/requests/{requestId}/confirm-ticket/`
- 헤더: `Authorization: Bearer <access_token>`
- Response
  ```json
  { "message": "좌석이 확정되었습니다." }
  ```

---

## 참고

- 모든 인증이 필요한 API는 `Authorization: Bearer <access_token>` 헤더 필요
- 상세 필드 구조는 실제 응답 예시 참고
- 팀/경기/요청/제안 등 PK는 DB에 따라 다름

