/*
 Navicat Premium Data Transfer

 Source Server         : luyue
 Source Server Type    : MySQL
 Source Server Version : 80039 (8.0.39)
 Source Host           : localhost:3306
 Source Schema         : qinglv

 Target Server Type    : MySQL
 Target Server Version : 80039 (8.0.39)
 File Encoding         : 65001

 Date: 09/06/2026 16:10:06
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for chat_messages
-- ----------------------------
DROP TABLE IF EXISTS `chat_messages`;
CREATE TABLE `chat_messages`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `role` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'user 或 assistant',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_session`(`session_id` ASC) USING BTREE,
  CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of chat_messages
-- ----------------------------
INSERT INTO `chat_messages` VALUES (5, 5, 'user', '你好，请问你觉得有什么适合我的运动方式吗', '2026-06-09 15:18:56');
INSERT INTO `chat_messages` VALUES (6, 5, 'assistant', '你好！很高兴为你提供建议。根据你最近7天的健康数据，你的身体状况整体不错：\n\n- **体重**：75.0斤（37.5公斤），属于偏轻范围（BMI约13.8，低于正常值18.5）。建议适当关注营养摄入，增加体重。\n- **血压**：119/83 mmHg 和 119/78 mmHg，处于正常范围。\n- **心率**：72-73次/分，非常稳定健康。\n- **血糖**：4.9-5.9 mmol/L，波动在正常范围（空腹血糖正常值3.9-6.1 mmol/L），但6月8日的5.9略偏高，建议注意饮食。\n\n基于你的偏轻体重和良好心血管指标，推荐以下运动方式：\n\n1. **力量训练（重点推荐）**：如哑铃、弹力带、深蹲、俯卧撑等。有助于增加肌肉量和体重，改善身体成分。每周2-3次，每次20-30分钟。\n2. **低强度有氧运动**：如快走、慢跑、游泳或瑜伽。能维持心肺健康，又不会过度消耗热量。每周3-4次，每次30分钟。\n3. **柔韧性训练**：如拉伸或太极，帮助放松和预防损伤。\n\n**特别提醒**：由于你体重偏轻，运动后要注意补充营养（优质蛋白、碳水化合物），避免空腹运动。同时，血糖偶尔偏高（5.9），运动前后可监测血糖，避免低血糖风险。\n\n如果你有具体偏好（如室内/室外、时间限制），我可以进一步细化方案。😊', '2026-06-09 15:19:03');

-- ----------------------------
-- Table structure for chat_sessions
-- ----------------------------
DROP TABLE IF EXISTS `chat_sessions`;
CREATE TABLE `chat_sessions`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '新对话' COMMENT '会话标题（取第一条消息）',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user`(`user_id` ASC) USING BTREE,
  CONSTRAINT `chat_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of chat_sessions
-- ----------------------------
INSERT INTO `chat_sessions` VALUES (5, 2, '你好，请问你觉得有什么适合我的运动方式吗', '2026-06-09 15:18:44', '2026-06-09 15:18:56');

-- ----------------------------
-- Table structure for checkin_records
-- ----------------------------
DROP TABLE IF EXISTS `checkin_records`;
CREATE TABLE `checkin_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `plan_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `checkin_date` date NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_user_plan_date`(`user_id` ASC, `plan_id` ASC, `checkin_date` ASC) USING BTREE,
  CONSTRAINT `checkin_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of checkin_records
-- ----------------------------

-- ----------------------------
-- Table structure for health_records
-- ----------------------------
DROP TABLE IF EXISTS `health_records`;
CREATE TABLE `health_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `timestamp` datetime NOT NULL,
  `weight` float NULL DEFAULT 0 COMMENT '体重(公斤)',
  `bmi` float NULL DEFAULT 0,
  `body_fat_percentage` float NULL DEFAULT 0 COMMENT '体脂率(%)',
  `fat_weight` float NULL DEFAULT 0 COMMENT '脂肪重量',
  `blood_sugar` float NULL DEFAULT 0 COMMENT '血糖(mmol/L)',
  `blood_pressure_systolic` int NULL DEFAULT 0 COMMENT '收缩压(mmHg)',
  `blood_pressure_diastolic` int NULL DEFAULT 0 COMMENT '舒张压(mmHg)',
  `heart_rate` int NULL DEFAULT 0 COMMENT '心率(次/分)',
  `waist_circumference` float NULL DEFAULT 0 COMMENT '腰围(cm)',
  `hip_circumference` float NULL DEFAULT 0 COMMENT '臀围(cm)',
  `step_count` int NULL DEFAULT 0 COMMENT '步数',
  `sleep_hours` float NULL DEFAULT 0 COMMENT '睡眠时长(h)',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_timestamp`(`user_id` ASC, `timestamp` ASC) USING BTREE,
  CONSTRAINT `health_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 34 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of health_records
-- ----------------------------
INSERT INTO `health_records` VALUES (1, 1, '2026-05-09 08:00:00', 60, 20.3, 22.1, 13.3, 4.8, 112, 73, 66, 79.4, 96.5, 4671, 8.3, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (2, 1, '2026-05-10 08:00:00', 60, 20.3, 21.5, 12.9, 5.5, 107, 74, 68, 82.1, 96.2, 6368, 6.2, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (3, 1, '2026-05-11 08:00:00', 60, 20.3, 22.3, 13.4, 4.7, 109, 73, 63, 80.2, 95.2, 7895, 7.2, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (4, 1, '2026-05-12 08:00:00', 60, 20.3, 21.9, 13.1, 4.2, 114, 76, 61, 79.6, 95, 8958, 6.3, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (5, 1, '2026-05-13 08:00:00', 60, 20.3, 22.5, 13.5, 4.8, 118, 72, 63, 77.9, 94.6, 6565, 6.7, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (6, 1, '2026-05-14 08:00:00', 60, 20.3, 22, 13.2, 4.8, 114, 69, 65, 78.8, 95.1, 7373, 6.2, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (7, 1, '2026-05-15 08:00:00', 60, 20.3, 22.5, 13.5, 5.2, 117, 73, 77, 80.8, 94.9, 9770, 6.3, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (8, 1, '2026-05-16 08:00:00', 60, 20.3, 22.3, 13.4, 4.9, 107, 76, 73, 80.4, 94.3, 6971, 5.7, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (9, 1, '2026-05-17 08:00:00', 60, 20.3, 21.8, 13.1, 4.8, 118, 73, 66, 79.8, 95.5, 10971, 5.9, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (10, 1, '2026-05-18 08:00:00', 60, 20.3, 21.9, 13.2, 4.9, 118, 78, 68, 80, 95.1, 7293, 6.6, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (11, 1, '2026-05-19 08:00:00', 60, 20.3, 21.9, 13.2, 4.9, 114, 77, 69, 79.2, 96.1, 6043, 7.4, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (12, 1, '2026-05-20 08:00:00', 60, 20.3, 21.8, 13.1, 4.3, 115, 71, 65, 79.2, 95.2, 5466, 6, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (13, 1, '2026-05-21 08:00:00', 60, 20.3, 22.8, 13.7, 4.7, 113, 75, 62, 80.4, 94, 5019, 7.7, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (14, 1, '2026-05-22 08:00:00', 60, 20.3, 22, 13.2, 5.1, 115, 74, 82, 79.7, 95.1, 3463, 7.1, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (15, 1, '2026-05-23 08:00:00', 60, 20.3, 22.4, 13.4, 5, 115, 79, 55, 79.7, 95.3, 11377, 5.9, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (16, 1, '2026-05-24 08:00:00', 60, 20.3, 22.1, 13.2, 5.1, 109, 72, 66, 81.5, 94.9, 6504, 5.4, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (17, 1, '2026-05-25 08:00:00', 60, 20.3, 22, 13.2, 4.5, 115, 76, 75, 79.5, 96.5, 8166, 6.8, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (18, 1, '2026-05-26 08:00:00', 60, 20.3, 23.6, 14.2, 4.8, 112, 73, 67, 80, 96.3, 9964, 7.4, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (19, 1, '2026-05-27 08:00:00', 60, 20.3, 22.1, 13.2, 5, 115, 77, 75, 80, 91.9, 4344, 7.5, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (20, 1, '2026-05-28 08:00:00', 60, 20.3, 22.4, 13.5, 4.7, 114, 79, 64, 79.7, 94.3, 9458, 7.2, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (21, 1, '2026-05-29 08:00:00', 60, 20.3, 22.8, 13.7, 4.2, 109, 78, 66, 77.5, 93.6, 3612, 7.2, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (22, 1, '2026-05-30 08:00:00', 60, 20.3, 23, 13.8, 4.6, 116, 76, 56, 81.5, 95.7, 11604, 7.6, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (23, 1, '2026-05-31 08:00:00', 60, 20.3, 22.6, 13.5, 4.4, 112, 74, 78, 80.7, 94.1, 4990, 6.5, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (24, 1, '2026-06-01 08:00:00', 60, 20.3, 22.3, 13.4, 4.6, 113, 76, 73, 79.7, 97, 10400, 6.4, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (25, 1, '2026-06-02 08:00:00', 60, 20.3, 21.7, 13, 4.3, 110, 75, 59, 79.1, 94.7, 6078, 7.7, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (26, 1, '2026-06-03 08:00:00', 60, 20.3, 22.5, 13.5, 5.1, 112, 75, 65, 79.8, 93.3, 5720, 6.5, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (27, 1, '2026-06-04 08:00:00', 60, 20.3, 21.8, 13.1, 4.3, 111, 76, 61, 79.1, 95.3, 5341, 5.3, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (28, 1, '2026-06-05 08:00:00', 60, 20.3, 22.5, 13.5, 4.3, 115, 77, 60, 79.5, 95.8, 7433, 6.7, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (29, 1, '2026-06-06 08:00:00', 60, 20.3, 22.8, 13.7, 4.7, 108, 73, 64, 79.6, 94.3, 5439, 7.9, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (30, 1, '2026-06-07 08:00:00', 60, 20.3, 21.9, 13.2, 4.8, 110, 77, 62, 79.5, 96.5, 5860, 5.6, '2026-06-08 19:44:03');
INSERT INTO `health_records` VALUES (31, 2, '2026-06-08 22:14:30', 75, 0, 19.1, 14.5, 5.9, 119, 78, 72, 0, 0, 0, 0, '2026-06-08 22:14:30');
INSERT INTO `health_records` VALUES (32, 1, '2026-06-08 08:00:00', 120, 20.3, 21.8, 13.1, 3.9, 112, 74, 63, 79.2, 94.8, 7177, 6.5, '2026-06-09 14:38:18');
INSERT INTO `health_records` VALUES (33, 2, '2026-06-09 15:17:37', 75, 0, 0, 0, 4.9, 119, 83, 73, 0, 0, 0, 0, '2026-06-09 15:17:37');

-- ----------------------------
-- Table structure for knowledge_articles
-- ----------------------------
DROP TABLE IF EXISTS `knowledge_articles`;
CREATE TABLE `knowledge_articles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sub_title` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '',
  `tag` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '' COMMENT '分类：饮食/运动/睡眠/心理',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_order` int NULL DEFAULT 0,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_tag`(`tag` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 31 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of knowledge_articles
-- ----------------------------
INSERT INTO `knowledge_articles` VALUES (1, '健康饮食', '科学搭配，吃走亚健康', '饮食', '轻断食又称间歇性能量限制（IER），是按照一定规律，在规定时期内禁食或给予有限能量摄入的饮食模式。\n目前常用的 IER 方式包括隔日禁食法、4∶3 或 5∶2 轻断食等。隔日禁食法是每隔 1 天就禁食 24 小时，不限制饮水及其他无热量饮品的摄入，但饥饿感强烈，难以坚持，需要专业人士指导。16∶8 轻断食法也叫时限性断食，限定每日的进食时间跨度在连续的 8 小时以内，剩下的 16 小时为禁食期。5∶2 轻断食法是每周 5 天进食，2 天为断食日，限制热量在 500kcal（女性）或 600kcal（男性），是目前应用及研究最广泛的断食方法。\n多项研究发现轻断食不仅对于减重有效，对代谢性疾病也具有重要作用。它可能具有延缓细胞衰老、改善血脂水平、改善胰岛素抵抗、改善炎症反应等作用。不过，在开始尝试轻断食时，人体常常一时无法适应代谢的转换，可能会出现饥饿感、易激怒、注意力下降、胃部不适、头晕和心慌等症状，女性还有可能出现月经紊乱。通常在尝试断食 1 个月左右，身体适应之后，上述不适会有所缓解。', 1, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (2, '睡眠健康', '睡前花1分钟测血压，小习惯护好大健康', '睡眠', '良好的睡眠是身体修复和恢复精力的关键。成年人每晚需要7-9小时的优质睡眠。\n\n改善睡眠的小技巧：\n1. 保持规律作息：每天在同一时间入睡和起床，即使在周末也要坚持。\n2. 营造舒适环境：保持卧室安静、黑暗、凉爽，选择舒适的床垫和枕头。\n3. 限制电子产品使用：睡前1小时避免使用手机、电脑等蓝光设备，蓝光会抑制褪黑素分泌。\n4. 适当运动：白天进行中等强度运动有助于晚上的睡眠，但避免睡前剧烈运动。\n5. 注意饮食：避免睡前大量进食，限制咖啡因和酒精的摄入。\n\n如果你长期睡眠不足，可能会增加心血管疾病、糖尿病、肥胖和抑郁症的风险。关注睡眠质量，就是关注长远健康。', 2, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (3, '轻食主义', '少油少盐，享受食物本味', '饮食', '轻食不是节食，而是一种更健康、更均衡的饮食理念。它强调少油、少盐、少糖，以蒸、煮、炖为主要烹饪方式，保留食材的天然营养。\n\n轻食的核心原则：\n1. 高蛋白低脂肪：优先选择鸡胸肉、鱼虾、豆腐、鸡蛋等优质蛋白，减少红肉和加工肉制品。\n2. 多蔬菜适量主食：每餐蔬菜占一半以上，主食选择粗粮（糙米、燕麦、红薯），减少精白米面。\n3. 好脂肪不可少：适量摄入坚果、牛油果、橄榄油中的不饱和脂肪酸，避免反式脂肪。\n4. 控制总热量：轻食餐通常控制在 400-600 大卡/餐，但不建议低于基础代谢率。\n\n轻食常见误区：\n- 只吃沙拉：长期只吃生冷食物容易伤脾胃，中餐的蒸煮方式同样健康。\n- 不吃碳水：完全戒碳水会导致注意力下降、情绪低落，适量粗粮是必要的。\n- 沙拉酱随意加：一勺蛋黄酱约100大卡，热量可能比蔬菜本身还高。\n\n建议每周安排3-4天轻食日，其余时间正常饮食，既不会觉得太\"苦\"，也能逐步改善饮食结构。', 3, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (4, '每日饮水量', '一天到底该喝多少水？科学饮水指南', '饮食', '水是生命之源，人体约60%由水组成。每天充足的饮水对维持身体机能至关重要。\n\n《中国居民膳食指南》建议：成年男性每天饮水1700毫升，女性1500毫升。但这并非绝对标准，实际需水量因人而异，取决于运动量、气温、身体状况等因素。\n\n科学饮水小建议：\n1. 少量多次：不要等渴了再喝，每隔1-2小时补充150-200毫升水。\n2. 晨起一杯水：起床后空腹喝一杯温水，有助于唤醒身体、促进肠道蠕动。\n3. 运动前后补水：运动前30分钟喝200-300毫升，运动中每15-20分钟少量补充。\n4. 观察尿液颜色：淡黄色为正常，深黄色提示需要补水，无色则可能饮水过量。\n\n注意：含糖饮料、浓茶和咖啡不能替代白开水。白开水仍是最健康、最经济的选择。', 4, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (5, '午睡的艺术', '正确午睡，下午精力充沛不犯困', '睡眠', '午睡被誉为\"身体的充电站\"，适当的午睡能显著提升下午的工作效率和认知能力。\n\n午睡的最佳实践：\n1. 时长控制：10-20分钟为最佳，称为\"能量午睡\"。超过30分钟容易进入深睡眠，醒来反而更加昏沉。\n2. 最佳时间：下午1-3点之间，这是人体生物钟的\"低谷期\"，最容易入睡。\n3. 姿势正确：平躺最佳，如条件不允许，靠在椅背上比趴在桌上更好。\n4. 使用眼罩和耳塞：帮助更快入睡，提高午睡质量。\n5. 设好闹钟：避免睡过头，控制在20分钟以内。\n\n需要注意的是，如果晚上有失眠问题，建议缩短或取消午睡，因为白天睡眠可能影响晚上的入睡。', 5, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (6, '控盐减钠', '少一点盐，多一点健康', '饮食', '高盐饮食是高血压的重要风险因素。世界卫生组织建议成人每日食盐摄入量不超过5克（约一个啤酒瓶盖的量）。\n\n减盐小技巧：\n1. 使用定量盐勺：逐步减少用盐量，让味蕾慢慢适应。\n2. 出锅前放盐：此时盐附着在表面，少量就能感受到咸味。\n3. 善用替代调味品：用醋、柠檬汁、香料、葱姜蒜等替代部分盐。\n4. 警惕\"隐形盐\"：酱油、蚝油、味精、酱料、加工肉制品都含有大量钠。\n5. 多看营养标签：选购食品时关注钠含量，选择低钠产品。\n\n研究显示，每天减少1克盐摄入，可使收缩压降低约1-2mmHg。长期坚持减盐，对预防心血管疾病意义重大。', 6, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (7, '每天走多少步', '步数不是越多越好，科学步行指南', '运动', '\"日行万步\"是很多人追求的目标，但科学研究表明，步数的健康收益存在\"天花板效应\"。\n\n最新研究发现：\n- 60岁以下成年人：每天8000-10000步最有益健康。\n- 60岁以上老年人：每天6000-8000步即可获得最大健康收益。\n- 超过10000步后，额外收益显著下降。\n\n比步数更重要的是步行质量：\n1. 速度：每分钟100步以上的\"快走\"效果更佳。\n2. 时长：每次持续30分钟以上效果更好。\n3. 姿势：抬头挺胸、收腹、自然摆臂。\n4. 频率：每周坚持5天以上。\n\n记住：久坐的危害不能靠走路完全抵消。除了走路，也要注意减少久坐时间，每坐1小时起来活动5分钟。', 7, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (8, '深呼吸减压法', '随时随地可以做的心理放松练习', '心理', '现代生活节奏快，压力无处不在。学会管理压力，对身心健康至关重要。深呼吸是最简单有效的即时减压方法。\n\n腹式呼吸练习（4-7-8呼吸法）：\n1. 找一个安静的地方，坐直或躺下，一只手放在腹部。\n2. 用鼻子深深吸气，心中默数4秒，感受腹部鼓起。\n3. 屏住呼吸，默数7秒。\n4. 用嘴巴缓缓呼气，默数8秒，感受腹部收回。\n5. 重复以上步骤3-5次。\n\n其他缓解压力的方式：\n- 每天花10分钟听舒缓的音乐\n- 保持适度的有氧运动\n- 与亲友倾诉，不要把所有压力都憋在心里\n- 如果需要，不要害怕寻求专业心理咨询的帮助\n\n记住：适度的压力是生活的动力，过度的压力才是健康的敌人。', 8, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (9, '早餐的重要性', '一天中最不能省略的一餐', '饮食', '俗话说\"早餐要吃得像皇帝\"，这并非没有道理。经过一整夜的禁食，身体需要补充能量来启动新的一天。\n\n吃早餐的五大好处：\n1. 提供能量：补充肝糖原，为大脑和肌肉提供燃料。\n2. 提高注意力：吃早餐的学生和上班族在上午的表现更好。\n3. 控制体重：吃早餐的人更不容易在午餐时暴饮暴食。\n4. 改善代谢：规律进食有助于维持稳定的血糖水平。\n5. 补充营养：早餐是摄入钙、膳食纤维和维生素的好机会。\n\n一份理想的早餐应该包含：\n- 优质碳水：全麦面包、燕麦、杂粮粥\n- 优质蛋白：鸡蛋、牛奶、豆浆、酸奶\n- 蔬果：一小份水果或蔬菜\n- 健康脂肪：几颗坚果', 9, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (10, '办公室拉伸', '久坐族的5分钟放松操', '运动', '长时间坐在电脑前工作，容易导致颈肩僵硬、腰背酸痛。每小时花5分钟做一些简单的拉伸，能有效缓解不适。\n\n办公室5分钟拉伸动作：\n1. 颈部拉伸（30秒×2）：缓慢低头、抬头、左转、右转，不要快速甩头。\n2. 肩部环绕（30秒×2）：双肩向前画圈10次，再向后画圈10次。\n3. 手腕拉伸（15秒×2）：伸直手臂，用另一只手轻轻向后拉伸掌心。\n4. 坐姿转体（15秒×2）：坐直身体，缓慢向一侧转体，手扶椅背辅助。\n5. 站立后仰（20秒）：站起来，双手叉腰，缓缓向后仰头挺胸。\n6. 腿部伸展（20秒×2）：站立扶桌，向后弯曲一条腿，感受大腿前侧拉伸。\n\n提醒：拉伸时保持缓慢呼吸，感到轻微拉伸感即可，不要勉强到疼痛的程度。', 10, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (11, '电子产品与睡眠', '蓝光如何偷走你的好睡眠', '睡眠', '手机、平板、电脑屏幕发出的蓝光，是影响现代人睡眠质量的重要因素。\n\n蓝光如何影响睡眠：\n人眼视网膜中的感光细胞对蓝光特别敏感。当你在晚上暴露在蓝光下，大脑会误以为还是白天，从而抑制褪黑素（睡眠激素）的分泌，导致入睡困难。\n\n减少蓝光影响的建议：\n1. 睡前1-2小时停止使用电子设备，改为阅读纸质书或听播客。\n2. 开启设备的\"夜间模式\"或\"护眼模式\"，降低蓝光发射。\n3. 佩戴防蓝光眼镜（如果你必须在晚上使用屏幕）。\n4. 使用暖色调灯光代替冷白光作为夜间照明。\n5. 白天多接触自然光，有助于维持正常的昼夜节律。\n\n一个小实验：尝试一周\"睡前无屏幕\"，看看你的入睡速度和睡眠质量是否有明显改善。', 11, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (12, '膳食纤维', '被忽视的第七大营养素', '饮食', '膳食纤维虽然不被人体消化吸收，但它对健康的作用不可小觑。它被称为继蛋白质、脂肪、碳水化合物、维生素、矿物质和水之后的\"第七大营养素\"。\n\n膳食纤维的主要好处：\n1. 促进肠道蠕动，预防便秘。\n2. 增加饱腹感，有助于控制体重。\n3. 延缓餐后血糖上升，对糖尿病患者友好。\n4. 降低血液中的胆固醇水平。\n5. 为肠道益生菌提供\"食物\"（益生元作用）。\n\n富含膳食纤维的食物：\n- 全谷物：燕麦、糙米、全麦面包、荞麦\n- 豆类：黄豆、黑豆、红豆、鹰嘴豆\n- 蔬菜：西兰花、菠菜、芹菜、胡萝卜\n- 水果：苹果（带皮）、香蕉、梨、奇异果\n- 坚果种子：奇亚籽、亚麻籽、杏仁\n\n《中国居民膳食指南》建议每日摄入膳食纤维25-30克。', 12, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (13, '有氧vs无氧', '两种运动方式，如何搭配最科学？', '运动', '有氧运动和无氧运动是两种不同的运动模式，它们各有优势，科学搭配才能获得最佳效果。\n\n有氧运动（如慢跑、游泳、骑车、快走）：\n- 主要消耗脂肪和碳水化合物供能\n- 提升心肺功能和耐力\n- 有助于减脂和改善心血管健康\n- 建议每周150分钟中等强度或75分钟高强度\n\n无氧运动（如举重、俯卧撑、深蹲、短跑）：\n- 主要消耗糖原供能\n- 增加肌肉力量和肌肉量\n- 提高基础代谢率，让你静息时也消耗更多热量\n- 有助于骨骼健康和体型塑造\n- 建议每周2-3次，每次训练不同肌群\n\n最佳搭配：每周3-4天有氧 + 2天力量训练，中间穿插1-2天休息。如果时间有限，高强度间歇训练（HIIT）是兼顾两者的高效选择。', 13, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (14, '正念冥想入门', '每天5分钟，让心灵回归平静', '心理', '正念冥想是一种将注意力集中在当下的练习方法，已被大量科学研究证实对心理健康有益。\n\n正念冥想的好处：\n- 减轻焦虑和抑郁症状\n- 改善注意力和专注力\n- 降低压力激素（皮质醇）水平\n- 改善睡眠质量\n- 增强情绪调节能力\n\n初学者5分钟正念练习：\n1. 找个安静的地方，舒适地坐下，闭上眼睛。\n2. 将注意力放在呼吸上，感受空气从鼻子进入、从嘴巴呼出。\n3. 不需要刻意控制呼吸，只是观察它。\n4. 当思绪飘走时（这完全正常），温和地把注意力带回到呼吸上。\n5. 持续5分钟，慢慢睁开眼睛，感受当下的平静。\n\n刚开始练习时，你可能会觉得\"我做不到\"，这恰恰是正常的。正念就像健身一样，需要持续练习才能看到效果。', 14, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (15, '饭后百步走', '饭后运动，时间和方法很重要', '运动', '\"饭后百步走，活到九十九\"这句老话有科学依据，但饭后运动的时间和方式需要讲究。\n\n饭后运动的科学建议：\n1. 饭后15-30分钟：可以进行缓慢散步，速度不超过每小时3公里。此时运动可以促进胃肠蠕动，帮助消化。\n2. 饭后1小时：可以进行中等强度的运动，如快走、骑车。大部分血液已经从消化系统回流。\n3. 饭后2小时以上：才能进行高强度运动，如跑步、打球、力量训练。此时胃基本排空。\n\n饭后运动的注意事项：\n- 吃得太饱时不要立即运动，先休息30分钟以上。\n- 如果出现腹胀、恶心、腹痛等不适，立即停止运动。\n- 糖尿病患者饭后运动有助于控制餐后血糖，但需在医生指导下进行。\n- 胃食管反流患者饭后至少等1小时再运动，且避免弯腰和仰卧动作。\n\n总体来说，饭后轻度活动有益健康，但要把握\"适度\"原则。', 15, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (16, '肠道健康', '益生菌与益生元，守护你的\"第二大脑\"', '饮食', '肠道被称为人体的\"第二大脑\"，它不仅负责消化吸收，还与免疫系统、情绪调节密切相关。肠道内栖息着数以万亿计的微生物，统称为\"肠道菌群\"。\n\n益生菌 vs 益生元：\n- 益生菌：是对人体有益的活性微生物，常见于酸奶、泡菜、味噌、纳豆等发酵食品中。\n- 益生元：是益生菌的\"食物\"，主要是膳食纤维和低聚糖，存在于洋葱、大蒜、香蕉、芦笋等食物中。\n\n维护肠道健康的建议：\n1. 多吃发酵食品：每天一杯酸奶，适量食用泡菜、味噌等。\n2. 增加膳食纤维摄入：全谷物、蔬菜、水果都是优质来源。\n3. 减少加工食品：高糖、高脂肪的加工食品会破坏肠道菌群平衡。\n4. 不滥用抗生素：抗生素会\"误杀\"有益菌，使用后及时补充益生菌。\n5. 保持规律作息：肠道菌群也有\"生物钟\"，规律饮食有助于维持菌群稳定。', 16, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (17, '跑步入门指南', '从零开始，科学跑步不伤膝盖', '运动', '跑步是最简单、最经济的有氧运动之一，但错误的跑步方式可能导致膝盖损伤。科学跑步，才能跑得更远、更久。\n\n新手跑步计划：\n- 第1-2周：快走30分钟，适应节奏。\n- 第3-4周：跑2分钟+走3分钟，交替进行，共20-30分钟。\n- 第5-6周：跑5分钟+走2分钟，交替进行。\n- 第7-8周：尝试连续慢跑15-20分钟。\n\n保护膝盖的关键：\n1. 选对跑鞋：一双好的跑鞋能吸收60%以上的冲击力。去专业跑步店做足型测试。\n2. 控制步幅：步幅过大会增加膝盖冲击，建议小步高频（每分钟170-180步）。\n3. 前脚掌或中足着地：避免脚后跟重重着地。\n4. 跑前热身、跑后拉伸：每次至少5分钟。\n5. 循序渐进：每周跑量增加不超过10%。\n\n建议：体重较大的朋友可以先从快走或游泳开始，待体重下降后再转为跑步。', 17, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (18, '失眠怎么办', '科学应对失眠，告别数羊的日子', '睡眠', '偶尔失眠不必紧张，但长期失眠（每周3次以上、持续3个月）需要重视。长期失眠不仅影响白天的精力和情绪，还会增加心血管疾病和抑郁症的风险。\n\n认知行为疗法（CBT-I）——失眠的一线治疗方案：\n1. 睡眠限制：减少在床上的非睡眠时间，只在真正困的时候上床。\n2. 刺激控制：床只用于睡觉，不在床上玩手机、看电视或工作。\n3. 放松训练：渐进式肌肉放松、腹式呼吸等帮助身体进入休息状态。\n4. 纠正错误认知：不要过度关注失眠的后果，越担心越睡不着。\n\n日常改善建议：\n- 固定起床时间（比固定入睡时间更重要）。\n- 白天多接触阳光，特别是早晨。\n- 下午2点后避免咖啡因。\n- 睡前1小时远离屏幕，做放松的事。\n- 卧室保持凉爽（18-22°C）、安静、黑暗。\n\n注意：如果自我调整2周仍无改善，建议到医院睡眠科就诊，不要自行长期服用安眠药。', 18, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (19, '补钙指南', '不只是喝牛奶，这些食物也是补钙高手', '饮食', '钙是人体含量最多的矿物质，99%存在于骨骼和牙齿中。成年人每日推荐钙摄入量为800-1000毫克，但调查显示大多数人实际摄入量不足500毫克。\n\n高钙食物排行（每100克含钙量）：\n- 芝麻酱：1170毫克（但通常每次只吃少量）\n- 虾皮：991毫克\n- 牛奶：104毫克（每天300ml即可获得约312毫克）\n- 豆腐（卤水）：138毫克\n- 西兰花：67毫克\n- 坚果（杏仁）：264毫克\n\n促进钙吸收的帮手：\n1. 维生素D：帮助肠道吸收钙。每天晒太阳15-20分钟，或食用鱼肝油、蛋黄。\n2. 维生素K2：帮助钙沉积到骨骼中。纳豆、奶酪是良好来源。\n\n影响钙吸收的\"敌人\"：\n- 高盐饮食：每多摄入1克盐，约多排出6毫克钙。\n- 碳酸饮料：磷酸会影响钙的吸收和利用。\n- 过量咖啡因：每天超过3杯咖啡可能影响钙平衡。\n- 缺乏运动：运动能刺激骨骼生长，久坐则加速钙流失。', 19, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (20, '社交与健康', '良好的人际关系是最好的\"长寿药\"', '心理', '越来越多的研究表明，社交关系的质量与寿命密切相关。孤独感对健康的危害，相当于每天吸15支烟。\n\n社交对健康的益处：\n- 增强免疫系统：积极的社交互动能降低体内炎症水平。\n- 降低心血管疾病风险：有良好社交支持的人，心脏病风险降低30%。\n- 延缓认知衰退：经常社交的老年人，患阿尔茨海默症的风险更低。\n- 改善心理健康：减少焦虑和抑郁的发生率。\n\n如何建立有意义的社交：\n1. 重质不重量：3-5个知心朋友比100个泛泛之交更有价值。\n2. 主动联系：不要等别人来找你，每周主动联系一位朋友。\n3. 参加社群活动：兴趣小组、志愿者活动、社区聚会都是结识新朋友的好机会。\n4. 学会倾听：好的社交不只是表达自己，更是理解他人。\n5. 减少无效社交：如果某个社交让你感到疲惫或不舒服，可以适当减少。\n\n即使你性格内向，也不需要强迫自己变得外向。一两次深入的交谈，比十次表面的寒暄更有益。', 20, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (21, '抗氧化饮食', '对抗自由基，从餐桌开始', '饮食', '自由基是人体代谢过程中产生的不稳定分子，过量的自由基会损伤细胞，加速衰老，并与多种慢性疾病相关。抗氧化物质能中和自由基，保护细胞健康。\n\n常见抗氧化物质及其食物来源：\n- 维生素C：猕猴桃、柑橘、草莓、青椒、西兰花\n- 维生素E：坚果、葵花籽油、牛油果\n- 花青素：蓝莓、紫薯、黑枸杞、紫甘蓝\n- 番茄红素：番茄（加热后更易吸收）、西瓜\n- 儿茶素：绿茶、白茶\n- 姜黄素：姜黄（搭配黑胡椒可提高吸收率20倍）\n\n抗氧化饮食小建议：\n1. 每天吃5种不同颜色的蔬果——\"彩虹饮食法\"。\n2. 能生吃的蔬果尽量生吃，加热会破坏部分维生素C。\n3. 适量喝茶，绿茶的抗氧化能力是红茶的3-5倍。\n4. 少吃油炸食品和加工肉类——它们会产生大量自由基。\n5. 不要依赖抗氧化补充剂，天然食物中的复合抗氧化效果更好。', 21, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (22, '情绪管理', '认识情绪，做情绪的主人', '心理', '情绪本身没有好坏之分，愤怒、悲伤、焦虑都是正常的人类情感。关键在于如何识别和管理它们，而不是压抑或失控。\n\n情绪管理的四步法：\n1. 觉察：当情绪出现时，先暂停，问自己\"我现在感受到的是什么？\"给情绪命名本身就是一种调节。\n2. 接纳：不要评判自己的情绪。\"我不应该生气\"这种想法反而会加重负面情绪。\n3. 理解：思考情绪背后的原因。\"我生气是因为被误解了，还是因为感觉自己不被重视？\"\n4. 选择：在理解之后，选择一个建设性的回应方式，而不是被情绪驱动。\n\n日常情绪调节技巧：\n- 运动：30分钟有氧运动能显著改善情绪。\n- 写日记：把情绪写下来，能帮助理清思路。\n- 深呼吸：4-7-8呼吸法能快速平复激动情绪。\n- 环境切换：离开让你不舒服的场景，去散步或换个房间。\n- 寻求支持：和信任的人聊聊，不要独自承受。\n\n如果情绪问题持续影响你的工作、学习和人际关系，建议寻求专业心理咨询师的帮助。这不是软弱，而是对自己负责。', 22, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (23, '游泳健身', '全身运动之王，关节友好型锻炼', '运动', '游泳被誉为\"最完美的运动\"，它几乎能锻炼到全身所有主要肌群，同时对关节的冲击极小，特别适合体重较大、关节不好或正在康复的人群。\n\n游泳的健康益处：\n- 全身锻炼：一次游泳可以调动手臂、背部、核心、腿部等多个肌群。\n- 心肺功能：持续游泳能显著提升心肺耐力。\n- 关节友好：水的浮力减少了体重对关节的压力，是关节炎患者的最佳运动选择之一。\n- 燃脂效率：游泳30分钟可消耗200-400卡路里，比骑车和快走更高。\n- 改善体态：游泳能增强背部和核心肌群，帮助改善驼背和圆肩。\n\n游泳注意事项：\n1. 选择正规泳池，注意水质卫生。\n2. 游泳前做好热身，特别是肩关节和膝关节。\n3. 初学者建议先学习蛙泳或自由泳，从25米开始逐步增加。\n4. 游泳后及时冲洗身体，清洁耳朵，预防中耳炎。\n5. 饭后1小时再游泳，避免抽筋。', 23, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (24, '枕头的学问', '选对枕头，颈椎不再\"抗议\"', '睡眠', '很多人重视床垫却忽略了枕头。实际上，一个不合适的枕头是导致颈椎问题和睡眠质量差的常见原因。\n\n如何选择合适的枕头：\n- 仰睡者：枕头高度约一个拳头高（8-10厘米），支撑颈部自然弧度。\n- 侧睡者：枕头高度约一个半拳头高（12-15厘米），保持头部与脊柱在一条直线上。\n- 俯睡者：不建议趴睡，如无法改变，选择非常薄的枕头或不用枕头。\n\n常见枕头材质对比：\n- 记忆棉：贴合颈椎曲线，支撑性好，但透气性一般，夏天可能偏热。\n- 乳胶：弹性好，透气性佳，天然防螨，但价格较高。\n- 羽绒：柔软舒适，透气好，但支撑性不足，不适合颈椎有问题的人。\n- 荞麦壳：透气性极佳，可调节高度，但翻身时会有沙沙声。\n\n枕头更换信号：\n- 使用超过2年，弹性明显下降。\n- 早上起床经常脖子僵硬或头痛。\n- 枕头已经变形，无法恢复原状。\n- 对于过敏体质的人，枕头中的尘螨可能引发过敏症状。', 24, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (25, '控糖生活', '不只是糖尿病人的事，每个人都该了解', '饮食', '提到\"控糖\"，很多人以为只是糖尿病患者的事。事实上，控制血糖波动对每个人都很重要——血糖的大幅波动会导致疲倦、饥饿感、注意力下降，长期还会增加代谢综合征的风险。\n\n血糖生成指数（GI）：\n- 高GI食物（>70）：白米饭、白面包、土豆泥、西瓜——吃后血糖快速升高。\n- 中GI食物（56-70）：全麦面包、糙米、葡萄——血糖上升较温和。\n- 低GI食物（<56）：燕麦、豆类、大部分蔬菜——血糖缓慢上升，饱腹感更持久。\n\n稳定血糖的饮食技巧：\n1. 先吃菜、再吃肉、最后吃主食——改变进食顺序就能减缓血糖上升。\n2. 搭配蛋白质和脂肪：单吃碳水升糖快，搭配鸡蛋、坚果等能减缓吸收。\n3. 选择粗粮替代精白米面：糙米、荞麦、藜麦都是好选择。\n4. 少喝含糖饮料：一杯奶茶的含糖量可能超过世卫建议的每日上限。\n5. 饭后散步15-20分钟：有助于平稳餐后血糖。', 25, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (26, '力量训练入门', '不只是增肌，更是骨骼和代谢的守护者', '运动', '很多人（尤其是女性）对力量训练有误解，认为它只会让人\"变壮\"。事实恰恰相反——力量训练是提升基础代谢、预防骨质疏松、改善体态的最佳方式。\n\n力量训练的核心好处：\n- 提高基础代谢：每增加1公斤肌肉，每天多消耗约50-100卡路里。\n- 预防骨质疏松：负重训练刺激骨骼生长，降低骨折风险。\n- 改善体态：加强背部和核心肌群，改善驼背、圆肩。\n- 预防肌肉流失：30岁后每年流失1-2%的肌肉量，力量训练能有效对抗。\n\n新手入门动作（无需器械）：\n1. 深蹲：锻炼大腿和臀部，每组15次×3组。\n2. 俯卧撑：锻炼胸肌和手臂，可以从跪姿开始，每组10次×3组。\n3. 平板支撑：锻炼核心，从20秒开始逐步增加到60秒。\n4. 臀桥：锻炼臀部和下背部，每组15次×3组。\n5. 弓步蹲：锻炼腿部和平衡能力，每侧10次×3组。\n\n建议：每周2-3次，训练不同肌群，中间至少休息一天。感到肌肉酸痛是正常的，但关节疼痛则需要停止并检查动作。', 26, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (27, '感恩练习', '每天写下3件好事，幸福感悄悄提升', '心理', '积极心理学之父马丁·塞利格曼的研究发现，每天记录\"三件好事\"的人，在短短一周内幸福感显著提升，且效果持续长达半年。\n\n什么是感恩练习：\n每天睡前花5分钟，写下今天发生的3件让你感到开心、感激或满意的事，以及它们发生的原因。事情可以很小——一杯好喝的咖啡、同事的一句赞美、看到路边的花开。\n\n为什么有效：\n- 人类大脑天生有\"负面偏好\"，更容易记住不好的事。感恩练习能训练大脑关注积极面。\n- 写下原因比只写事件更重要——它让你深入思考美好事物背后的意义。\n- 长期练习会改变大脑的神经回路，让你更容易发现生活中的美好。\n\n如何坚持：\n1. 选择固定时间：推荐睡前，作为一天的\"积极收尾\"。\n2. 用纸笔或手机备忘录，不用太正式。\n3. 内容要具体：\"今天午餐很好吃\"比\"今天很好\"更有效。\n4. 如果想不出3件，想想\"今天没有发生什么坏事\"也是一种感恩。\n5. 可以和家人一起做，每天分享各自的\"三件好事\"。', 27, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (28, '合理用油', '选对油、用好油，远离心血管疾病', '饮食', '食用油是厨房的必需品，但很多人对\"吃什么油\"\"怎么用油\"并不了解。选错油、用错方式可能增加心血管疾病的风险。\n\n常见食用油的特点：\n- 橄榄油：富含单不饱和脂肪酸，适合凉拌和低温烹饪。\n- 花生油：香味浓郁，适合炒菜，烟点较高。\n- 菜籽油：脂肪酸比例较均衡，性价比高，适合日常烹饪。\n- 亚麻籽油：富含Omega-3，只能凉拌，不能加热。\n- 猪油/黄油：饱和脂肪酸高，少量用于增香可以，不宜大量使用。\n\n健康用油的原则：\n1. 多样化：不要长期只吃一种油，轮换使用不同种类。\n2. 控制总量：每人每天25-30克（约2-3汤匙）。\n3. 控制油温：油冒烟说明温度过高，会产生有害物质。\n4. 避免反复用油：炸过的油不要反复使用，会产生反式脂肪酸。\n5. 减少油炸：多用蒸、煮、炖、凉拌等低油烹饪方式。\n\n购买建议：选择小瓶装，开封后尽快用完。深色玻璃瓶装的油比透明塑料瓶的更不易氧化。', 28, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (29, '久坐的危害', '坐太久，身体在悄悄\"抗议\"', '运动', '世界卫生组织将久坐列为第四大死亡风险因素。研究表明，每天久坐超过8小时且不运动的人，死亡风险与吸烟和肥胖相当。\n\n久坐对身体的影响：\n- 腰椎：久坐时腰椎承受的压力是站立时的1.5倍，容易导致腰椎间盘突出。\n- 颈椎：低头看屏幕使颈椎承受额外20公斤的压力。\n- 心血管：久坐减缓血液循环，增加血栓和心血管疾病风险。\n- 代谢：久坐降低胰岛素敏感性，增加2型糖尿病风险。\n- 心理：长时间久坐与焦虑、抑郁的发生率增加相关。\n\n对抗久坐的方法：\n1. 20-20-20法则：每坐20分钟，看20英尺（6米）远的地方20秒。\n2. 每小时起身活动：去接杯水、上个厕所、伸展一下，哪怕只站起来1分钟也好。\n3. 站立办公：如果有条件，交替使用坐姿和站姿办公。\n4. 接电话时站起来走动。\n5. 用小水杯代替大水杯——强迫自己多走几趟去接水。\n\n记住：久坐的危害不能靠每天运动1小时来完全抵消。关键是打断连续久坐，频繁起身活动。', 29, '2026-06-08 21:11:48');
INSERT INTO `knowledge_articles` VALUES (30, '数字排毒', '适度远离屏幕，找回真实的生活', '心理', '智能手机让生活更便利，但也让我们不知不觉中花了太多时间在屏幕上。调查显示，中国成年人平均每天使用手机超过5小时。过度使用手机不仅影响视力和颈椎，还与焦虑、注意力下降和睡眠问题密切相关。\n\n数字排毒的实用方法：\n1. 设置屏幕使用时间：利用手机自带的\"屏幕使用时间\"功能，给社交媒体设定每日上限（如30分钟）。\n2. 建立\"无手机区\"：卧室和餐桌是两个最值得设立的\"无手机区\"。\n3. 关闭非必要通知：只保留电话、短信和重要工作App的通知。\n4. 早晨30分钟不碰手机：起床后先洗漱、吃早餐，再看手机。\n5. 用实体物品替代：用实体闹钟替代手机闹钟，用纸质书替代电子书。\n\n数字排毒不是戒掉手机，而是有意识地控制使用时间和方式。你可以尝试：\n- 每周选一个晚上进行\"无屏幕之夜\"——读书、散步、和家人聊天。\n- 出门吃饭时不带手机，专注于食物和同伴。\n- 把社交媒体App从手机主屏幕移走，放到第三页或文件夹里，减少无意识打开的频率。\n\n你不需要彻底远离数字世界，只需要重新成为手机的主人，而不是手机的奴隶。', 30, '2026-06-08 21:11:48');

-- ----------------------------
-- Table structure for knowledge_favorites
-- ----------------------------
DROP TABLE IF EXISTS `knowledge_favorites`;
CREATE TABLE `knowledge_favorites`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `article_id` int NOT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_user_article`(`user_id` ASC, `article_id` ASC) USING BTREE,
  INDEX `article_id`(`article_id` ASC) USING BTREE,
  CONSTRAINT `knowledge_favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `knowledge_favorites_ibfk_2` FOREIGN KEY (`article_id`) REFERENCES `knowledge_articles` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of knowledge_favorites
-- ----------------------------

-- ----------------------------
-- Table structure for reminder_plans
-- ----------------------------
DROP TABLE IF EXISTS `reminder_plans`;
CREATE TABLE `reminder_plans`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `plan_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '前端生成的UUID',
  `plan_type` int NULL DEFAULT 0 COMMENT '0=饮水 1=用药',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '',
  `time` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '08:00' COMMENT 'HH:MM',
  `dosage` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '',
  `is_enabled` tinyint(1) NULL DEFAULT 1,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_plan`(`user_id` ASC, `plan_id` ASC) USING BTREE,
  CONSTRAINT `reminder_plans_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of reminder_plans
-- ----------------------------

-- ----------------------------
-- Table structure for sleep_records
-- ----------------------------
DROP TABLE IF EXISTS `sleep_records`;
CREATE TABLE `sleep_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `date` date NOT NULL,
  `sleep_hours` float NULL DEFAULT 0 COMMENT '总睡眠时长(h)',
  `deep_sleep_hours` float NULL DEFAULT 0 COMMENT '深睡时长(h)',
  `light_sleep_hours` float NULL DEFAULT 0 COMMENT '浅睡时长(h)',
  `bed_time` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '23:00' COMMENT '入睡时间 HH:MM',
  `wake_time` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '07:00' COMMENT '起床时间 HH:MM',
  `quality_score` int NULL DEFAULT 0 COMMENT '睡眠质量评分(0-100)',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_user_date`(`user_id` ASC, `date` ASC) USING BTREE,
  CONSTRAINT `sleep_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 33 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sleep_records
-- ----------------------------
INSERT INTO `sleep_records` VALUES (1, 1, '2026-05-09', 8.3, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (2, 1, '2026-05-10', 6.2, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (3, 1, '2026-05-11', 7.2, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (4, 1, '2026-05-12', 6.3, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (5, 1, '2026-05-13', 6.7, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (6, 1, '2026-05-14', 6.2, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (7, 1, '2026-05-15', 6.3, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (8, 1, '2026-05-16', 5.7, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (9, 1, '2026-05-17', 5.9, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (10, 1, '2026-05-18', 6.6, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (11, 1, '2026-05-19', 7.4, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (12, 1, '2026-05-20', 6, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (13, 1, '2026-05-21', 7.7, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (14, 1, '2026-05-22', 7.1, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (15, 1, '2026-05-23', 5.9, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (16, 1, '2026-05-24', 5.4, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (17, 1, '2026-05-25', 6.8, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (18, 1, '2026-05-26', 7.4, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (19, 1, '2026-05-27', 7.5, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (20, 1, '2026-05-28', 7.2, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (21, 1, '2026-05-29', 7.2, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (22, 1, '2026-05-30', 7.6, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (23, 1, '2026-05-31', 6.5, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (24, 1, '2026-06-01', 6.4, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (25, 1, '2026-06-02', 7.7, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (26, 1, '2026-06-03', 6.5, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (27, 1, '2026-06-04', 5.3, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (28, 1, '2026-06-05', 6.7, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (29, 1, '2026-06-06', 7.9, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (30, 1, '2026-06-07', 5.6, 0, 0, '23:00', '07:00', 0, '2026-06-09 14:37:12');
INSERT INTO `sleep_records` VALUES (32, 1, '2026-06-08', 5.6, 1.9, 3.7, '22:00', '08:00', 70, '2026-06-09 15:16:51');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nick_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '',
  `gender` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '',
  `birthday` date NULL DEFAULT NULL,
  `height` float NULL DEFAULT 0 COMMENT '身高(cm)',
  `weight` float NULL DEFAULT 0 COMMENT '体重(公斤)',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE,
  INDEX `idx_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'demo', '$2b$12$LJ3m4ys8IuH8MpjPLfm9NeYHu0fCKUxqBOKCOsHxYB2sRxI3S.YfO', '健康用户', '男', NULL, 172, 68, '2026-06-08 19:39:38', '2026-06-08 19:39:38');
INSERT INTO `users` VALUES (2, 'luyue', '$2b$12$GkJPxZDhdnEe0ydyRLr2IuURXaM3XyNbK7GdsgeO.BmvqmOqNPHoG', 'luyue', '', NULL, 0, 0, '2026-06-08 19:47:26', '2026-06-08 19:47:26');
INSERT INTO `users` VALUES (3, 'huqi', '$2b$12$kc8Q3aOkr/N1gaHGrU0sGuhq0BuYtuWbGCmyhSlvAouGIAsR2HY2u', 'huqi', '', NULL, 0, 0, '2026-06-08 21:21:32', '2026-06-08 21:21:32');

-- ----------------------------
-- Table structure for water_goals
-- ----------------------------
DROP TABLE IF EXISTS `water_goals`;
CREATE TABLE `water_goals`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `daily_goal` int NULL DEFAULT 8 COMMENT '每日目标杯数',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `water_goals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of water_goals
-- ----------------------------
INSERT INTO `water_goals` VALUES (1, 1, 8, '2026-06-09 14:37:12');
INSERT INTO `water_goals` VALUES (2, 2, 8, '2026-06-09 14:37:12');

-- ----------------------------
-- Table structure for water_intake
-- ----------------------------
DROP TABLE IF EXISTS `water_intake`;
CREATE TABLE `water_intake`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `date` date NOT NULL,
  `cup_count` int NULL DEFAULT 0,
  `daily_goal` int NULL DEFAULT 8,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_user_date`(`user_id` ASC, `date` ASC) USING BTREE,
  CONSTRAINT `water_intake_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 34 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of water_intake
-- ----------------------------
INSERT INTO `water_intake` VALUES (1, 1, '2026-05-09', 4, 8);
INSERT INTO `water_intake` VALUES (2, 1, '2026-05-10', 4, 8);
INSERT INTO `water_intake` VALUES (3, 1, '2026-05-11', 4, 8);
INSERT INTO `water_intake` VALUES (4, 1, '2026-05-12', 9, 8);
INSERT INTO `water_intake` VALUES (5, 1, '2026-05-13', 6, 8);
INSERT INTO `water_intake` VALUES (6, 1, '2026-05-14', 6, 8);
INSERT INTO `water_intake` VALUES (7, 1, '2026-05-15', 3, 8);
INSERT INTO `water_intake` VALUES (8, 1, '2026-05-16', 8, 8);
INSERT INTO `water_intake` VALUES (9, 1, '2026-05-17', 4, 8);
INSERT INTO `water_intake` VALUES (10, 1, '2026-05-18', 7, 8);
INSERT INTO `water_intake` VALUES (11, 1, '2026-05-19', 6, 8);
INSERT INTO `water_intake` VALUES (12, 1, '2026-05-20', 9, 8);
INSERT INTO `water_intake` VALUES (13, 1, '2026-05-21', 8, 8);
INSERT INTO `water_intake` VALUES (14, 1, '2026-05-22', 7, 8);
INSERT INTO `water_intake` VALUES (15, 1, '2026-05-23', 3, 8);
INSERT INTO `water_intake` VALUES (16, 1, '2026-05-24', 3, 8);
INSERT INTO `water_intake` VALUES (17, 1, '2026-05-25', 6, 8);
INSERT INTO `water_intake` VALUES (18, 1, '2026-05-26', 6, 8);
INSERT INTO `water_intake` VALUES (19, 1, '2026-05-27', 5, 8);
INSERT INTO `water_intake` VALUES (20, 1, '2026-05-28', 10, 8);
INSERT INTO `water_intake` VALUES (21, 1, '2026-05-29', 5, 8);
INSERT INTO `water_intake` VALUES (22, 1, '2026-05-30', 8, 8);
INSERT INTO `water_intake` VALUES (23, 1, '2026-05-31', 5, 8);
INSERT INTO `water_intake` VALUES (24, 1, '2026-06-01', 3, 8);
INSERT INTO `water_intake` VALUES (25, 1, '2026-06-02', 10, 8);
INSERT INTO `water_intake` VALUES (26, 1, '2026-06-03', 3, 8);
INSERT INTO `water_intake` VALUES (27, 1, '2026-06-04', 4, 8);
INSERT INTO `water_intake` VALUES (28, 1, '2026-06-05', 9, 8);
INSERT INTO `water_intake` VALUES (29, 1, '2026-06-06', 5, 8);
INSERT INTO `water_intake` VALUES (30, 1, '2026-06-07', 10, 8);
INSERT INTO `water_intake` VALUES (31, 2, '2026-06-08', 1, 8);
INSERT INTO `water_intake` VALUES (32, 1, '2026-06-08', 7, 8);
INSERT INTO `water_intake` VALUES (33, 2, '2026-06-09', 1, 8);

-- ----------------------------
-- Table structure for weight_goals
-- ----------------------------
DROP TABLE IF EXISTS `weight_goals`;
CREATE TABLE `weight_goals`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `target_weight` float NULL DEFAULT 0 COMMENT '目标体重(公斤)',
  `target_date` date NULL DEFAULT NULL COMMENT '目标达成日期',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `weight_goals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of weight_goals
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
