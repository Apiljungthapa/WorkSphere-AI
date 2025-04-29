-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 29, 2025 at 07:35 AM
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

--
-- Dumping data for table `announcement`
--

INSERT INTO `announcement` (`announcement_id`, `title`, `date`, `content`, `priority_level`, `manager_id`) VALUES
('ANM216', 'Office Leave', '2025-04-09', 'Tomorrow, we have leave because of protest', 'Medium', 'MGR001'),
('ANM435', 'Office Leave', '2025-04-20', 'Tomorrow, will be leave due to political issues', 'Low', 'MGR001');

-- --------------------------------------------------------

--
-- Table structure for table `chatroom`
--

CREATE TABLE `chatroom` (
  `chat_id` varchar(50) NOT NULL,
  `created_date` datetime NOT NULL,
  `emp1_id` varchar(50) DEFAULT NULL,
  `emp2_id` varchar(50) DEFAULT NULL,
  `is_deleted` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chatroom`
--

INSERT INTO `chatroom` (`chat_id`, `created_date`, `emp1_id`, `emp2_id`, `is_deleted`) VALUES
('CHT12990721', '2025-04-06 15:23:55', 'EMP002', 'MGR001', '0'),
('CHT18257144', '2025-04-06 15:23:20', 'EMP002', 'EMP003', '0'),
('CHT73072395', '2025-04-07 19:03:02', 'EMP002', 'EMP001', '0');

-- --------------------------------------------------------

--
-- Table structure for table `chat_history`
--

CREATE TABLE `chat_history` (
  `id` int(11) NOT NULL,
  `user_id` varchar(255) NOT NULL,
  `user_query` text DEFAULT NULL,
  `response` text DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `filepath` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_history`
--

INSERT INTO `chat_history` (`id`, `user_id`, `user_query`, `response`, `timestamp`, `filepath`) VALUES
(39, 'EMP002', 'where is nepal located?', 'Nepal is a landlocked country nestled between China and India.', '2025-04-01 11:31:41', 'resources/EMP002_RoshniThapa\\Nepal.pdf'),
(40, 'EMP002', 'explain more about nepal', 'Nepal is a nation of contrasts - ancient and modern, traditional and progressive. Its breathtaking landscapes, rich cultural heritage, and resilient people make it unique. \n\nNepal faces several challenges, including:\n\n1. Political instability affecting development projects.\n2. Economic dependence on remittances.\n3. Environmental issues such as deforestation and climate change.\n4. Improving infrastructure, healthcare, and education.\n\nDespite these challenges, Nepal has immense potential for growth, particularly in:\n\n1. Tourism\n2. Hydropower\n3. Technology\n\nWith strategic policies and investments, Nepal can achieve sustainable development and prosperity. Nepal continues to navigate political and economic challenges, but it remains a land of opportunity and hope. \n\nRural regions in Nepal still struggle with inadequate healthcare services, while urban areas have better healthcare facilities.', '2025-04-01 11:40:49', 'resources/EMP002_RoshniThapa\\Nepal.pdf'),
(41, 'EMP002', 'explain about culture in nepal', 'Nepal is a mosaic of ethnicities, languages, and traditions. With over 120 ethnic groups and 123 languages spoken, Nepal boasts immense cultural diversity. The major aspects of Nepal\'s culture include:\n\n1. Religion: Hinduism and Buddhism are predominant, with numerous temples, stupas, and monasteries reflecting religious harmony.\n\n2. Festivals: Dashain, Tihar, Holi, Buddha Jayanti, and Indra Jatra are widely celebrated.\n\n3. Traditional Arts and Crafts: Nepali handicrafts, Thangka paintings, and metalwork are globally recognized.\n\n4. Cuisine: Dal Bhat (lentils and rice), momo (dumplings), and Newari dishes like yomari and chatamari are popular.', '2025-04-01 11:41:38', 'resources/EMP002_RoshniThapa\\Nepal.pdf'),
(42, 'EMP002', 'where is nepl located', 'Your question is outside the document\'s content.', '2025-04-01 11:47:34', 'resources/EMP002_RoshniThapa\\Nepal.pdf'),
(43, 'EMP002', 'what us this document about?', 'This document provides a glimpse into Nepal’s multifaceted identity, but the nation’s story is ever-evolving, shaped by its history, people, and aspirations for the future.\n\nThis document is about Nepal.', '2025-04-03 11:18:57', 'resources/EMP002_RoshniThapa\\SONY SHARMA_9745988911_DOTM_Appointment.pdf'),
(44, 'EMP002', 'which banks are mentioned in it?', 'Your question is outside the document\'s content.', '2025-04-03 11:19:47', 'resources/EMP002_RoshniThapa\\SONY SHARMA_9745988911_DOTM_Appointment.pdf'),
(45, 'EMP002', 'What is covergent thinking from this?', 'Convergent reasoning is a type of argument structure mentioned in the context as: \n\nConvergent reasoning \nTwo one-premise argument', '2025-04-03 11:21:58', 'resources/EMP002_RoshniThapa\\Analytical Skills Notes SMU.pdf'),
(46, 'EMP002', 'what are good argument?', 'A good argument has the following characteristics:\n\n- All of its basic premises to be true\n- Inferences made to be acceptable\n- Acceptable inference – if you were to assume for the sake of the argument that the premises are true, then it would guarantee the truth of the conclusion', '2025-04-03 11:22:51', 'resources/EMP002_RoshniThapa\\Analytical Skills Notes SMU.pdf'),
(47, 'EMP003', 'what is neural networks?', 'Neural networks are a subset of machine learning, modeled after the human brain, designed to recognize patterns and solve complex problems. They consist of interconnected layers of nodes (neurons) that process data and make predictions. \n\nKey Features: \n• Ability to learn from data.', '2025-04-04 20:06:36', 'resources/EMP003_Sagar Kshetri\\Neural Networks.pdf'),
(48, 'EMP001', 'what is nepal', '<coroutine object BaseChatModel.ainvoke at 0x0000021CBFB3D210>', '2025-04-07 16:34:00', 'resources/EMP001_Ayub bhatta\\Nepal.pdf'),
(49, 'EMP001', 'where is nepal located?', 'Nepal is a landlocked country nestled between China and India.', '2025-04-07 16:40:12', 'resources/EMP001_Ayub bhatta\\Nepal.pdf'),
(50, 'EMP001', 'where is nepal?', 'Nepal is nestled between China and India.', '2025-04-07 16:40:30', 'resources/EMP001_Ayub bhatta\\Nepal.pdf'),
(51, 'EMP002', 'hello', 'I don\'t have any answer for this query in the documents. Please upload different documents or ask another query.', '2025-04-08 17:43:11', 'resources/EMP002_RoshniThapa\\Apil_Thapa_CV.pdf'),
(52, 'EMP002', 'hello', 'I don\'t have any answer for this query in the documents. Please upload different documents or ask another query.', '2025-04-08 17:44:33', 'resources/EMP002_RoshniThapa\\Apil_Thapa_CV.pdf'),
(53, 'EMP002', 'what is my name?', 'I don\'t have any answer for this query in the documents. Please upload different documents or ask another query.', '2025-04-08 17:45:27', 'resources/EMP002_RoshniThapa\\Apil_Thapa_CV.pdf'),
(54, 'EMP002', 'what is biocheistry?', 'Biochemistry is fundamental to understanding biological functions at a molecular level. It involves two main processes: \n1. Catabolism: Breakdown of complex molecules into simpler ones, releasing energy (e.g., Glycolysis, Krebs Cycle, Electron Transport Chain).\n2. Anabolism: Synthesis of complex molecules from simpler ones, requiring energy (e.g., Protein synthesis, DNA replication, Lipid biosynthesis).\n\nKey terms in biochemistry include:\n- Enzymes: Biological catalysts\n- ATP: The primary energy carrier\n- pH: Measure of acidity or alkalinity\n- Hormones: Chemical messengers\n- Cofactors and Coenzymes: Required for enzyme activity\n- Homeostasis: Maintenance of a stable internal environment\n- Oxidation-Reduction Reactions: Electron transfer reactions\n\nBiochemistry has applications in medicine, agriculture, genetics, and biotechnology, making it an indispensable field of study.', '2025-04-08 17:46:03', 'resources/EMP002_RoshniThapa\\biochemistry_details.pdf'),
(55, 'EMP002', 'what is my name?', 'I don\'t have any answer for this query in the documents. Please upload different documents or ask another query.', '2025-04-08 17:46:28', 'resources/EMP002_RoshniThapa\\biochemistry_details.pdf'),
(56, 'EMP002', 'my name is apil ok', 'I don\'t have any answer for this query in the documents. Please upload different documents or ask another query.', '2025-04-08 17:46:43', 'resources/EMP002_RoshniThapa\\biochemistry_details.pdf'),
(57, 'EMP002', 'what is neural netwoeks?', 'Neural networks have several components:  an input layer that receives raw data (like images or text); hidden layers that perform computations to extract features and consist of neurons connected by weights; and an output layer that produces predictions or classifications.  Activation functions, such as Sigmoid, ReLU, and Tanh, add non-linearity to the network.  Transformer networks, based on self-attention mechanisms for handling sequential data, are the backbone of natural language processing (NLP) models like GPT.', '2025-04-09 17:40:15', 'resources/EMP002_RoshniThapa\\Neural Networks.pdf'),
(58, 'EMP002', 'what is neural netoweks?', 'Neural networks have several components:  an input layer that receives raw data (like images or text); hidden layers that perform computations to extract features and consist of neurons connected by weights; and an output layer that produces predictions or classifications.  Activation functions, such as Sigmoid, ReLU, and Tanh, add non-linearity to the network.  Transformer networks, based on self-attention mechanisms for handling sequential data, are the backbone of NLP models like GPT.', '2025-04-10 22:47:25', 'resources/EMP002_RoshniThapa\\Neural Networks.pdf'),
(59, 'EMP002', 'what is my name', 'I don\'t have any answer for this query in the documents. Please upload different documents or ask another query.', '2025-04-11 15:23:32', 'resources/EMP002_RoshniThapa\\Apil_CV.pdf'),
(60, 'EMP002', 'what is neural netowk', 'A neural network has several components:  an input layer that receives raw data (like images or text); hidden layers that perform computations to extract features and consist of neurons connected by weights; and an output layer that produces predictions or classifications.  Activation functions, such as Sigmoid, ReLU, and Tanh, add non-linearity to the network.  Transformer networks, based on self-attention mechanisms for handling sequential data, are the backbone of NLP models like GPT.\n', '2025-04-11 15:23:53', 'resources/EMP002_RoshniThapa\\Neural Networks.pdf'),
(61, 'EMP002', 'explain more about this', 'I don\'t have any answer for this query in the documents. Please upload different documents or ask another query.', '2025-04-11 15:24:14', 'resources/EMP002_RoshniThapa\\Neural Networks.pdf'),
(62, 'EMP002', 'explain more about neural netoweks?', 'Neural networks consist of several components:  an input layer that receives raw data (like images or text); hidden layers that perform computations to extract features and contain neurons connected by weights; and an output layer that produces predictions or classifications.  Activation functions, such as Sigmoid, ReLU, and Tanh, add non-linearity to the network.  Transformer networks, based on self-attention mechanisms for handling sequential data, are the backbone of NLP models like GPT.\n', '2025-04-11 15:24:28', 'resources/EMP002_RoshniThapa\\Neural Networks.pdf'),
(63, 'EMP002', 'explain about weights and biases?', 'I don\'t have any answer for this query in the documents. Please upload different documents or ask another query.', '2025-04-11 19:39:37', 'resources/EMP002_RoshniThapa\\Neural Networks.pdf'),
(64, 'EMP002', 'tell about neural networks', 'Neural networks are a subset of machine learning, modeled after the human brain.  They are designed to recognize patterns and solve complex problems.  They consist of interconnected layers of nodes (neurons) that process data and make predictions. A key feature is their ability to learn from data.  Neural networks work through a process involving forward propagation (input data passes through layers, with each neuron applying weights, biases, and activation functions), loss calculation (comparing predictions to actual values using loss functions like Mean Squared Error or Cross-Entropy), and backpropagation (adjusting weights and biases using gradient descent to minimize the loss function iteratively).  Training involves data preparation (cleaning, preprocessing, and splitting data into training, validation, and testing sets) and the use of optimization algorithms.  Types of neural networks include feedforward neural networks (FNNs), convolutional neural networks (CNNs), recurrent neural networks (RNNs), and generative adversarial networks (GANs), each suited for different types of data and tasks.  They are suitable for tasks involving large datasets and are powering advancements in artificial intelligence.\n', '2025-04-11 19:40:00', 'resources/EMP002_RoshniThapa\\Neural Networks.pdf'),
(65, 'EMP002', 'explain about this propsal file?', 'I don\'t have any answer for this query in the documents. Please upload different documents or ask another query.', '2025-04-29 09:45:53', 'resources/EMP002_RoshniThapa\\FYP_FINAL PROPOSAL.pdf'),
(66, 'EMP002', 'what is neural netwoek?', 'A neural network consists of an input layer that receives raw data (e.g., images, text); hidden layers that perform computations to extract features and consist of neurons connected by weights; and an output layer that produces predictions or classifications.  Activation functions, such as Sigmoid, ReLU, and Tanh, add non-linearity to the network.  Transformer networks, based on self-attention mechanisms for handling sequential data, are the backbone of natural language processing (NLP) models like GPT.\n', '2025-04-29 10:12:40', 'resources/EMP002_RoshniThapa\\Neural Networks.pdf');

-- --------------------------------------------------------

--
-- Table structure for table `comment`
--

CREATE TABLE `comment` (
  `comment_id` varchar(50) NOT NULL,
  `content` text NOT NULL,
  `comment_date` datetime NOT NULL,
  `post_id` varchar(50) DEFAULT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `is_deleted` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `comment`
--

INSERT INTO `comment` (`comment_id`, `content`, `comment_date`, `post_id`, `user_id`, `is_deleted`) VALUES
('cmnt16336', 'ok sir', '2025-04-20 23:32:06', 'PST34058', 'EMP002', '0'),
('cmnt18072', 'Great work on phase 1!', '2025-04-06 13:46:09', 'PST28785', 'EMP003', '0');

-- --------------------------------------------------------

--
-- Table structure for table `company_policies`
--

CREATE TABLE `company_policies` (
  `id` int(11) NOT NULL,
  `general_guidelines` text NOT NULL,
  `attendance_policy` text NOT NULL,
  `leave_policy` text NOT NULL,
  `working_hours` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`working_hours`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `company_policies`
--

INSERT INTO `company_policies` (`id`, `general_guidelines`, `attendance_policy`, `leave_policy`, `working_hours`) VALUES
(1, ' All employees are expected to adhere to the company\'s code of conduct, maintaining professionalism and respect in all interactions. This includes appropriate dress code, communication standards, and ethical behavior in the workplace.', '  Employees are expected to maintain regular attendance and punctuality. Any absence should be reported to the respective manager at least 2 hours before shift start. Excessive unexcused absences may result in disciplinary action.\r\n', '           \r\n               Employees are entitled to 24 days of paid leave annually. Leave requests must be submitted at least 7 days in advance for approval. Unused leave days may be carried forward to the next year with a maximum of 5 days.', '[{\"day\": \"Monday\", \"hours\": \"9:00 AM - 5:00 PM\", \"break\": \"1:00 PM - 2:00 PM\"}, {\"day\": \"Wednesday\", \"hours\": \"9:00 AM - 5:00 PM\", \"break\": \"1:00 PM - 2:00 PM\"}, {\"day\": \"Friday\", \"hours\": \"9:00 AM - 5:00 PM\", \"break\": \"1:00 PM - 2:00 PM\"}, {\"day\": \"Saturday\", \"hours\": \"Closed\", \"break\": \"No break\"}, {\"day\": \"Sunday\", \"hours\": \"Closed\", \"break\": \"No break\"}]');

-- --------------------------------------------------------

--
-- Table structure for table `likes`
--

CREATE TABLE `likes` (
  `like_id` varchar(50) NOT NULL,
  `post_id` varchar(50) DEFAULT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `is_deleted` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `likes`
--

INSERT INTO `likes` (`like_id`, `post_id`, `user_id`, `is_deleted`) VALUES
('LKE4487', 'PST34058', 'EMP002', '0'),
('LKE6510', 'PST28785', 'EMP002', '0');

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
  `status` varchar(30) DEFAULT 'unread',
  `is_deleted` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `message`
--

INSERT INTO `message` (`msg_id`, `content`, `timestamp`, `chat_id`, `sender_id`, `receiver_id`, `is_read`, `status`, `is_deleted`) VALUES
('MSG0177', 'hello sir', '2025-04-29 10:08:29', 'CHT12990721', 'EMP002', 'MGR001', 0, 'read', '0'),
('MSG1044', 'hello roshni mam', '2025-04-09 18:09:32', 'CHT73072395', 'EMP002', 'EMP001', 0, 'read', '0'),
('MSG2209', 'fs', '2025-04-11 17:18:19', 'CHT73072395', 'EMP002', 'EMP001', 0, 'unread', '0'),
('MSG2817', 'k', '2025-04-06 21:09:04', 'CHT12990721', 'EMP002', 'MGR001', 0, 'read', '0'),
('MSG3526', 'hrllo', '2025-04-06 21:08:25', 'CHT18257144', 'EMP002', 'EMP003', 0, 'unread', '0'),
('MSG4024', 'k', '2025-04-29 10:09:00', 'CHT12990721', 'MGR001', 'EMP002', 0, 'unread', '0'),
('MSG5108', 'bhi', '2025-04-06 21:09:12', 'CHT12990721', 'MGR001', 'EMP002', 0, 'read', '0'),
('MSG5147', 'sir', '2025-04-06 21:09:01', 'CHT12990721', 'EMP002', 'MGR001', 0, 'read', '0'),
('MSG5535', 'ok', '2025-04-29 10:08:57', 'CHT12990721', 'EMP002', 'MGR001', 0, 'read', '0'),
('MSG7376', 'k xa', '2025-04-29 10:08:37', 'CHT12990721', 'MGR001', 'EMP002', 0, 'unread', '0'),
('MSG8447', 'ok', '2025-04-06 21:09:16', 'CHT12990721', 'EMP002', 'MGR001', 0, 'read', '0'),
('MSG8652', 'Hello sir ayub', '2025-04-09 18:09:39', 'CHT73072395', 'EMP001', 'EMP002', 0, 'read', '0'),
('MSG9442', 'ok', '2025-04-29 10:08:41', 'CHT12990721', 'EMP002', 'MGR001', 0, 'read', '0');

-- --------------------------------------------------------

--
-- Table structure for table `notification`
--

CREATE TABLE `notification` (
  `notification_id` varchar(255) NOT NULL,
  `content` text DEFAULT NULL,
  `date` datetime DEFAULT current_timestamp(),
  `user_id` varchar(20) DEFAULT NULL,
  `task_id` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notification`
--

INSERT INTO `notification` (`notification_id`, `content`, `date`, `user_id`, `task_id`) VALUES
('NTF1434', 'New task assigned: apil, Check it out!', '2025-02-24 16:24:35', 'EMP007', 'TSK201'),
('NTF1447', 'New task assigned: Complete AI Model Development for health care system with transformers, Check it out!', '2025-04-20 22:11:31', 'EMP002', 'TSK529'),
('NTF2236', 'New task assigned: Complete AI Model Development for health care system with transformers, Check it out!', '2025-04-10 18:09:55', 'EMP002', 'TSK278'),
('NTF3701', '📢 A new announcement has been created. Check out the announcement page!', '2025-03-18 11:42:41', NULL, NULL),
('NTF3864', 'New task assigned: Lean jQUERY, Check it out!', '2025-04-08 09:54:53', 'EMP003', 'TSK288'),
('NTF3870', 'New task assigned: Complete AI Model Development for health care system, Check it out!', '2025-04-08 23:50:23', 'EMP002', 'TSK594'),
('NTF4396', 'New task assigned: Vacation tomorrow, Check it out!', '2025-04-12 00:52:21', 'EMP003', 'TSK396'),
('NTF4791', 'New task assigned: Lean jQUERY, Check it out!', '2025-04-08 11:37:14', 'EMP002', 'TSK990'),
('NTF5458', '📢 A new announcement has been created. Check out the announcement page!', '2025-04-01 11:35:27', NULL, NULL),
('NTF5526', '📢 A new announcement has been created. Check out the announcement page!', '2025-02-24 18:03:33', NULL, NULL),
('NTF6801', 'New task assigned: jhsd, Check it out!', '2025-02-24 14:06:08', 'EMP007', 'TSK594'),
('NTF6861', 'New task assigned: hi, Check it out!', '2025-04-08 09:55:18', 'EMP002', 'TSK511'),
('NTF6964', 'New task assigned: Lean jQUERY, Check it out!', '2025-04-04 09:29:05', 'EMP003', 'TSK228'),
('NTF7144', 'New task assigned: Complete AI Model Development for health care system with transformers, Check it out!', '2025-04-20 22:11:55', 'EMP002', 'TSK384'),
('NTF7156', '📢 A new announcement has been created. Check out the announcement page!', '2025-02-26 12:28:37', NULL, NULL),
('NTF7731', 'New task assigned: dc, Check it out!', '2025-02-13 11:27:08', 'EMP010', 'TSK515'),
('NTF7732', 'New task assigned: LearnHtml, Check it out!', '2025-04-12 00:50:56', 'EMP001', 'TSK252'),
('NTF8773', '📢 A new announcement has been created. Check out the announcement page!', '2025-04-20 23:39:30', NULL, NULL),
('NTF9994', '📢 A new announcement has been created. Check out the announcement page!', '2025-04-09 14:57:47', NULL, NULL);

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
  `is_deleted` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `post`
--

INSERT INTO `post` (`post_id`, `title`, `content`, `likes`, `created_date`, `user_id`, `is_deleted`) VALUES
('PST13260', 'dfs', 'dca', 0, '2025-04-07 16:52:42', 'EMP002', '1'),
('PST22628', 'd', 'cds', 0, '2025-04-07 16:34:06', 'EMP002', '1'),
('PST25167', 'sd', 'csd', 0, '2025-04-07 16:40:16', 'EMP002', '1'),
('PST28785', 'Project Update', 'Completed phase 1 and started phase 2 of the project.', 1, '2025-04-06 13:17:59', 'EMP003', '0'),
('PST34058', 'Task updation  ', 'update task properly in github', 1, '2025-04-20 23:31:42', 'EMP002', '0'),
('PST86162', 'fgb', 'b nb', 0, '2025-04-08 18:24:29', 'EMP002', '0'),
('PST87616', 'sad', 'sad', 0, '2025-04-07 17:04:57', 'EMP002', '0');

-- --------------------------------------------------------

--
-- Table structure for table `support_feedback`
--

CREATE TABLE `support_feedback` (
  `feedback_id` varchar(50) NOT NULL,
  `feedback_type` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `feedback_summary` varchar(20) DEFAULT NULL,
  `is_deleted` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `support_feedback`
--

INSERT INTO `support_feedback` (`feedback_id`, `feedback_type`, `message`, `user_id`, `created_at`, `feedback_summary`, `is_deleted`) VALUES
('FDB26108', 'complaint', 'lov you', 'EMP001', '2025-04-07 17:04:56', 'Positive 60.20%', '0'),
('FDB44560', 'complaint', 'very good company', 'EMP001', '2025-03-02 11:30:49', 'Positive 95.90%', '1'),
('FDB44775', 'complaint', 'office environment is not good', 'EMP003', '2025-04-01 10:06:29', 'Negative 96.48%', '0'),
('FDB63921', 'suggestion', 'fsdawfgbndhyuyiutbrvjehv, .ny,', 'EMP001', '2025-03-18 16:24:32', 'Positive 51.23%', '1'),
('FDB75357', 'complaint', 'What is this?', 'EMP002', '2025-04-03 11:24:12', 'Negative 64.65%', '0'),
('FDB80701', 'appreciation', 'Office environment is very much good and thanks to all management project teams for this.', 'EMP002', '2025-04-09 13:07:44', 'Positive 97.26%', '0'),
('FDB83454', 'suggestion', 'you need to make proper environment', 'EMP003', '2025-04-01 10:06:17', 'Positive 70.26%', '0'),
('FDB84525', 'appreciation', 'you are good person', 'EMP003', '2025-04-01 10:06:41', 'Positive 93.61%', '0'),
('FDB87945', 'complaint', 'I am very happy with this office environments', 'EMP002', '2025-04-20 21:40:50', 'Positive 97.36%', '0'),
('FDB88362', 'suggestion', 'love you', 'EMP003', '2025-04-02 14:19:38', 'Positive 74.04%', '0'),
('FDB90244', 'suggestion', 'love you', 'EMP001', '2025-04-07 16:52:41', 'Positive 74.04%', '0'),
('FDB96867', 'suggestion', 'hello goodbye', 'EMP002', '2025-04-11 17:18:06', 'Positive 67.95%', '0');

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
  `is_deleted` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `task`
--

INSERT INTO `task` (`task_id`, `title`, `description`, `due_date`, `docs_path`, `status`, `assigned_to_id`, `assigned_by_id`, `is_deleted`) VALUES
('TSK252', 'LearnHtml', '', '2025-04-15 00:00:00', NULL, 'Pending', 'EMP001', 'MGR001', '0'),
('TSK278', 'Complete AI Model Development for health care system with transformers', 'Develop a complete AI model for a healthcare system using transformer-based architectures. This involves data preprocessing, designing a suitable transformer model (e.g., BERT or custom encoder-decoder), training on relevant clinical or medical datasets, and deploying the model for tasks such as diagnosis prediction, medical text summarization, or patient data analysis to enhance decision-making and patient care.', '2025-04-24 00:00:00', 'resources\\EMP002_RoshniThapa\\OIP (3).jpg', 'Approved', 'EMP002', 'MGR001', '1'),
('TSK384', 'Complete AI Model Development for health care system with transformers', 'ok', '2025-04-14 00:00:00', 'resources\\EMP002_RoshniThapa\\FYPSubmissionGuidelines2025_82787.pdf', 'submitted', 'EMP002', 'MGR001', '0'),
('TSK396', 'Vacation tomorrow', '', '2025-04-16 00:00:00', NULL, 'Pending', 'EMP003', 'MGR001', '0'),
('TSK511', 'hi', 'fghdsds', '2025-04-23 00:00:00', 'resources\\EMP002_RoshniThapa\\worksphere.rdp', 'submitted', 'EMP002', 'MGR001', '1'),
('TSK529', 'Complete AI Model Development for health care system with transformers', '', '2025-04-02 00:00:00', NULL, 'Pending', 'EMP002', 'MGR001', '0'),
('TSK594', 'Complete AI Model Development for health care system', 'Completed full Ai model training but remaining integration into Apis.', '2025-04-24 00:00:00', 'resources\\EMP002_RoshniThapa\\themed_presentation.pptx', 'Approved', 'EMP002', 'MGR001', '0'),
('TSK990', 'Lean jQUERY', 'jdds', '2025-04-16 00:00:00', 'resources\\EMP002_RoshniThapa\\worksphere.rdp', 'submitted', 'EMP002', 'MGR001', '0');

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
  `is_deleted` tinyint(1) DEFAULT 0,
  `isannouncement_read` varchar(10) DEFAULT NULL,
  `istask_read` varchar(10) DEFAULT NULL,
  `isnotificationread` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`user_id`, `full_name`, `email`, `phone`, `password`, `role`, `department_name`, `position`, `otp_code`, `is_deleted`, `isannouncement_read`, `istask_read`, `isnotificationread`) VALUES
('EMP001', 'Ayub bhatta', 'bikash047basnet@gmail.com', '3456789', '$2b$12$aSzPB65LlHq8S9XyYt63fuhVi0Q97DA1vC4FHtaKltLW435IzqyYa', 'employee', 'Ai', 'junior developer', '918979', 1, 'false', 'false', 'false'),
('EMP002', 'RoshniThapa', 'roshnithapaa@gmail.com', '9067143349', '$2b$12$4ZSM85nb3BQ.qBgn8FbDaOTd.Ur4pHwNKixUTr0ghM7GoPEVBV4.K', 'employee', 'Engineering', 'senior ml developer', '099882', 0, 'true', '1', '1'),
('EMP003', 'Sagar Kshetri', 'apilcode566@gmail.com', '9863267573', '$2b$12$zm/vBi7AmcoEJTQMnujnCOpjFYLYu.nvF3aPcaIqLkB.qpGinlaIa', 'employee', 'AI', 'junior ml developer', '590468', 0, 'false', 'false', 'false'),
('EMP004', 'Miraj Bhatta', 'apilthapa87@gmail.com', '9867004146', '$2b$12$q5GXfY.zFtk51E4moQ3HNeqoExgUvVIQzRUzMU8g.w7WrhUMiils.', 'employee', 'AI', 'junior ml developer', '982932', 0, 'false', NULL, 'false'),
('HR002', 'Worksphere HR', 'workspherehr@gmail.com', NULL, 'don', 'HR', NULL, NULL, '634215', 0, 'false', NULL, 'false'),
('MGR001', 'Worksphere Manager', 'workspheremanager@gmail.com', NULL, '$2b$12$p5SkYM95CPNn5HYyeXpL1upwb1LzT6LwLXcaLhKRXlMddyXxrvXqW', 'manager', NULL, NULL, '123456', 0, 'false', NULL, 'false');

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
-- Indexes for table `chat_history`
--
ALTER TABLE `chat_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `comment`
--
ALTER TABLE `comment`
  ADD PRIMARY KEY (`comment_id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `company_policies`
--
ALTER TABLE `company_policies`
  ADD PRIMARY KEY (`id`);

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
-- Indexes for table `notification`
--
ALTER TABLE `notification`
  ADD PRIMARY KEY (`notification_id`);

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
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `chat_history`
--
ALTER TABLE `chat_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=67;

--
-- AUTO_INCREMENT for table `company_policies`
--
ALTER TABLE `company_policies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

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
-- Constraints for table `chat_history`
--
ALTER TABLE `chat_history`
  ADD CONSTRAINT `chat_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE;

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
