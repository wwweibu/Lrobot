/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: mysql    Database: lrobot_data
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `system_command`
--

DROP TABLE IF EXISTS `system_command`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_command` (
  `id` int NOT NULL AUTO_INCREMENT,
  `command` varchar(255) DEFAULT NULL,
  `user` varchar(255) DEFAULT NULL,
  `platform` varchar(255) DEFAULT NULL,
  `recv_content` text,
  `send_content` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1503 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_data`
--

DROP TABLE IF EXISTS `system_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `text` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=99907 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_feedback`
--

DROP TABLE IF EXISTS `system_feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `questions` json DEFAULT NULL,
  `responses` json DEFAULT NULL,
  `period` timestamp NULL DEFAULT NULL,
  `seq` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_ip`
--

DROP TABLE IF EXISTS `system_ip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_ip` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ip` varchar(45) DEFAULT NULL,
  `time` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip` (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_joke`
--

DROP TABLE IF EXISTS `system_joke`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_joke` (
  `id` int NOT NULL AUTO_INCREMENT,
  `text` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_panel`
--

DROP TABLE IF EXISTS `system_panel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_panel` (
  `id` int NOT NULL AUTO_INCREMENT,
  `func` varchar(255) DEFAULT NULL,
  `answer` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `func` (`func`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_remind`
--

DROP TABLE IF EXISTS `system_remind`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_remind` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` datetime DEFAULT NULL,
  `content` text,
  `user` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_timeline`
--

DROP TABLE IF EXISTS `system_timeline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_timeline` (
  `id` int NOT NULL AUTO_INCREMENT,
  `node_id` int DEFAULT NULL,
  `date` date DEFAULT NULL,
  `event` text,
  `tag` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_wiki`
--

DROP TABLE IF EXISTS `system_wiki`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_wiki` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `group_name` varchar(255) DEFAULT NULL,
  `content` text,
  `sort` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_writer`
--

DROP TABLE IF EXISTS `system_writer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_writer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `organization` varchar(45) DEFAULT NULL,
  `name` varchar(45) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `qq` varchar(20) DEFAULT NULL,
  `remark` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_external_information`
--

DROP TABLE IF EXISTS `user_external_information`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_external_information` (
  `id` int NOT NULL AUTO_INCREMENT,
  `qq` bigint DEFAULT NULL,
  `codename` varchar(50) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `grade` varchar(50) DEFAULT NULL,
  `gender` enum('男','女') DEFAULT NULL,
  `major` varchar(100) DEFAULT NULL,
  `school` varchar(20) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `card_number` varchar(20) DEFAULT NULL,
  `card_id` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `qq` (`qq`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_information`
--

DROP TABLE IF EXISTS `user_information`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_information` (
  `id` int NOT NULL AUTO_INCREMENT,
  `qq` bigint DEFAULT NULL,
  `codename` varchar(50) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `grade` varchar(50) DEFAULT NULL,
  `gender` enum('男','女') DEFAULT NULL,
  `major` varchar(100) DEFAULT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `political_status` varchar(50) DEFAULT NULL,
  `hometown` varchar(100) DEFAULT NULL,
  `card_number` varchar(20) DEFAULT NULL,
  `card_id` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `qq` (`qq`)
) ENGINE=InnoDB AUTO_INCREMENT=2556 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_material`
--

DROP TABLE IF EXISTS `user_material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_material` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `num` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_media`
--

DROP TABLE IF EXISTS `user_media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_media` (
  `id` int NOT NULL AUTO_INCREMENT,
  `filepath` varchar(255) DEFAULT NULL,
  `media_id` varchar(256) DEFAULT NULL,
  `wechat` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `media_json` json DEFAULT NULL,
  `qq` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `media_url` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `filepath` (`filepath`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_nickname`
--

DROP TABLE IF EXISTS `user_nickname`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_nickname` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user` bigint DEFAULT NULL,
  `nickname` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user` (`user`)
) ENGINE=InnoDB AUTO_INCREMENT=614 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_platform`
--

DROP TABLE IF EXISTS `user_platform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_platform` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lr5921` varchar(128) DEFAULT NULL,
  `lr232` varchar(128) DEFAULT NULL,
  `wechat` varchar(128) DEFAULT NULL,
  `bili` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_lr5921` (`lr5921`),
  UNIQUE KEY `ux_lr232` (`lr232`),
  UNIQUE KEY `ux_wechat` (`wechat`),
  UNIQUE KEY `ux_bili` (`bili`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_status`
--

DROP TABLE IF EXISTS `user_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `info` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_user_status` (`user_id`,`status`),
  KEY `ix_status` (`status`),
  CONSTRAINT `fk_user_status_user` FOREIGN KEY (`user_id`) REFERENCES `user_platform` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_subscribe`
--

DROP TABLE IF EXISTS `user_subscribe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_subscribe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user` varchar(255) DEFAULT NULL,
  `sub` varchar(64) DEFAULT NULL,
  `info` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_sub` (`user`,`sub`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_test`
--

DROP TABLE IF EXISTS `user_test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_test` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user` bigint DEFAULT NULL,
  `nickname` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user` (`user`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-10-28 23:06:31
/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: mysql    Database: lrobot_data
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `system_joke`
--

DROP TABLE IF EXISTS `system_joke`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_joke` (
  `id` int NOT NULL AUTO_INCREMENT,
  `text` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_joke`
--

LOCK TABLES `system_joke` WRITE;
/*!40000 ALTER TABLE `system_joke` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `system_joke` VALUES
(16,'华生：“你怎么知道我要喝三分糖？”\r\n福尔摩斯：“你嘴角有蚂蚁排队，说明糖量不足致死；你手机屏保是‘抗糖宣言’，但手指在‘全糖’选项上有划痕……”\r\n华生：“停！我只是今天想放纵！”\r\n福尔摩斯：“……哦，那是我推理错了。”'),
(17,'程序员单膝跪地：“你是我的全局唯一解！”\r\n女友：“那你的前女友呢？”\r\n程序员：“她们是局部最优解，但收敛不到你。”'),
(18,'“先有鸡还是先有蛋？”\r\n哲学家：“先有‘先’这个字。”'),
(19,'数学家向朋友炫耀：「我能用归纳法证明所有人都是光头！」\r\n朋友：「？？？」\r\n数学家：「1个人是光头，假设k个人是光头，那么k+1个人也是光头，证毕。」\r\n朋友：「你漏了归纳基础，第一个人根本不是光头！」\r\n数学家摸头：「啊，我确实是光头。」'),
(20,'警长：“这密室杀人案必须请顶级侦探！”\r\n局长：“不用，把案发现场挂到Airbnb上，写上‘凶宅半价’，凶手会来自首的。”'),
(21,'三个逻辑学家走进酒吧。\r\n酒保问：「三位都要啤酒吗？」\r\n第一个说：「我不知道。」\r\n第二个说：「我也不知道。」\r\n第三个说：「是的，都要。」'),
(22,'女友：“你和前女友纠缠不清是吧？”\r\n男友：“不！我和她的关系是量子态的——你不观测时不存在！”\r\n女友：“那我观测一下你的手机？”\r\n男友：“……系统坍缩了。”'),
(23,'教授：“给猴子一台打字机，迟早打出《莎士比亚全集》！”\r\n学生：“那它们打出‘您访问的网站存在风险’怎么办？”\r\n教授：“……说明猴子当网警了。”'),
(24,'妻子：「你说你爱我，到底有多爱？」\r\n程序员：「我对你的爱，等于我对你的爱加上1。」\r\n妻子：「死循环了是吧？」\r\n（无限递归表白，卒）'),
(25,'老婆：“买颗白菜，顺便带根葱。”\r\n程序员老公：“最优路径是：先到葱摊，因为葱的保质期是白菜的0.3倍；但根据实时人流……”\r\n老婆：“你买了三小时还没回来？！”\r\n老公：“……我在模拟退火算法。”'),
(26,'死者：“我在虚拟世界被杀了！这犯法吗？”\r\n警察：“根据《刑法》第250条，凶手得先证明你是真人。”\r\n死者：“……我微信余额还有3块5！”\r\n警察：“立案了！”'),
(27,'凶手：“我用了完美分尸手法，你绝对找不到证据！”\r\n侦探：“确实，但你把肝扔进了厨余垃圾桶——”\r\n凶手：“所以呢？！”\r\n侦探：“小区垃圾分类奖金被扣了，保洁阿姨供出了你。”'),
(28,'老婆：“买两斤土豆，要表面光滑摩擦系数小的。”\r\n物理学家：“你是要做惯性实验还是炖牛肉？”\r\n老婆：“……要好削皮的。”'),
(29,'凶手：“案发时我在元宇宙挖矿！”\r\n警察：“但你显卡温度记录显示当时在玩《原神》。”\r\n凶手：“……我承认，是我干的。”'),
(30,'客户：“我要一个绝对完美的密室杀人案！”\r\n侦探：“好的，方案是：门没锁，但甲方坚持说它是密室。”');
/*!40000 ALTER TABLE `system_joke` ENABLE KEYS */;
UNLOCK TABLES;
commit;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-10-28 23:06:31
