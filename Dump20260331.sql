-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: payment_integration
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add api call errors',6,'add_apicallerrors'),(22,'Can change api call errors',6,'change_apicallerrors'),(23,'Can delete api call errors',6,'delete_apicallerrors'),(24,'Can view api call errors',6,'view_apicallerrors'),(25,'Can add bank details',7,'add_bankdetails'),(26,'Can change bank details',7,'change_bankdetails'),(27,'Can delete bank details',7,'delete_bankdetails'),(28,'Can view bank details',7,'view_bankdetails'),(29,'Can add processed deposits',8,'add_processeddeposits'),(30,'Can change processed deposits',8,'change_processeddeposits'),(31,'Can delete processed deposits',8,'delete_processeddeposits'),(32,'Can view processed deposits',8,'view_processeddeposits'),(33,'Can add user login history',9,'add_userloginhistory'),(34,'Can change user login history',9,'change_userloginhistory'),(35,'Can delete user login history',9,'delete_userloginhistory'),(36,'Can view user login history',9,'view_userloginhistory'),(37,'Can add users',10,'add_users'),(38,'Can change users',10,'change_users'),(39,'Can delete users',10,'delete_users'),(40,'Can view users',10,'view_users'),(41,'Can add appym',11,'add_appym'),(42,'Can change appym',11,'change_appym'),(43,'Can delete appym',11,'delete_appym'),(44,'Can view appym',11,'view_appym'),(45,'Can add aptcr',12,'add_aptcr'),(46,'Can change aptcr',12,'change_aptcr'),(47,'Can delete aptcr',12,'delete_aptcr'),(48,'Can view aptcr',12,'view_aptcr'),(49,'Can add apven',13,'add_apven'),(50,'Can change apven',13,'change_apven'),(51,'Can delete apven',13,'delete_apven'),(52,'Can view apven',13,'view_apven'),(53,'Can add projects',14,'add_projects'),(54,'Can change projects',14,'change_projects'),(55,'Can delete projects',14,'delete_projects'),(56,'Can view projects',14,'view_projects'),(57,'Can add remita auth',15,'add_remitaauth'),(58,'Can change remita auth',15,'change_remitaauth'),(59,'Can delete remita auth',15,'delete_remitaauth'),(60,'Can view remita auth',15,'view_remitaauth'),(61,'Can add source bank details',16,'add_sourcebankdetails'),(62,'Can change source bank details',16,'change_sourcebankdetails'),(63,'Can delete source bank details',16,'delete_sourcebankdetails'),(64,'Can view source bank details',16,'view_sourcebankdetails');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_webapp_users_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_webapp_users_id` FOREIGN KEY (`user_id`) REFERENCES `webapp_users` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2025-10-13 10:47:57.527558','2','Chanda',1,'[{\"added\": {}}]',10,1),(2,'2025-10-13 10:48:05.696122','2','Chanda',2,'[{\"changed\": {\"fields\": [\"Is active\"]}}]',10,1),(3,'2025-10-13 13:38:08.115563','3','Chongo',1,'[{\"added\": {}}]',10,1),(4,'2025-10-13 13:38:13.911250','3','Chongo',2,'[{\"changed\": {\"fields\": [\"Is active\"]}}]',10,1),(5,'2025-10-13 13:48:34.392509','1','BankDetails object (1)',1,'[{\"added\": {}}]',7,1),(6,'2025-10-13 14:01:19.771304','1','BankDetails object (1)',2,'[{\"changed\": {\"fields\": [\"Vendor ID\"]}}]',7,1),(7,'2025-10-13 14:04:33.033471','1','BankDetails object (1)',2,'[{\"changed\": {\"fields\": [\"Vendor ID\"]}}]',7,1),(8,'2025-10-13 14:07:16.566692','1','BankDetails object (1)',2,'[{\"changed\": {\"fields\": [\"Vendor ID\"]}}]',7,1),(9,'2025-10-15 08:22:02.581342','1','IHVN Accumulated Fund Financial Database',1,'[{\"added\": {}}]',14,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(5,'sessions','session'),(6,'webapp','apicallerrors'),(11,'webapp','appym'),(12,'webapp','aptcr'),(13,'webapp','apven'),(7,'webapp','bankdetails'),(8,'webapp','processeddeposits'),(14,'webapp','projects'),(15,'webapp','remitaauth'),(16,'webapp','sourcebankdetails'),(9,'webapp','userloginhistory'),(10,'webapp','users');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-10-13 10:39:31.477315'),(2,'contenttypes','0002_remove_content_type_name','2025-10-13 10:39:31.616867'),(3,'auth','0001_initial','2025-10-13 10:39:32.164286'),(4,'auth','0002_alter_permission_name_max_length','2025-10-13 10:39:32.288679'),(5,'auth','0003_alter_user_email_max_length','2025-10-13 10:39:32.296716'),(6,'auth','0004_alter_user_username_opts','2025-10-13 10:39:32.305261'),(7,'auth','0005_alter_user_last_login_null','2025-10-13 10:39:32.313371'),(8,'auth','0006_require_contenttypes_0002','2025-10-13 10:39:32.321751'),(9,'auth','0007_alter_validators_add_error_messages','2025-10-13 10:39:32.329505'),(10,'auth','0008_alter_user_username_max_length','2025-10-13 10:39:32.340230'),(11,'auth','0009_alter_user_last_name_max_length','2025-10-13 10:39:32.351049'),(12,'auth','0010_alter_group_name_max_length','2025-10-13 10:39:32.374131'),(13,'auth','0011_update_proxy_permissions','2025-10-13 10:39:32.384007'),(14,'auth','0012_alter_user_first_name_max_length','2025-10-13 10:39:32.392241'),(15,'webapp','0001_initial','2025-10-13 10:39:33.171357'),(16,'admin','0001_initial','2025-10-13 10:39:33.428384'),(17,'admin','0002_logentry_remove_auto_add','2025-10-13 10:39:33.438374'),(18,'admin','0003_logentry_add_action_flag_choices','2025-10-13 10:39:33.449237'),(19,'sessions','0001_initial','2025-10-13 10:39:33.511513'),(20,'webapp','0002_alter_users_password','2025-10-13 10:39:33.523082'),(21,'webapp','0003_appym_aptcr_apven_alter_bankdetails_account_no','2025-10-13 10:39:33.629078'),(22,'webapp','0004_remove_users_cif','2025-10-13 10:47:10.286441'),(23,'webapp','0005_remove_bankdetails_biccode_remove_bankdetails_branch_and_more','2025-10-13 13:35:25.021993'),(24,'webapp','0006_projects','2025-10-15 08:11:46.594166'),(25,'webapp','0007_bankdetails_project_processeddeposits_project','2025-10-15 08:36:44.000891'),(26,'webapp','0008_processeddeposits_batch_identifier','2025-10-15 08:41:16.998431'),(27,'webapp','0009_remove_processeddeposits_transaction_type','2025-10-15 09:11:52.703836'),(28,'webapp','0010_remitaauth','2025-10-15 13:23:12.939049'),(29,'webapp','0011_alter_processeddeposits_invoice_project_unique','2026-03-31 05:22:16.367510'),(30,'webapp','0012_users_email','2026-03-31 05:22:16.412472'),(31,'webapp','0013_processeddeposits_transaction_ref','2026-03-31 05:22:16.425915'),(32,'webapp','0014_sourcebankdetails','2026-03-31 05:22:16.540806'),(33,'webapp','0015_sourcebankdetails_bank_account_name','2026-03-31 05:22:16.557015'),(34,'webapp','0016_alter_users_is_active','2026-03-31 06:07:32.254899');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('0ik1rd1tl1ri9k7i62jwa7ltkqtvy3q3','.eJxVi0sOwjAMRO_iNYrc_MuSI3CByE4cBYGgIq1YIO4OFV3AbubNvCckWuaWli73dCqwBwe7X8aUz3Jdh4cwTZPaQFfr5_At6ni7yJb_9Ua9fVxvA9c8FIN-0LkQWXQBdSauxGbkglUiuVgxGgpSs-hRi0frovPFB3i9AXy8N5I:1w7XDz:j2-lf6D7d04HkR_dTA8z5rmUuPgmwBcAlElSTcwVmzY','2026-04-14 11:25:35.486494'),('9k6vdahzrzzv42c0asgep8g0spewomck','.eJxVizsOwjAQRO_iGln-75qSI3ABa2OvZQSCCCeiQNw9iUgB3cybeW-RaJ5amjs_06WIo9Di8MsGyle-b8OLBxpHuYMut8_pW-T5ceM9_-uNelvdYJUhoyGgd1xrQHCVosZis6davWL0FosLDKQAtVfZGAdgKQaKzorPAkCXNf4:1v8JCg:vtzOjUkOuYPfHQ1aFbdDrPiNVn41JSRUbZKHo35MGZQ','2025-10-27 14:07:10.953687'),('eeadn7uz127b5l9bxqmy564q9tyo1zun','.eJxVizsOwjAQRO_iGln-fyg5Ahewdpe1jEAQ4UQUiLsTixTQzbx58xIFlrmVpfOjnE9iL4zY_TIEuvBtDE9GmCa5gS6Hc_gWebxfecv_9wa9rd9sWUVtONpAPlQKymmtfURtXFUuVIiVmFIiv0oOM2VKYzJgLWQU7w9Czzap:1v8JDD:wywTwZ8ddtRysOM-7skDE8xgZhcWfjRnWW5m_akxYqI','2025-10-27 14:07:43.861251'),('qfr1k6ev33xr0a2bf9xfgyv7xszqeifk','.eJxVjU0OwiAQhe_C2jSUgYG69AhegAzwDEajjbRxYby7bexCd-_vy3upKPNU49zwiOei9orU7jdLki-4rcUTScax24LWrZvD13TH-xWb_sertLqwmQYW57i3IdhUSnLw3ujMKfjcE0qRQfvAhrSGodNyQi5YJnAGCOr9AVV7Nw8:1vB6vW:TotXim1y3Hqx86b3QWOb-qcMOENcaC3EP_SardP9ycM','2025-11-04 07:37:02.567019'),('t065lp3eirwb2exmtbse69rjetsdephn','.eJxVi0EOwjAMBP-SM4riNHEQR57AByLbiRUEgoq04oD4O63oAW67Ozsvk2meWp57feRzMQczmN3vxiSXelvBszKNo92GbtfP8Vvs6X6tW_7XG_W2uKKgEUGAXZBAmIqPLjlHvgTYD6KB0YVaFUUSw0KBPUckIdXo0bw_ZVk3cw:1vBCl8:QtwJdYZBzJYDzuOGX330ZYMalAKl04a6yYjEdFucHow','2025-11-04 13:50:42.080161'),('tlglg6z63xvoub0e4gsrkyb1zet35qwu','.eJxVi0EOwjAMBP-SM4riNHEQR57AByLbiRUEgoq04oD4O63oAW67Ozsvk2meWp57feRzMQczmN3vxiSXelvBszKNo92GbtfP8Vvs6X6tW_7XG_W2uKKgEUGAXZBAmIqPLjlHvgTYD6KB0YVaFUUSw0KBPUckIdXo0bw_ZVk3cw:1vBCR9:VGQT32K4Xgo9M_VxYQTbN4zHFP22u3ngzW8LWsmnnqM','2025-11-04 13:30:03.948024'),('woxowzu3zok2d1y0l6m0sfs8eah3d9v1','.eJxVi0EOwjAMBP-SM4riNHEQR57AByLbiRUEgoq04oD4O63oAW67Ozsvk2meWp57feRzMQczmN3vxiSXelvBszKNo92GbtfP8Vvs6X6tW_7XG_W2uKKgEUGAXZBAmIqPLjlHvgTYD6KB0YVaFUUSw0KBPUckIdXo0bw_ZVk3cw:1vBCRy:oym-GyDNkdKY5N8COtR_VBPgLPpz85stclk_uqJ74sA','2025-11-04 13:30:54.923682');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_apicallerrors`
--

DROP TABLE IF EXISTS `webapp_apicallerrors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_apicallerrors` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service` varchar(255) NOT NULL,
  `error_list` longtext NOT NULL,
  `transaction_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_apicallerrors`
--

LOCK TABLES `webapp_apicallerrors` WRITE;
/*!40000 ALTER TABLE `webapp_apicallerrors` DISABLE KEYS */;
/*!40000 ALTER TABLE `webapp_apicallerrors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_bankdetails`
--

DROP TABLE IF EXISTS `webapp_bankdetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_bankdetails` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `account_no` varchar(20) NOT NULL,
  `account_name` varchar(255) NOT NULL,
  `vendor_id` varchar(255) NOT NULL,
  `vendor_mobile_number` varchar(20) NOT NULL,
  `vendor_email` varchar(255) NOT NULL,
  `bank_name` varchar(255) NOT NULL,
  `bank_code` varchar(255) NOT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `webapp_bankdetails_project_id_d0c0b2a8_fk_webapp_projects_id` (`project_id`),
  CONSTRAINT `webapp_bankdetails_project_id_d0c0b2a8_fk_webapp_projects_id` FOREIGN KEY (`project_id`) REFERENCES `webapp_projects` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_bankdetails`
--

LOCK TABLES `webapp_bankdetails` WRITE;
/*!40000 ALTER TABLE `webapp_bankdetails` DISABLE KEYS */;
INSERT INTO `webapp_bankdetails` VALUES (5,'05869573987','Lubasi Nyirenda','19','+260987631244','lubasi@ihvn.co.zm','Citibank','023',1),(6,'9807678956','CHANDA MWANGO','','+26098763123','chanda@gmail.com','Polaris Bank Ltd','076',1),(7,'05869578744','Liseli Mwanda','','+2340987654561','liseli@ihvn.co.zm','United Bank of Africa','033',1),(8,'098766523','Mabvuto Banda','','+2340976856435','mabvuto@ihvn.co.zm','Access Bank Nigeria Plc','044',1),(9,'0586957398','Paul Reed','','','','GTBank','058',1);
/*!40000 ALTER TABLE `webapp_bankdetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_processeddeposits`
--

DROP TABLE IF EXISTS `webapp_processeddeposits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_processeddeposits` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `invoiceid` varchar(255) NOT NULL,
  `vendorid` varchar(255) NOT NULL,
  `vendorname` varchar(255) NOT NULL,
  `transaction_date` varchar(255) NOT NULL,
  `amount` varchar(255) NOT NULL,
  `status` int NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `processed_by` varchar(255) NOT NULL,
  `project_id` bigint NOT NULL,
  `batch_identifier` varchar(255) NOT NULL,
  `transaction_ref` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `webapp_processeddeposits_project_id_invoiceid_4ac36e84_uniq` (`project_id`,`invoiceid`),
  KEY `webapp_processeddepo_project_id_ed9cf950_fk_webapp_pr` (`project_id`),
  CONSTRAINT `webapp_processeddepo_project_id_ed9cf950_fk_webapp_pr` FOREIGN KEY (`project_id`) REFERENCES `webapp_projects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_processeddeposits`
--

LOCK TABLES `webapp_processeddeposits` WRITE;
/*!40000 ALTER TABLE `webapp_processeddeposits` DISABLE KEYS */;
/*!40000 ALTER TABLE `webapp_processeddeposits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_projects`
--

DROP TABLE IF EXISTS `webapp_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_projects` (
  `id` bigint NOT NULL,
  `project_name` text,
  `project_code` text,
  `is_active` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_projects`
--

LOCK TABLES `webapp_projects` WRITE;
/*!40000 ALTER TABLE `webapp_projects` DISABLE KEYS */;
INSERT INTO `webapp_projects` VALUES (1,'IHVN Accumulated Fund Financial Database','ACCDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(2,'Action Grant Financial Database','ACTDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(3,'IHV Adapt Grant Financial Database','ADADAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(4,'Accelerating Nutritional Results In Nigeria (Anrin) Project','ANRDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(5,'Africa Postdoctoral Training Initiative (APTI) Fellowship','APTDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(6,'ASPIRE Project Financial Database','ASPDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(7,'Beaming Grant Financial Database','BEADAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(8,'IHVN/BEGET Project Financial Database','BEGDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(9,'HIV Vista Project (BRILLIANT Consortium) Financial Database','BRIDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(10,'Building Fund Financial Database','BUFDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(11,'Building Trust Grant Financial Database','BUTDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(12,'CAMP Study Project Financial Database','CAMDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(13,'Case Inspire Grant Financial Database','CASDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(14,'Cipher Research Grant Financial Database','CIPDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(15,'IHVN/Clear Grant Financial Database','CLEDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(16,'D2EFT Study Grant Financial Database','D2EDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(17,'IHVN/Gesundes emergency food aid grants financial Database','EFADAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(18,'ENHANCE Project Financial Database','ENHDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(19,'EQUAL Project Financial Database','EQUDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(20,'EXCEL Rite  Project Financial Database','EXCDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(21,'EXPAND Project Financial Database','EXPDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(22,'EDCTP Fellowship Financial Database','FELDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(23,'Global Fund GC7 Project Financial Database','GC7DAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(24,'NIH/IHVN GDRS  Ghana Project Financial Database','GDRSDA',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(25,'Gesundes Afrika Project Financial database','GESDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(26,'IHVN/Gesunde Food Security Financial Database','GFSDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(27,'Global Fund TB Sub-Recipients Financial Database','GFTBSR',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(28,'Global Fund/CCM/TB Grant Financial Database','GFTDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(29,'NIH/H3A/I-HAB Grant Financial Database','H3ADAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(30,'Global Fund TB Sub-Recipients Financial Database.','HAFDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(31,'Hepatitis B Project Financial Database','HEPDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(32,'Hominy Project Financial Database','HOMDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(33,'IEV Grant Financial Database','IEVDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(34,'IHVN Guest House','IGHDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(35,'IHVN InterGrant Transactions Database','IHVGDA',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(36,'IHVN Payroll Database','IHVPAD',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(37,'Non UMB Grants Financial Database','IHVSDA',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(38,'Impact Malaria Financial Database','IMADAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(39,'IMPACT Project Financial Database','IMPDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(40,'IMPACT UMB Project Financial Database.','IMUDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(41,'INFORM Africa Project Financial Database','INFDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(42,'IHVN International Research Center of Excellence','IRCDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(43,'IRCE Secure Financial Database','ISEDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(44,'INSIGHT013 ITAC (The study)','ITADAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(45,'USAID/Nigeria Tuberculosis Local Organizations Network','LONDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(46,'HIV-ST-Evaluation Project (LSTM) Financial Database','LSTDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(47,'IHVN/ Ondo State Malaria Impact project Financial Database','MALDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(48,'Novateur Developement Business Services','NDBSDA',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(49,'NORA Project Financial Database','NORDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(50,'Outcome Study Financial Database','OUTDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(51,'IHVN PAVIA Grant Financial Database','PAVDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(52,'Pediatrics Project Financial Database','PEDDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(53,'NIH/UMB/Plasvirec Grant Financial Database','PLADAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(54,'IHVN Recoup Database','RECDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(55,'Resolve To Save Lives Grant Finacial Database','RSLDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(56,'Safe/Thrive Project Financial Database','SAFDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(57,'Scenario Study Financial Database','SCEDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(58,'Strengthng Global Health Security Agenda In Nig(Secure- Nig)','SGHDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(59,'SPEED (Vital Strategies) Project Financial Database','SPEDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(60,'UNSW/TKI/Start Study Grant Financial Database','STADAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(61,'Syndemic Project Financial Database','SYNDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(62,'TICO Project Financial Database','TICDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(63,'IHVN TIFA Grant Financial Database','TIFDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(64,'EDCTP - TRiAD Study Financial Database','TRIDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(65,'VERDI Mpox Project','VERDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(66,'IHVN Wanetam EDCTP Grant Financial Database.','WANDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00'),(67,'HIV & HCV Clinical Validation Study Financial Database','WONDAT',1,'2022-02-06 00:00:00','2022-02-06 00:00:00');
/*!40000 ALTER TABLE `webapp_projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_remitaauth`
--

DROP TABLE IF EXISTS `webapp_remitaauth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_remitaauth` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` longtext,
  `expires_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_remitaauth`
--

LOCK TABLES `webapp_remitaauth` WRITE;
/*!40000 ALTER TABLE `webapp_remitaauth` DISABLE KEYS */;
INSERT INTO `webapp_remitaauth` VALUES (1,'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJjNmpqdFpSeEtlQkcyemEyMmU2NFF2N0pIZDBSc2FPT2g5M1Q1Zmh2UWpFIn0.eyJleHAiOjE3NzQ5NTk5MzYsImlhdCI6MTc3NDk1NjMzNiwianRpIjoiZTk1Mjg5MWQtY2RmZi00OTMxLWE4YmYtMDFlYzczNmRjOWNkIiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMTAuODI6OTE4MC9rZXljbG9hay9yZW1pdGEvZXhhcHAvYXBpL3YxL3JlZGdhdGUvYXV0aC9yZWFsbXMvcmVtaXRhIiwiYXVkIjpbImRpc2NvdmVyeS1zZXJ2ZXIiLCJhY2NvdW50Il0sInN1YiI6IjY5MzAzM2M4LWU2YmQtNDBkMC04M2RmLWQ1MzgwNDM4Njk0NyIsInR5cCI6IkJlYXJlciIsImF6cCI6InJlbWl0YXVhYS1zZXJ2aWNlIiwic2Vzc2lvbl9zdGF0ZSI6IjdjNzg2ZDFhLTg1ZTUtNDY3Zi1iMTBiLWJlMGU0OTE2ZTc3NyIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9sb2dpbi5yZW1pdGEubmV0Il0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiZGlzY292ZXJ5LXNlcnZlciI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsInZpZXctcHJvZmlsZSJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiIwMTEgMDExIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYzltZWw0bm16bTdjbm01bSIsImdpdmVuX25hbWUiOiIwMTEiLCJmYW1pbHlfbmFtZSI6IjAxMSIsIm9yZ2FuaXNhdGlvbi1pZCI6IkNXR0RFTU8iLCJlbWFpbCI6IjAxMSJ9.Mhk0ysJ9NrsGYa9yQEaJKLdFT3c3d_Pi2suqdFiOtoHcattcUHmBaN9P1yglyTdvIVeOWbmg0YYxm3qUFutS9_MhqCzQCa-9Z8C92-lFFcVO45byI_PWxZRx1bd96ZxeoNliMHCAnFZG6Wwjs6ykTpq2dTcL56WM3JEYgaUA8ceT_ey-BQNoV996yH8KUOrqHsx_SGYUUYX0Pdf2BqRiIN7dW3zdPVISNSPvxDla-YQvoof6vhtpdveS4ImIMBBC7IL_PJOoTHQObGDiQ1uMyNuS9FraWd-WmvQ07smUwDiSqRAiOTbdGtgmuHbY4uIusV1TCyqGuD-Wp2CwfFY5YA','2026-03-31 12:25:35.466415','2025-10-15 13:25:29.247182','2026-03-31 11:25:35.467459');
/*!40000 ALTER TABLE `webapp_remitaauth` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_sourcebankdetails`
--

DROP TABLE IF EXISTS `webapp_sourcebankdetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_sourcebankdetails` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bank_name` varchar(255) NOT NULL,
  `bank_code` varchar(255) NOT NULL,
  `bank_account_number` varchar(255) NOT NULL,
  `project_id` bigint NOT NULL,
  `bank_account_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `webapp_sourcebankdet_project_id_44923fb3_fk_webapp_pr` (`project_id`),
  CONSTRAINT `webapp_sourcebankdet_project_id_44923fb3_fk_webapp_pr` FOREIGN KEY (`project_id`) REFERENCES `webapp_projects` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_sourcebankdetails`
--

LOCK TABLES `webapp_sourcebankdetails` WRITE;
/*!40000 ALTER TABLE `webapp_sourcebankdetails` DISABLE KEYS */;
INSERT INTO `webapp_sourcebankdetails` VALUES (1,'UBA','007','05869573988',1,'Chifula Nambela');
/*!40000 ALTER TABLE `webapp_sourcebankdetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_userloginhistory`
--

DROP TABLE IF EXISTS `webapp_userloginhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_userloginhistory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `ipaddress` varchar(255) NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_userloginhistory`
--

LOCK TABLES `webapp_userloginhistory` WRITE;
/*!40000 ALTER TABLE `webapp_userloginhistory` DISABLE KEYS */;
/*!40000 ALTER TABLE `webapp_userloginhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_users`
--

DROP TABLE IF EXISTS `webapp_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_admin` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_users`
--

LOCK TABLES `webapp_users` WRITE;
/*!40000 ALTER TABLE `webapp_users` DISABLE KEYS */;
INSERT INTO `webapp_users` VALUES (1,'hp','pbkdf2_sha256$720000$ONHFz8fDRBL1N4p3YOunXK$R1ixVi0NUJZCZID7HmuXdzrhT/ZN8L72gGgCuXun90s=','',1,1,1,1,'2025-10-15 08:20:25.740860',NULL),(2,'Chanda','pbkdf2_sha256$1000000$ZGP5JT9U2k84g478tCQiQG$o8zSnHLqPGat6RokuUl8S3yEALKbQ2RnJwrQgoIOGWA=','002',1,0,0,0,'2025-10-15 14:43:25.955453',NULL),(3,'Chongo','pbkdf2_sha256$390000$kYm4mw9DGmLsnR1snLKOnR$C71dKP/JpKLE6amIC09t1Z0SlOXH0jXmXOaA8pY3yYY=','001',1,0,0,0,'2025-10-21 13:50:42.064055',NULL),(4,'Chifula','pbkdf2_sha256$870000$ufpBaUJrvBmsVFH7LI9j87$iezyeTnh1Dug2y2ufCbcD+JRl8DAAMZ6WmyIcB1E/gM=','001',1,1,1,1,'2026-03-31 09:52:28.155146','chichinambela2@gmail.com'),(5,'Chongoo','pbkdf2_sha256$870000$saWIt9RCmDTOnyIXHpRBJ1$bUVG/2/YR4432RRMDL9bHYn7YA8/it4Ch5L0RMsmb/Y=','002',1,0,0,0,'2026-03-31 11:25:35.483306','chifulanambela@gmail.com');
/*!40000 ALTER TABLE `webapp_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_users_groups`
--

DROP TABLE IF EXISTS `webapp_users_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_users_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `users_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `webapp_users_groups_users_id_group_id_d336ce01_uniq` (`users_id`,`group_id`),
  KEY `webapp_users_groups_group_id_258e0704_fk_auth_group_id` (`group_id`),
  CONSTRAINT `webapp_users_groups_group_id_258e0704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `webapp_users_groups_users_id_37f574de_fk_webapp_users_id` FOREIGN KEY (`users_id`) REFERENCES `webapp_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_users_groups`
--

LOCK TABLES `webapp_users_groups` WRITE;
/*!40000 ALTER TABLE `webapp_users_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `webapp_users_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webapp_users_user_permissions`
--

DROP TABLE IF EXISTS `webapp_users_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webapp_users_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `users_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `webapp_users_user_permis_users_id_permission_id_8533f94d_uniq` (`users_id`,`permission_id`),
  KEY `webapp_users_user_pe_permission_id_52772504_fk_auth_perm` (`permission_id`),
  CONSTRAINT `webapp_users_user_pe_permission_id_52772504_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `webapp_users_user_pe_users_id_2f3ffa1b_fk_webapp_us` FOREIGN KEY (`users_id`) REFERENCES `webapp_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webapp_users_user_permissions`
--

LOCK TABLES `webapp_users_user_permissions` WRITE;
/*!40000 ALTER TABLE `webapp_users_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `webapp_users_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-31 14:59:34
