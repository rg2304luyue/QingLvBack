-- =============================================
-- 清律健康 - AI 对话会话 & 消息表
-- 在 init_db.sql 基础上执行
-- =============================================

USE qinglv;

-- AI 对话会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
  id          INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id     INT          NOT NULL,
  title       VARCHAR(128) DEFAULT '新对话' COMMENT '会话标题（取第一条消息）',
  created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- AI 对话消息表
CREATE TABLE IF NOT EXISTS chat_messages (
  id          INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  session_id  INT          NOT NULL,
  role        VARCHAR(16)  NOT NULL COMMENT 'user 或 assistant',
  content     TEXT         NOT NULL,
  created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_session (session_id),
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
