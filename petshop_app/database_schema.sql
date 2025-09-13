-- ========================================
-- 宠物拍卖平台数据库设计
-- 版本: v1.0
-- 创建时间: 2024-09-13
-- ========================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS petshop_auction 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE petshop_auction;

-- ========================================
-- 1. 用户系统模块 (4张表)
-- ========================================

-- 用户基础信息表
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `phone` varchar(20) NOT NULL COMMENT '手机号',
  `nickname` varchar(50) NOT NULL COMMENT '昵称',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像URL',
  `real_name` varchar(50) DEFAULT NULL COMMENT '真实姓名',
  `id_card` varchar(20) DEFAULT NULL COMMENT '身份证号',
  `gender` tinyint(1) DEFAULT 0 COMMENT '性别: 0未知 1男 2女',
  `birthday` date DEFAULT NULL COMMENT '生日',
  `province` varchar(50) DEFAULT NULL COMMENT '省份',
  `city` varchar(50) DEFAULT NULL COMMENT '城市',
  `balance` decimal(10,2) DEFAULT 0.00 COMMENT '账户余额',
  `points` int(11) DEFAULT 0 COMMENT '积分',
  `status` enum('active','banned','deleted') DEFAULT 'active' COMMENT '状态',
  `last_login_at` timestamp NULL DEFAULT NULL COMMENT '最后登录时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_phone` (`phone`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户基础信息表';

-- 用户认证表
DROP TABLE IF EXISTS `user_auths`;
CREATE TABLE `user_auths` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '用户ID',
  `auth_type` enum('password','wechat','alipay','apple') NOT NULL COMMENT '认证类型',
  `auth_value` varchar(255) NOT NULL COMMENT '认证值(加密后密码/第三方ID)',
  `salt` varchar(32) DEFAULT NULL COMMENT '密码盐值',
  `verified_at` timestamp NULL DEFAULT NULL COMMENT '验证时间',
  `expires_at` timestamp NULL DEFAULT NULL COMMENT '过期时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_auth_type` (`user_id`, `auth_type`),
  KEY `idx_auth_value` (`auth_value`),
  CONSTRAINT `fk_user_auths_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户认证表';

-- 用户地址表
DROP TABLE IF EXISTS `user_addresses`;
CREATE TABLE `user_addresses` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '用户ID',
  `name` varchar(50) NOT NULL COMMENT '收货人姓名',
  `phone` varchar(20) NOT NULL COMMENT '收货人电话',
  `province` varchar(50) NOT NULL COMMENT '省份',
  `city` varchar(50) NOT NULL COMMENT '城市',
  `district` varchar(50) NOT NULL COMMENT '区县',
  `detail` varchar(255) NOT NULL COMMENT '详细地址',
  `postal_code` varchar(10) DEFAULT NULL COMMENT '邮政编码',
  `is_default` tinyint(1) DEFAULT 0 COMMENT '是否默认地址',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_is_default` (`is_default`),
  CONSTRAINT `fk_user_addresses_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户地址表';

-- 用户签到记录表
DROP TABLE IF EXISTS `user_checkins`;
CREATE TABLE `user_checkins` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '用户ID',
  `checkin_date` date NOT NULL COMMENT '签到日期',
  `reward_points` int(11) DEFAULT 0 COMMENT '奖励积分',
  `consecutive_days` int(11) DEFAULT 1 COMMENT '连续签到天数',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_date` (`user_id`, `checkin_date`),
  KEY `idx_checkin_date` (`checkin_date`),
  CONSTRAINT `fk_user_checkins_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户签到记录表';

-- ========================================
-- 2. 商品系统模块 (4张表)
-- ========================================

-- 商品分类表
DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '分类ID',
  `name` varchar(50) NOT NULL COMMENT '分类名称',
  `parent_id` int(11) unsigned DEFAULT NULL COMMENT '父级分类ID',
  `level` tinyint(2) DEFAULT 1 COMMENT '分类层级',
  `sort_order` int(11) DEFAULT 0 COMMENT '排序权重',
  `icon` varchar(255) DEFAULT NULL COMMENT '分类图标',
  `description` text DEFAULT NULL COMMENT '分类描述',
  `status` enum('active','inactive') DEFAULT 'active' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_status_sort` (`status`, `sort_order`),
  CONSTRAINT `fk_categories_parent_id` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- 商品基础表
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '商品ID',
  `seller_id` int(11) unsigned NOT NULL COMMENT '卖家用户ID',
  `category_id` int(11) unsigned NOT NULL COMMENT '分类ID',
  `title` varchar(200) NOT NULL COMMENT '商品标题',
  `description` text DEFAULT NULL COMMENT '商品描述',
  `images` json DEFAULT NULL COMMENT '商品图片JSON数组',
  `video_url` varchar(255) DEFAULT NULL COMMENT '视频链接',
  `type` enum('auction','fixed') DEFAULT 'auction' COMMENT '商品类型: auction拍卖 fixed一口价',
  `status` enum('draft','active','sold','expired','deleted') DEFAULT 'draft' COMMENT '商品状态',
  `location` varchar(100) DEFAULT NULL COMMENT '所在地区',
  `view_count` int(11) DEFAULT 0 COMMENT '浏览次数',
  `favorite_count` int(11) DEFAULT 0 COMMENT '收藏次数',
  `share_count` int(11) DEFAULT 0 COMMENT '分享次数',
  `weight` decimal(8,2) DEFAULT NULL COMMENT '重量(kg)',
  `length` decimal(8,2) DEFAULT NULL COMMENT '长度(cm)',
  `width` decimal(8,2) DEFAULT NULL COMMENT '宽度(cm)',
  `height` decimal(8,2) DEFAULT NULL COMMENT '高度(cm)',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_seller_id` (`seller_id`),
  KEY `idx_category_id` (`category_id`),
  KEY `idx_type_status` (`type`, `status`),
  KEY `idx_created_at` (`created_at`),
  FULLTEXT KEY `ft_title_desc` (`title`, `description`),
  CONSTRAINT `fk_products_seller_id` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_products_category_id` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品基础表';

-- 拍卖商品表
DROP TABLE IF EXISTS `auction_products`;
CREATE TABLE `auction_products` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `product_id` int(11) unsigned NOT NULL COMMENT '商品ID',
  `start_price` decimal(10,2) NOT NULL COMMENT '起拍价',
  `current_price` decimal(10,2) NOT NULL COMMENT '当前价格',
  `reserve_price` decimal(10,2) DEFAULT NULL COMMENT '保留价',
  `bid_increment` decimal(10,2) DEFAULT 1.00 COMMENT '加价幅度',
  `start_time` timestamp NOT NULL COMMENT '拍卖开始时间',
  `end_time` timestamp NOT NULL COMMENT '拍卖结束时间',
  `bid_count` int(11) DEFAULT 0 COMMENT '出价次数',
  `auto_extend` tinyint(1) DEFAULT 0 COMMENT '是否自动延时',
  `extend_minutes` int(11) DEFAULT 5 COMMENT '延时分钟数',
  `winner_id` int(11) unsigned DEFAULT NULL COMMENT '获胜者用户ID',
  `final_price` decimal(10,2) DEFAULT NULL COMMENT '最终成交价',
  `status` enum('pending','active','ended','cancelled') DEFAULT 'pending' COMMENT '拍卖状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_product_id` (`product_id`),
  KEY `idx_status_end_time` (`status`, `end_time`),
  KEY `idx_winner_id` (`winner_id`),
  CONSTRAINT `fk_auction_products_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_auction_products_winner_id` FOREIGN KEY (`winner_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='拍卖商品表';

-- 一口价商品表
DROP TABLE IF EXISTS `fixed_products`;
CREATE TABLE `fixed_products` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `product_id` int(11) unsigned NOT NULL COMMENT '商品ID',
  `price` decimal(10,2) NOT NULL COMMENT '销售价格',
  `original_price` decimal(10,2) DEFAULT NULL COMMENT '原价',
  `stock` int(11) DEFAULT 1 COMMENT '库存数量',
  `sales_count` int(11) DEFAULT 0 COMMENT '销售数量',
  `min_purchase` int(11) DEFAULT 1 COMMENT '最少购买数量',
  `max_purchase` int(11) DEFAULT NULL COMMENT '最多购买数量',
  `shipping_fee` decimal(8,2) DEFAULT 0.00 COMMENT '运费',
  `free_shipping_amount` decimal(10,2) DEFAULT NULL COMMENT '包邮金额',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_product_id` (`product_id`),
  KEY `idx_price` (`price`),
  CONSTRAINT `fk_fixed_products_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='一口价商品表';

-- ========================================
-- 3. 竞拍系统模块 (3张表)
-- ========================================

-- 竞拍记录表
DROP TABLE IF EXISTS `bids`;
CREATE TABLE `bids` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '竞拍ID',
  `product_id` int(11) unsigned NOT NULL COMMENT '商品ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '竞拍用户ID',
  `bid_amount` decimal(10,2) NOT NULL COMMENT '出价金额',
  `bid_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '出价时间',
  `is_auto_bid` tinyint(1) DEFAULT 0 COMMENT '是否自动竞拍',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` text DEFAULT NULL COMMENT '用户代理',
  `status` enum('active','cancelled','outbid','winning') DEFAULT 'active' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_bid_time` (`bid_time`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_bids_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_bids_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='竞拍记录表';

-- 自动竞拍设置表
DROP TABLE IF EXISTS `auto_bids`;
CREATE TABLE `auto_bids` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '用户ID',
  `product_id` int(11) unsigned NOT NULL COMMENT '商品ID',
  `max_amount` decimal(10,2) NOT NULL COMMENT '最大出价金额',
  `increment` decimal(10,2) NOT NULL COMMENT '每次加价金额',
  `current_bid` decimal(10,2) DEFAULT 0.00 COMMENT '当前已出价金额',
  `bid_count` int(11) DEFAULT 0 COMMENT '已出价次数',
  `status` enum('active','paused','completed','cancelled') DEFAULT 'active' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_product` (`user_id`, `product_id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_auto_bids_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_auto_bids_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自动竞拍设置表';

-- 拍卖结果表
DROP TABLE IF EXISTS `auction_results`;
CREATE TABLE `auction_results` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `product_id` int(11) unsigned NOT NULL COMMENT '商品ID',
  `winner_id` int(11) unsigned DEFAULT NULL COMMENT '获胜者用户ID',
  `final_price` decimal(10,2) NOT NULL COMMENT '最终成交价',
  `bid_count` int(11) DEFAULT 0 COMMENT '总出价次数',
  `start_time` timestamp NOT NULL COMMENT '开始时间',
  `end_time` timestamp NOT NULL COMMENT '结束时间',
  `status` enum('success','failed','cancelled') DEFAULT 'success' COMMENT '拍卖结果',
  `failure_reason` varchar(255) DEFAULT NULL COMMENT '失败原因',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_product_id` (`product_id`),
  KEY `idx_winner_id` (`winner_id`),
  KEY `idx_end_time` (`end_time`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_auction_results_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_auction_results_winner_id` FOREIGN KEY (`winner_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='拍卖结果表';

-- ========================================
-- 4. 订单交易模块 (4张表)
-- ========================================

-- 订单主表
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `order_no` varchar(32) NOT NULL COMMENT '订单号',
  `buyer_id` int(11) unsigned NOT NULL COMMENT '买家用户ID',
  `seller_id` int(11) unsigned NOT NULL COMMENT '卖家用户ID',
  `product_id` int(11) unsigned NOT NULL COMMENT '商品ID',
  `quantity` int(11) DEFAULT 1 COMMENT '购买数量',
  `unit_price` decimal(10,2) NOT NULL COMMENT '单价',
  `total_amount` decimal(10,2) NOT NULL COMMENT '商品总金额',
  `shipping_fee` decimal(8,2) DEFAULT 0.00 COMMENT '运费',
  `discount_amount` decimal(8,2) DEFAULT 0.00 COMMENT '优惠金额',
  `final_amount` decimal(10,2) NOT NULL COMMENT '实付金额',
  `payment_method` enum('alipay','wechat','balance','bank') DEFAULT 'alipay' COMMENT '支付方式',
  `status` enum('pending','paid','shipped','delivered','completed','cancelled','refunded') DEFAULT 'pending' COMMENT '订单状态',
  `remark` text DEFAULT NULL COMMENT '订单备注',
  `shipping_address` json DEFAULT NULL COMMENT '收货地址JSON',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_buyer_id` (`buyer_id`),
  KEY `idx_seller_id` (`seller_id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_orders_buyer_id` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_orders_seller_id` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_orders_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单主表';

-- 支付记录表
DROP TABLE IF EXISTS `payments`;
CREATE TABLE `payments` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '支付ID',
  `order_id` int(11) unsigned NOT NULL COMMENT '订单ID',
  `payment_no` varchar(32) NOT NULL COMMENT '支付流水号',
  `third_party_no` varchar(64) DEFAULT NULL COMMENT '第三方支付订单号',
  `payment_method` enum('alipay','wechat','balance','bank') NOT NULL COMMENT '支付方式',
  `amount` decimal(10,2) NOT NULL COMMENT '支付金额',
  `status` enum('pending','success','failed','cancelled') DEFAULT 'pending' COMMENT '支付状态',
  `callback_data` json DEFAULT NULL COMMENT '支付回调数据',
  `paid_at` timestamp NULL DEFAULT NULL COMMENT '支付成功时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_payment_no` (`payment_no`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_third_party_no` (`third_party_no`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_payments_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付记录表';

-- 物流信息表
DROP TABLE IF EXISTS `logistics`;
CREATE TABLE `logistics` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `order_id` int(11) unsigned NOT NULL COMMENT '订单ID',
  `express_company` varchar(50) DEFAULT NULL COMMENT '快递公司',
  `express_code` varchar(20) DEFAULT NULL COMMENT '快递公司编码',
  `tracking_number` varchar(50) DEFAULT NULL COMMENT '快递单号',
  `sender_name` varchar(50) DEFAULT NULL COMMENT '发件人',
  `sender_phone` varchar(20) DEFAULT NULL COMMENT '发件人电话',
  `sender_address` varchar(255) DEFAULT NULL COMMENT '发件地址',
  `receiver_name` varchar(50) DEFAULT NULL COMMENT '收件人',
  `receiver_phone` varchar(20) DEFAULT NULL COMMENT '收件人电话',
  `receiver_address` varchar(255) DEFAULT NULL COMMENT '收件地址',
  `status` enum('pending','picked','transit','delivered','exception','rejected') DEFAULT 'pending' COMMENT '物流状态',
  `tracking_info` json DEFAULT NULL COMMENT '物流跟踪信息JSON',
  `shipped_at` timestamp NULL DEFAULT NULL COMMENT '发货时间',
  `delivered_at` timestamp NULL DEFAULT NULL COMMENT '签收时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_id` (`order_id`),
  KEY `idx_tracking_number` (`tracking_number`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_logistics_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物流信息表';

-- 退款记录表
DROP TABLE IF EXISTS `refunds`;
CREATE TABLE `refunds` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '退款ID',
  `order_id` int(11) unsigned NOT NULL COMMENT '订单ID',
  `refund_no` varchar(32) NOT NULL COMMENT '退款单号',
  `third_party_no` varchar(64) DEFAULT NULL COMMENT '第三方退款单号',
  `refund_amount` decimal(10,2) NOT NULL COMMENT '退款金额',
  `refund_reason` varchar(255) DEFAULT NULL COMMENT '退款原因',
  `status` enum('pending','processing','success','failed') DEFAULT 'pending' COMMENT '退款状态',
  `processed_at` timestamp NULL DEFAULT NULL COMMENT '处理时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_refund_no` (`refund_no`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_refunds_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='退款记录表';

-- ========================================
-- 5. 消息聊天模块 (3张表)
-- ========================================

-- 对话表
DROP TABLE IF EXISTS `conversations`;
CREATE TABLE `conversations` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '对话ID',
  `user_id1` int(11) unsigned NOT NULL COMMENT '用户1 ID',
  `user_id2` int(11) unsigned NOT NULL COMMENT '用户2 ID',
  `product_id` int(11) unsigned DEFAULT NULL COMMENT '关联商品ID',
  `last_message_id` int(11) unsigned DEFAULT NULL COMMENT '最后一条消息ID',
  `user1_unread_count` int(11) DEFAULT 0 COMMENT '用户1未读消息数',
  `user2_unread_count` int(11) DEFAULT 0 COMMENT '用户2未读消息数',
  `user1_deleted` tinyint(1) DEFAULT 0 COMMENT '用户1是否删除对话',
  `user2_deleted` tinyint(1) DEFAULT 0 COMMENT '用户2是否删除对话',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users` (`user_id1`, `user_id2`),
  KEY `idx_user_id1` (`user_id1`),
  KEY `idx_user_id2` (`user_id2`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_updated_at` (`updated_at`),
  CONSTRAINT `fk_conversations_user_id1` FOREIGN KEY (`user_id1`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_conversations_user_id2` FOREIGN KEY (`user_id2`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_conversations_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话表';

-- 消息表
DROP TABLE IF EXISTS `messages`;
CREATE TABLE `messages` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `conversation_id` int(11) unsigned NOT NULL COMMENT '对话ID',
  `sender_id` int(11) unsigned NOT NULL COMMENT '发送者用户ID',
  `receiver_id` int(11) unsigned NOT NULL COMMENT '接收者用户ID',
  `message_type` enum('text','image','voice','video','system') DEFAULT 'text' COMMENT '消息类型',
  `content` text DEFAULT NULL COMMENT '消息内容',
  `media_url` varchar(255) DEFAULT NULL COMMENT '媒体文件URL',
  `media_size` int(11) DEFAULT NULL COMMENT '媒体文件大小(字节)',
  `media_duration` int(11) DEFAULT NULL COMMENT '媒体时长(秒)',
  `is_read` tinyint(1) DEFAULT 0 COMMENT '是否已读',
  `read_at` timestamp NULL DEFAULT NULL COMMENT '已读时间',
  `is_deleted` tinyint(1) DEFAULT 0 COMMENT '是否已删除',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_conversation_id` (`conversation_id`),
  KEY `idx_sender_id` (`sender_id`),
  KEY `idx_receiver_id` (`receiver_id`),
  KEY `idx_is_read` (`is_read`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_messages_conversation_id` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_messages_sender_id` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_messages_receiver_id` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息表';

-- 系统通知表
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '通知ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '用户ID',
  `type` enum('system','auction','order','payment','message') DEFAULT 'system' COMMENT '通知类型',
  `title` varchar(100) NOT NULL COMMENT '通知标题',
  `content` text DEFAULT NULL COMMENT '通知内容',
  `data` json DEFAULT NULL COMMENT '附加数据JSON',
  `is_read` tinyint(1) DEFAULT 0 COMMENT '是否已读',
  `read_at` timestamp NULL DEFAULT NULL COMMENT '已读时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_type` (`type`),
  KEY `idx_is_read` (`is_read`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_notifications_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统通知表';

-- ========================================
-- 6. 社交功能模块 (4张表)
-- ========================================

-- 宠物社区动态表
DROP TABLE IF EXISTS `social_posts`;
CREATE TABLE `social_posts` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '动态ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '用户ID',
  `content` text DEFAULT NULL COMMENT '动态内容',
  `images` json DEFAULT NULL COMMENT '图片JSON数组',
  `video_url` varchar(255) DEFAULT NULL COMMENT '视频URL',
  `location` varchar(100) DEFAULT NULL COMMENT '位置信息',
  `pet_type` varchar(50) DEFAULT NULL COMMENT '宠物类型',
  `tags` json DEFAULT NULL COMMENT '标签JSON数组',
  `like_count` int(11) DEFAULT 0 COMMENT '点赞数',
  `comment_count` int(11) DEFAULT 0 COMMENT '评论数',
  `share_count` int(11) DEFAULT 0 COMMENT '分享数',
  `view_count` int(11) DEFAULT 0 COMMENT '浏览数',
  `is_top` tinyint(1) DEFAULT 0 COMMENT '是否置顶',
  `status` enum('active','hidden','deleted') DEFAULT 'active' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status_created` (`status`, `created_at`),
  KEY `idx_is_top` (`is_top`),
  CONSTRAINT `fk_social_posts_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='宠物社区动态表';

-- 社区互动记录表
DROP TABLE IF EXISTS `social_interactions`;
CREATE TABLE `social_interactions` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '用户ID',
  `post_id` int(11) unsigned NOT NULL COMMENT '动态ID',
  `type` enum('like','comment','share','report') NOT NULL COMMENT '互动类型',
  `content` text DEFAULT NULL COMMENT '评论内容(仅评论类型)',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_post_type` (`user_id`, `post_id`, `type`),
  KEY `idx_post_id` (`post_id`),
  KEY `idx_type_created` (`type`, `created_at`),
  CONSTRAINT `fk_social_interactions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_social_interactions_post_id` FOREIGN KEY (`post_id`) REFERENCES `social_posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='社区互动记录表';

-- 本地服务商表
DROP TABLE IF EXISTS `local_services`;
CREATE TABLE `local_services` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '服务商ID',
  `name` varchar(100) NOT NULL COMMENT '服务商名称',
  `type` enum('pet_store','aquarium_design','door_service','grooming') NOT NULL COMMENT '服务类型',
  `description` text DEFAULT NULL COMMENT '服务描述',
  `images` json DEFAULT NULL COMMENT '服务图片JSON数组',
  `contact_phone` varchar(20) DEFAULT NULL COMMENT '联系电话',
  `address` varchar(255) DEFAULT NULL COMMENT '服务地址',
  `latitude` decimal(10,7) DEFAULT NULL COMMENT '纬度',
  `longitude` decimal(10,7) DEFAULT NULL COMMENT '经度',
  `service_area` varchar(255) DEFAULT NULL COMMENT '服务区域',
  `business_hours` json DEFAULT NULL COMMENT '营业时间JSON',
  `price_range` varchar(50) DEFAULT NULL COMMENT '价格区间',
  `rating` decimal(3,2) DEFAULT 0.00 COMMENT '评分',
  `review_count` int(11) DEFAULT 0 COMMENT '评价数量',
  `is_verified` tinyint(1) DEFAULT 0 COMMENT '是否认证',
  `status` enum('active','inactive','suspended') DEFAULT 'active' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_type_status` (`type`, `status`),
  KEY `idx_location` (`latitude`, `longitude`),
  KEY `idx_rating` (`rating`),
  CONSTRAINT `chk_rating` CHECK (`rating` >= 0 AND `rating` <= 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='本地服务商表';

-- 服务评价表
DROP TABLE IF EXISTS `service_reviews`;
CREATE TABLE `service_reviews` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '评价ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '用户ID',
  `service_id` int(11) unsigned NOT NULL COMMENT '服务商ID',
  `rating` tinyint(1) NOT NULL COMMENT '评分(1-5)',
  `content` text DEFAULT NULL COMMENT '评价内容',
  `images` json DEFAULT NULL COMMENT '评价图片JSON数组',
  `reply` text DEFAULT NULL COMMENT '商家回复',
  `replied_at` timestamp NULL DEFAULT NULL COMMENT '回复时间',
  `is_anonymous` tinyint(1) DEFAULT 0 COMMENT '是否匿名',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_service_id` (`service_id`),
  KEY `idx_rating` (`rating`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_service_reviews_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_service_reviews_service_id` FOREIGN KEY (`service_id`) REFERENCES `local_services` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_review_rating` CHECK (`rating` >= 1 AND `rating` <= 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='服务评价表';

-- ========================================
-- 7. 其他辅助表 (5张表)
-- ========================================

-- 用户收藏表
DROP TABLE IF EXISTS `user_favorites`;
CREATE TABLE `user_favorites` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int(11) unsigned NOT NULL COMMENT '用户ID',
  `product_id` int(11) unsigned NOT NULL COMMENT '商品ID',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_product` (`user_id`, `product_id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_user_favorites_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_favorites_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- 搜索历史表
DROP TABLE IF EXISTS `search_history`;
CREATE TABLE `search_history` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int(11) unsigned DEFAULT NULL COMMENT '用户ID(游客为空)',
  `keyword` varchar(100) NOT NULL COMMENT '搜索关键词',
  `result_count` int(11) DEFAULT 0 COMMENT '搜索结果数',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP地址',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_keyword` (`keyword`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_search_history_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='搜索历史表';

-- 热门搜索表
DROP TABLE IF EXISTS `hot_keywords`;
CREATE TABLE `hot_keywords` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `keyword` varchar(100) NOT NULL COMMENT '关键词',
  `search_count` int(11) DEFAULT 1 COMMENT '搜索次数',
  `weight` int(11) DEFAULT 0 COMMENT '权重分数',
  `is_recommended` tinyint(1) DEFAULT 0 COMMENT '是否推荐',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_keyword` (`keyword`),
  KEY `idx_weight` (`weight`),
  KEY `idx_search_count` (`search_count`),
  KEY `idx_is_recommended` (`is_recommended`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='热门搜索表';

-- 轮播图表
DROP TABLE IF EXISTS `banners`;
CREATE TABLE `banners` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '轮播图ID',
  `title` varchar(100) NOT NULL COMMENT '轮播图标题',
  `image_url` varchar(255) NOT NULL COMMENT '图片URL',
  `link_url` varchar(255) DEFAULT NULL COMMENT '跳转链接',
  `link_type` enum('none','product','category','url','page') DEFAULT 'none' COMMENT '链接类型',
  `target_id` int(11) unsigned DEFAULT NULL COMMENT '目标ID(商品ID/分类ID等)',
  `position` enum('home_top','category_top','product_detail') DEFAULT 'home_top' COMMENT '显示位置',
  `sort_order` int(11) DEFAULT 0 COMMENT '排序权重',
  `start_time` timestamp NULL DEFAULT NULL COMMENT '开始时间',
  `end_time` timestamp NULL DEFAULT NULL COMMENT '结束时间',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '是否启用',
  `click_count` int(11) DEFAULT 0 COMMENT '点击次数',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_position_sort` (`position`, `sort_order`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_time_range` (`start_time`, `end_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='轮播图表';

-- 系统配置表
DROP TABLE IF EXISTS `system_configs`;
CREATE TABLE `system_configs` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `config_key` varchar(50) NOT NULL COMMENT '配置键',
  `config_value` text DEFAULT NULL COMMENT '配置值',
  `config_type` enum('string','number','boolean','json') DEFAULT 'string' COMMENT '配置类型',
  `description` varchar(255) DEFAULT NULL COMMENT '配置描述',
  `is_public` tinyint(1) DEFAULT 0 COMMENT '是否公开(前端可访问)',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- ========================================
-- 8. 插入初始数据
-- ========================================

-- 插入系统配置
INSERT INTO `system_configs` (`config_key`, `config_value`, `config_type`, `description`, `is_public`) VALUES
('app_name', '宠物拍卖平台', 'string', '应用名称', 1),
('app_version', '1.0.0', 'string', '应用版本', 1),
('default_avatar', '/assets/images/default_avatar.png', 'string', '默认头像', 1),
('bid_increment_min', '1.00', 'number', '最小加价幅度', 1),
('auction_extend_time', '5', 'number', '拍卖延时分钟数', 1),
('upload_max_size', '10485760', 'number', '文件上传最大大小(字节)', 0),
('jwt_secret', 'your-jwt-secret-key', 'string', 'JWT密钥', 0);

-- 插入商品分类
INSERT INTO `categories` (`name`, `parent_id`, `level`, `sort_order`, `icon`) VALUES
('宠物', NULL, 1, 1, 'pets'),
('猫咪', 1, 2, 1, 'cat'),
('狗狗', 1, 2, 2, 'dog'),
('鸟类', 1, 2, 3, 'bird'),
('水族', NULL, 1, 2, 'aquarium'),
('观赏鱼', 5, 2, 1, 'fish'),
('水草', 5, 2, 2, 'plant'),
('鱼缸设备', 5, 2, 3, 'equipment'),
('宠物用品', NULL, 1, 3, 'supplies'),
('猫用品', 9, 2, 1, 'cat_supplies'),
('狗用品', 9, 2, 2, 'dog_supplies');

-- 插入热门搜索关键词
INSERT INTO `hot_keywords` (`keyword`, `search_count`, `weight`, `is_recommended`) VALUES
('英短蓝猫', 156, 100, 1),
('金毛犬', 143, 95, 1),
('布偶猫', 132, 90, 1),
('比熊犬', 128, 88, 1),
('观赏鱼', 98, 85, 1),
('鱼缸', 87, 80, 1),
('猫粮', 76, 75, 1),
('狗粮', 72, 72, 1);

-- 创建索引优化
CREATE INDEX idx_products_search ON products(title, status, type, created_at);
CREATE INDEX idx_bids_search ON bids(product_id, bid_amount, bid_time);
CREATE INDEX idx_orders_search ON orders(buyer_id, seller_id, status, created_at);
CREATE INDEX idx_messages_search ON messages(conversation_id, created_at, is_read);

-- ========================================
-- 数据库设计完成
-- ========================================