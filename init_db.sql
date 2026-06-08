-- =============================================
-- 清律健康 App - 数据库初始化脚本
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- =============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS qinglv
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE qinglv;

-- -------------------------------------------
-- 用户表
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id            INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(64)  NOT NULL UNIQUE,
  password_hash VARCHAR(128) NOT NULL,
  nick_name     VARCHAR(64)  DEFAULT '',
  gender        VARCHAR(4)   DEFAULT '',
  birthday      DATE         DEFAULT NULL,
  height        FLOAT        DEFAULT 0 COMMENT '身高(cm)',
  weight        FLOAT        DEFAULT 0 COMMENT '体重(斤)',
  created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------
-- 健康数据记录
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS health_records (
  id                      INT      NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id                 INT      NOT NULL,
  timestamp               DATETIME NOT NULL,
  weight                  FLOAT    DEFAULT 0 COMMENT '体重(斤)',
  bmi                     FLOAT    DEFAULT 0,
  body_fat_percentage     FLOAT    DEFAULT 0 COMMENT '体脂率(%)',
  fat_weight              FLOAT    DEFAULT 0 COMMENT '脂肪重量',
  blood_sugar             FLOAT    DEFAULT 0 COMMENT '血糖(mmol/L)',
  blood_pressure_systolic INT      DEFAULT 0 COMMENT '收缩压(mmHg)',
  blood_pressure_diastolic INT     DEFAULT 0 COMMENT '舒张压(mmHg)',
  heart_rate              INT      DEFAULT 0 COMMENT '心率(次/分)',
  waist_circumference     FLOAT    DEFAULT 0 COMMENT '腰围(cm)',
  hip_circumference       FLOAT    DEFAULT 0 COMMENT '臀围(cm)',
  step_count              INT      DEFAULT 0 COMMENT '步数',
  sleep_hours             FLOAT    DEFAULT 0 COMMENT '睡眠时长(h)',
  created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_timestamp (user_id, timestamp),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------
-- 每日饮水记录
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS water_intake (
  id         INT  NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id    INT  NOT NULL,
  date       DATE NOT NULL,
  cup_count  INT  DEFAULT 0,
  daily_goal INT  DEFAULT 8,
  UNIQUE INDEX idx_user_date (user_id, date),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------
-- 提醒计划
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS reminder_plans (
  id         INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id    INT         NOT NULL,
  plan_id    VARCHAR(64) NOT NULL COMMENT '前端生成的UUID',
  plan_type  INT         DEFAULT 0 COMMENT '0=饮水 1=用药',
  name       VARCHAR(64) DEFAULT '',
  time       VARCHAR(8)  DEFAULT '08:00' COMMENT 'HH:MM',
  dosage     VARCHAR(32) DEFAULT '',
  is_enabled BOOLEAN     DEFAULT TRUE,
  INDEX idx_user_plan (user_id, plan_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------
-- 打卡记录
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS checkin_records (
  id           INT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id      INT         NOT NULL,
  plan_id      VARCHAR(64) NOT NULL,
  checkin_date DATE        NOT NULL,
  UNIQUE INDEX idx_user_plan_date (user_id, plan_id, checkin_date),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------
-- 插入 demo 用户（密码: demo123，bcrypt 哈希）
-- 注意：首次启动时 FastAPI 也会自动创建，这里作为手动初始化的备用
-- -------------------------------------------
INSERT IGNORE INTO users (username, password_hash, nick_name, gender, height, weight)
VALUES ('demo', '$2b$12$LJ3m4ys8IuH8MpjPLfm9NeYHu0fCKUxqBOKCOsHxYB2sRxI3S.YfO', '健康用户', '男', 172, 136);
