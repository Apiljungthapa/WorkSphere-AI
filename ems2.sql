-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 29, 2025 at 08:02 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ems2`
--

-- --------------------------------------------------------

--
-- Table structure for table `announcement`
--

CREATE TABLE `announcement` (
  `announcement_id` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `date` date NOT NULL,
  `content` text NOT NULL,
  `priority_level` enum('High','Medium','Low') NOT NULL,
  `manager_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `chatroom`
--

CREATE TABLE `chatroom` (
  `chat_id` varchar(50) NOT NULL,
  `created_date` datetime NOT NULL,
  `emp1_id` varchar(50) DEFAULT NULL,
  `emp2_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chatroom`
--

INSERT INTO `chatroom` (`chat_id`, `created_date`, `emp1_id`, `emp2_id`) VALUES
('CHT15460089', '2025-01-29 17:33:47', 'EMP005', 'MGR001'),
('CHT29015803', '2025-01-27 11:53:40', 'EMP003', 'EMP003'),
('CHT71498751', '2025-01-27 14:22:49', 'EMP003', 'EMP004'),
('CHT72130153', '2025-01-27 10:38:40', 'EMP005', 'EMP004'),
('CHT77015626', '2025-01-27 10:48:08', 'EMP005', 'EMP006'),
('CHT85527827', '2025-01-27 10:37:39', 'EMP005', 'EMP003');

-- --------------------------------------------------------

--
-- Table structure for table `comment`
--

CREATE TABLE `comment` (
  `comment_id` varchar(50) NOT NULL,
  `content` text NOT NULL,
  `comment_date` datetime NOT NULL,
  `post_id` varchar(50) DEFAULT NULL,
  `user_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `comment`
--

INSERT INTO `comment` (`comment_id`, `content`, `comment_date`, `post_id`, `user_id`) VALUES
('cmnt11761', 'thik xa hola kre', '2025-01-29 05:30:22', 'PST13155', 'EMP005'),
('cmnt12287', 'gh', '2025-01-25 17:42:07', 'PST13155', 'EMP005'),
('cmnt17101', 'xa', '2025-01-25 17:28:54', 'PST13155', 'EMP005'),
('cmnt17600', 'hey', '2025-01-25 17:41:07', 'PST13155', 'EMP005'),
('cmnt20176', 'aur', '2025-01-30 00:08:03', 'PST13890', 'EMP005'),
('cmnt20589', 'bbbss', '2025-01-29 11:25:42', 'PST13155', 'EMP005'),
('cmnt27081', 'b', '2025-01-25 17:44:14', 'PST13890', 'EMP005'),
('cmnt28036', 'b', '2025-01-25 18:17:21', 'PST13155', 'EMP005'),
('cmnt28296', 'k xa', '2025-01-25 18:09:57', 'PST33828', 'EMP005'),
('cmnt49021', 'b', '2025-01-25 18:48:38', 'PST33828', 'EMP005'),
('cmnt69842', 'k xa mero bhai sanchai xas ni ta hola', '2025-01-29 05:28:20', 'PST13890', 'EMP005'),
('cmnt88610', 'no', '2025-01-25 18:09:38', 'PST13890', 'EMP005');

-- --------------------------------------------------------

--
-- Table structure for table `likes`
--

CREATE TABLE `likes` (
  `like_id` varchar(50) NOT NULL,
  `post_id` varchar(50) DEFAULT NULL,
  `user_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `likes`
--

INSERT INTO `likes` (`like_id`, `post_id`, `user_id`) VALUES
('LKE3801', 'PST11090', 'EMP005'),
('LKE9637', 'PST13155', 'EMP004'),
('LKE5798', 'PST13155', 'EMP005'),
('LKE3321', 'PST13890', 'EMP005'),
('LKE3550', 'PST15646', 'EMP005'),
('LKE7146', 'PST22148', 'EMP005'),
('LKE3025', 'PST25832', 'EMP005'),
('LKE9855', 'PST30140', 'EMP005'),
('LKE1048', 'PST33418', 'EMP005'),
('LKE5056', 'PST33828', 'EMP005'),
('LKE5306', 'PST61020', 'EMP004'),
('LKE3511', 'PST61020', 'EMP005'),
('LKE2818', 'PST73320', 'EMP005'),
('LKE9108', 'PST96225', 'EMP005');

-- --------------------------------------------------------

--
-- Table structure for table `message`
--

CREATE TABLE `message` (
  `msg_id` varchar(50) NOT NULL,
  `content` text NOT NULL,
  `timestamp` datetime NOT NULL,
  `chat_id` varchar(50) DEFAULT NULL,
  `sender_id` varchar(50) DEFAULT NULL,
  `receiver_id` varchar(50) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `status` varchar(30) DEFAULT 'unread'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `message`
--

INSERT INTO `message` (`msg_id`, `content`, `timestamp`, `chat_id`, `sender_id`, `receiver_id`, `is_read`, `status`) VALUES
('MSG0045', 'fg', '2025-01-29 23:58:24', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG0083', 'saf', '2025-01-29 23:57:23', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG0440', 'new', '2025-01-29 23:55:08', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG0597', 'dfh', '2025-01-29 23:58:09', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG0726', 'ki dil judna paye wapas', '2025-01-30 00:04:01', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG1096', 'sfd', '2025-01-29 23:56:47', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG1136', 'fhd', '2025-01-29 23:58:03', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG1538', 'sgh', '2025-01-29 23:58:36', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG1633', 'hunxa', '2025-01-30 00:04:16', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG1742', 'fw', '2025-01-29 23:56:10', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG1779', 'gfds', '2025-01-29 23:55:13', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG2327', 'gf', '2025-01-29 23:58:21', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG2379', 'dgf', '2025-01-29 23:57:39', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG2566', 'illawa', '2025-01-30 00:03:37', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG2845', 'new', '2025-01-29 23:56:03', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG3188', 'wfe', '2025-01-29 23:56:24', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG4396', 'nakaro', '2025-01-30 00:03:51', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG4533', 'we', '2025-01-29 23:56:35', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG5556', 'sda', '2025-01-29 23:47:19', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG5625', 'aisa', '2025-01-30 00:03:45', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG5702', 'uyterw', '2025-01-29 23:57:56', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG5907', 'as', '2025-01-29 23:47:04', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG5912', 'fh', '2025-01-29 23:58:27', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG6465', 'apil', '2025-01-29 23:45:44', 'CHT85527827', 'EMP005', 'EMP003', 0, 'sent'),
('MSG6529', 'dsfg', '2025-01-29 23:58:40', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG6827', 'rn', '2025-01-29 23:56:52', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG7038', 'ok x ata', '2025-01-30 00:04:12', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG7073', 'new', '2025-01-29 23:45:49', 'CHT85527827', 'EMP003', 'EMP005', 0, 'sent'),
('MSG7524', 'dfgs', '2025-01-29 23:48:31', 'CHT85527827', 'EMP005', 'EMP003', 0, 'sent'),
('MSG7930', 'dsgfg', '2025-01-29 23:57:45', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG7980', 'sdf', '2025-01-29 23:56:39', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG8020', 'dsgf', '2025-01-29 23:48:34', 'CHT85527827', 'EMP003', 'EMP005', 0, 'sent'),
('MSG8144', 'sa', '2025-01-29 23:47:36', 'CHT85527827', 'EMP005', 'EMP003', 0, 'sent'),
('MSG8426', 'fd', '2025-01-29 23:55:24', 'CHT85527827', 'EMP003', 'EMP005', 0, 'read'),
('MSG8442', 'husn', '2025-01-30 00:03:32', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read'),
('MSG9907', 'df', '2025-01-29 23:55:21', 'CHT85527827', 'EMP005', 'EMP003', 0, 'read');

-- --------------------------------------------------------

--
-- Table structure for table `post`
--

CREATE TABLE `post` (
  `post_id` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `likes` int(11) DEFAULT 0,
  `created_date` datetime NOT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `deleted_at` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `post`
--

INSERT INTO `post` (`post_id`, `title`, `content`, `likes`, `created_date`, `user_id`, `deleted_at`) VALUES
('PST11089', 'LearnHtml', 'g', 0, '2025-01-19 00:47:35', 'EMP005', 1),
('PST11090', 'shishir', 'shishir mama', 1, '2025-01-25 14:03:59', 'EMP005', 1),
('PST13155', 'nsa', 'dsa', 2, '2025-01-25 15:50:49', 'EMP005', 1),
('PST13890', 'apilhoraa', 'puche', 1, '2025-01-25 15:51:27', 'EMP005', 0),
('PST15646', 'xzn', 'new', 1, '2025-01-25 13:38:10', 'EMP005', 1),
('PST19425', 'hi', 'szxrdcfgvhb', 0, '2025-01-19 00:47:22', 'EMP005', 1),
('PST22148', 'naya nepal', 'mero desh nepal', 1, '2025-01-29 11:22:49', 'EMP005', 0),
('PST25832', 'ML and AI', 'this is machine learniong and deep learning ai', 1, '2025-01-25 15:29:37', 'EMP005', 1),
('PST27733', 'sa', 'dsa and ml', 0, '2025-01-18 23:12:04', 'EMP005', 1),
('PST30140', 'bn', 'xcvbn', 1, '2025-01-25 14:28:01', 'EMP005', 1),
('PST33418', 'ram', 'ramkaka', 1, '2025-01-25 14:21:20', 'EMP005', 1),
('PST33828', 'shsor', 'hshjd', 1, '2025-01-25 16:28:22', 'EMP005', 0),
('PST45933', 'Machine Learning And Data Sceince', 'this is ml and ds cpurse', 0, '2025-01-18 23:06:37', 'EMP005', 1),
('PST61020', 'Lean jQUERY', 'hjadkjads', 3, '2025-01-18 23:12:24', 'EMP005', 1),
('PST73320', 'apil', 'apil', 1, '2025-01-25 14:02:15', 'EMP005', 1),
('PST84700', 'hi', 'f', 0, '2025-01-18 23:12:00', 'EMP005', 1),
('PST96225', 'new', 'nsd', 1, '2025-01-25 15:47:24', 'EMP005', 1);

-- --------------------------------------------------------

--
-- Table structure for table `support_feedback`
--

CREATE TABLE `support_feedback` (
  `feedback_id` varchar(50) NOT NULL,
  `feedback_type` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `support_feedback`
--

INSERT INTO `support_feedback` (`feedback_id`, `feedback_type`, `message`, `user_id`, `created_at`) VALUES
('FDB24203', 'appreciation', 'weel done', 'EMP005', '2025-01-26 06:36:34'),
('FDB28877', 'complaint', 'you are fired', 'EMP005', '2025-01-26 06:37:40'),
('FDB32577', 'appreciation', 'weel done', 'EMP005', '2025-01-26 06:35:05'),
('FDB42266', 'complaint', 'shishir', 'EMP005', '2025-01-26 12:45:58'),
('FDB69027', 'complaint', 'you are fired', 'EMP005', '2025-01-26 06:37:21'),
('FDB75038', 'appreciation', 'weel done', 'EMP005', '2025-01-26 06:37:11'),
('FDB75401', 'appreciation', 'weel done', 'EMP005', '2025-01-26 06:31:25'),
('FDB76525', 'complaint', 'you are fired', 'EMP005', '2025-01-26 06:37:35'),
('FDB79341', 'appreciation', 'weel done', 'EMP005', '2025-01-26 06:32:40'),
('FDB80527', 'complaint', 'zx', 'EMP005', '2025-01-26 12:47:34'),
('FDB87191', 'appreciation', 'weel done', 'EMP005', '2025-01-26 06:36:41'),
('FDB98067', 'complaint', 'shishir', 'EMP005', '2025-01-26 12:47:13');

-- --------------------------------------------------------

--
-- Table structure for table `task`
--

CREATE TABLE `task` (
  `task_id` varchar(255) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `due_date` datetime DEFAULT NULL,
  `docs_path` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `assigned_to_id` varchar(255) DEFAULT NULL,
  `assigned_by_id` varchar(255) DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `task`
--

INSERT INTO `task` (`task_id`, `title`, `description`, `due_date`, `docs_path`, `status`, `assigned_to_id`, `assigned_by_id`, `deleted_at`) VALUES
('TSK017', 'lesrn ds', 'xc', '2024-12-18 00:00:00', 'resources\\EMP005_jeevan_thapa\\train_using_pretrained_model_image_classifier.ipynb', 'Approved', 'EMP005', 'MGR001', '2024-12-13 13:15:04'),
('TSK063', 'miraj', 'sanjennaq', '2024-12-21 00:00:00', 'resources\\EMP005_jeevan_thapa\\Screenshot 2024-12-18 125508.png', 'submitted', 'EMP005', 'MGR001', '0000-00-00 00:00:00'),
('TSK081', 'gf', 'vcb', '2025-01-02 00:00:00', 'resources\\EMP005_jeevan_thapa\\th.jpg', 'Approved', 'EMP005', 'MGR001', '2024-12-13 13:18:36'),
('TSK198', 'aa', '', '2024-12-27 00:00:00', NULL, 'Approved', 'EMP005', 'MGR001', '2024-12-13 13:44:55'),
('TSK204', 'neural network from scratch', '', '2025-02-08 00:00:00', NULL, 'Pending', 'EMP005', 'MGR001', '2025-01-26 13:06:19'),
('TSK222', 'learn GenAi', 'apildon12dsf', '2024-12-21 00:00:00', 'resources\\EMP005_jeevan_thapa\\Facial-Emotion-Recognition-on-Vision  Transformer.pdf', 'Approved', 'EMP005', 'MGR001', '2024-12-13 13:19:43'),
('TSK289', 'ssaa', 'ghjk', '2024-12-20 00:00:00', 'resources\\EMP005_jeevan_thapa\\fine-tuning-image-model (1).ipynb', 'Approved', 'EMP005', 'MGR001', '2024-12-13 13:51:08'),
('TSK331', 'ezsxrdctfvghbjn', '', '2024-12-21 00:00:00', NULL, 'Approved', 'EMP005', 'MGR001', '2024-12-13 13:26:52'),
('TSK551', 'hi', 'vdfbjas', '2024-12-19 00:00:00', 'resources\\EMP005_jeevan_thapa\\fine-tuning-image-model (1).ipynb', 'Approved', 'EMP005', 'MGR001', NULL),
('TSK620', 'hey gpt scrap', 'vcbngfhj', '2024-12-18 00:00:00', 'resources\\EMP005_jeevan_thapa\\proposal updated_final2.docx', 'Approved', 'EMP005', 'MGR001', '2024-12-13 13:27:02'),
('TSK651', 'nn', '', '2024-12-26 00:00:00', NULL, 'Pending', 'EMP005', 'MGR001', NULL),
('TSK732', 'ezsxrdctfvghbjn', '', '2024-12-21 00:00:00', NULL, 'Approved', 'EMP005', 'MGR001', '2024-12-13 13:27:45'),
('TSK848', 'apil', '', '2024-12-21 00:00:00', NULL, 'Pending', 'EMP003', 'MGR001', NULL),
('TSK877', 'gfhjk', '', '2024-12-28 00:00:00', NULL, 'Approved', 'EMP004', 'MGR001', '2024-12-13 13:36:42'),
('TSK897', 'hey gpt scrap', '', '2024-12-18 00:00:00', NULL, 'Approved', 'EMP005', 'MGR001', '2024-12-13 13:31:01');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `user_id` varchar(255) NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` varchar(100) DEFAULT NULL,
  `department_name` varchar(100) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `otp_code` varchar(100) DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`user_id`, `full_name`, `email`, `phone`, `password`, `role`, `department_name`, `position`, `otp_code`, `is_deleted`) VALUES
('EMP003', 'shishir', 'shishircodeid07@gmail.com', '9863267573', 'apil', 'employee', 'Human Resources', 'hr head', '890066', 1),
('EMP004', 'miraj', 'mirajdeepbhandari30@gmail.com', '79821964293', '123', 'employee', 'Engineering', 'consultant', '553518', 1),
('EMP005', 'jeevan thapa', 'apilcode566@gmail.com', '42667986473', 'hey', 'employee', 'Engineering', 'head', '642809', 0),
('EMP006', 'Don thapa', 'shishir@gmail.com', '09867004146', 'new', 'employee', NULL, NULL, NULL, 0),
('MGR001', 'Apil thapa', 'apilthapa87@gmail.com', '79821964293', 'apil12', 'manager', NULL, NULL, '1234', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `announcement`
--
ALTER TABLE `announcement`
  ADD PRIMARY KEY (`announcement_id`),
  ADD KEY `manager_id` (`manager_id`);

--
-- Indexes for table `chatroom`
--
ALTER TABLE `chatroom`
  ADD PRIMARY KEY (`chat_id`),
  ADD KEY `emp1_id` (`emp1_id`),
  ADD KEY `emp2_id` (`emp2_id`);

--
-- Indexes for table `comment`
--
ALTER TABLE `comment`
  ADD PRIMARY KEY (`comment_id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `likes`
--
ALTER TABLE `likes`
  ADD PRIMARY KEY (`like_id`),
  ADD UNIQUE KEY `post_id` (`post_id`,`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `message`
--
ALTER TABLE `message`
  ADD PRIMARY KEY (`msg_id`),
  ADD KEY `chat_id` (`chat_id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Indexes for table `post`
--
ALTER TABLE `post`
  ADD PRIMARY KEY (`post_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `support_feedback`
--
ALTER TABLE `support_feedback`
  ADD PRIMARY KEY (`feedback_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `task`
--
ALTER TABLE `task`
  ADD PRIMARY KEY (`task_id`),
  ADD KEY `assigned_to_id` (`assigned_to_id`),
  ADD KEY `assigned_by_id` (`assigned_by_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user_id`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `announcement`
--
ALTER TABLE `announcement`
  ADD CONSTRAINT `announcement_ibfk_1` FOREIGN KEY (`manager_id`) REFERENCES `user` (`user_id`);

--
-- Constraints for table `chatroom`
--
ALTER TABLE `chatroom`
  ADD CONSTRAINT `chatroom_ibfk_1` FOREIGN KEY (`emp1_id`) REFERENCES `user` (`user_id`),
  ADD CONSTRAINT `chatroom_ibfk_2` FOREIGN KEY (`emp2_id`) REFERENCES `user` (`user_id`);

--
-- Constraints for table `comment`
--
ALTER TABLE `comment`
  ADD CONSTRAINT `comment_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `post` (`post_id`),
  ADD CONSTRAINT `comment_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`);

--
-- Constraints for table `likes`
--
ALTER TABLE `likes`
  ADD CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `post` (`post_id`),
  ADD CONSTRAINT `likes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`);

--
-- Constraints for table `message`
--
ALTER TABLE `message`
  ADD CONSTRAINT `message_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `chatroom` (`chat_id`),
  ADD CONSTRAINT `message_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `user` (`user_id`),
  ADD CONSTRAINT `message_ibfk_3` FOREIGN KEY (`receiver_id`) REFERENCES `user` (`user_id`);

--
-- Constraints for table `post`
--
ALTER TABLE `post`
  ADD CONSTRAINT `post_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`);

--
-- Constraints for table `support_feedback`
--
ALTER TABLE `support_feedback`
  ADD CONSTRAINT `support_feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`);

--
-- Constraints for table `task`
--
ALTER TABLE `task`
  ADD CONSTRAINT `task_ibfk_1` FOREIGN KEY (`assigned_to_id`) REFERENCES `user` (`user_id`),
  ADD CONSTRAINT `task_ibfk_2` FOREIGN KEY (`assigned_by_id`) REFERENCES `user` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
