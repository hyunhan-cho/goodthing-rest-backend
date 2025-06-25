CREATE TABLE `Bookings` (
	`booking_id`	INT	NOT NULL	COMMENT '예매 고유 식별자',
	`team`	VARCHAR(50)	NOT NULL	COMMENT '예매한 팀',
	`game_date`	DATE	NOT NULL	COMMENT '경기 날짜',
	`num_tickets`	INT	NOT NULL	COMMENT '예매한 티켓 수',
	`total_price`	INT	NOT NULL	COMMENT '총 결제 금액',
	`created_at`	TIMESTAMP	NOT NULL	DEFAULT CURRENT_TIMESTAMP	COMMENT '예매 완료일',
	`user_id`	VARCHAR(20)	NOT NULL	COMMENT '사용자 ID (연락처)'
);

CREATE TABLE `Users` (
	`user_id`	VARCHAR(20)	NOT NULL	COMMENT '사용자 ID (연락처)',
	`password`	VARCHAR(255)	NOT NULL	COMMENT '비밀번호 (해시하여 저장)',
	`name`	VARCHAR(50)	NOT NULL	COMMENT '사용자 이름',
	`area`	VARCHAR(100)	NULL	COMMENT '활동 가능 지역',
	`introduction`	TEXT	NULL	COMMENT '자기소개',
	`created_at`	TIMESTAMP	NOT NULL	DEFAULT CURRENT_TIMESTAMP	COMMENT '계정 생성일'
);

CREATE TABLE `Help_Requests` (
	`request_id`	INT	NOT NULL	COMMENT '요청 고유 식별자',
	`requester_name`	VARCHAR(50)	NOT NULL	COMMENT '요청자 이름',
	`requester_contact`	VARCHAR(100)	NOT NULL	COMMENT '요청자 연락처',
	`matched_helper_id`	VARCHAR(20)	NULL	COMMENT '매칭된 헬퍼 ID',
	`requested_team`	VARCHAR(50)	NOT NULL	COMMENT '요청 응원팀',
	`requested_date`	DATE	NOT NULL	COMMENT '희망 경기 날짜',
	`num_tickets`	INT	NOT NULL	COMMENT '요청 티켓 수',
	`status`	ENUM('open', 'in-progress', 'resolved')	NOT NULL	DEFAULT 'open'	COMMENT '요청 상태',
	`created_at`	TIMESTAMP	NOT NULL	DEFAULT CURRENT_TIMESTAMP	COMMENT '요청 등록일',
	`updated_at`	TIMESTAMP	NOT NULL	DEFAULT CURRENT_TIMESTAMP	COMMENT '요청 상태 변경일',
	`user_id`	VARCHAR(20)	NOT NULL	COMMENT '사용자 ID (연락처)'
);

ALTER TABLE `Bookings` ADD CONSTRAINT `PK_BOOKINGS` PRIMARY KEY (
	`booking_id`
);

ALTER TABLE `Users` ADD CONSTRAINT `PK_USERS` PRIMARY KEY (
	`user_id`
);

ALTER TABLE `Help_Requests` ADD CONSTRAINT `PK_HELP_REQUESTS` PRIMARY KEY (
	`request_id`
);

