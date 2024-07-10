-- phpMyAdmin SQL Dump
-- version 5.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 11, 2024 at 12:54 PM
-- Server version: 10.4.11-MariaDB
-- PHP Version: 7.4.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `compliant_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `compliant_tbl`
--

CREATE TABLE `compliant_tbl` (
  `id` int(50) NOT NULL,
  `compliant_type` varchar(50) NOT NULL,
  `description` varchar(500) NOT NULL,
  `City` varchar(50) NOT NULL,
  `Street` varchar(50) NOT NULL,
  `Pincode` varchar(50) NOT NULL,
  `filename` varchar(120) NOT NULL,
  `status` varchar(50) NOT NULL,
  `username` varchar(50) NOT NULL,
  `regdate` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `compliant_tbl`
--

INSERT INTO `compliant_tbl` (`id`, `compliant_type`, `description`, `City`, `Street`, `Pincode`, `filename`, `status`, `username`, `regdate`) VALUES
(1, 'Water', 'We have been experiencing a severe water shortage in our locality for the past 20 days. The supply of drinking water has been completely disrupted, causing significant inconvenience to all residents. We urgently need a resolution to this critical issue.', 'Salem', 'Maariyamman kovil street', '637301', 'water.jpg', 'COMPLETED', 'boopathi', '2024-03-11'),
(2, 'EB', 'Our neighborhood is facing issues with disrupted drinking water supply and malfunctioning street lights. Immediate attention is required. ', 'Salem', 'Maariyamman kovil street', '637301', 'eb.jpg', 'PROCESSING', 'boopathi', '2024-03-11'),
(3, 'Road', 'The condition of the roads in our locality is substandard, leading to a challenging commute. This issue needs to be addressed promptly for the convenience of all residents. ', 'salem', 'Maariyamman kovil street', '637301', 'road.jpg', 'COMPLETED', 'boopathi', '2024-03-11'),
(4, 'Drinage', 'The drainage system in our locality is inadequate, leading to frequent blockages and overflows. This is a significant health and hygiene concern that needs immediate resolution ', 'Salem', 'Maariyamman kovil street', '637301', 'drainage.jpg', 'PENDING', 'boopathi', '2024-03-11'),
(5, 'Road', 'road problem ', 'Salem', 'Maariyamman kovil street', '637301', 'road.jpg', 'PROCESSING', 'boopathi', '2024-03-11'),
(6, 'other', 'The garbage collection in our street has been neglected, resulting in litter spreading around. This poses a serious environmental and health risk that needs immediate attention and action. ', 'Salem', 'Maariyamman kovil street', '637301', 'dust.jpg', 'PROCESSING', 'boopathi', '2024-03-11');


-- --------------------------------------------------------

--
-- Table structure for table `usertbl`
--

CREATE TABLE `usertbl` (
  `Name` varchar(50) NOT NULL,
  `Emailid` varchar(50) NOT NULL,
  `contactno` varchar(50) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `usertbl`
--

INSERT INTO `usertbl` (`Name`, `Emailid`, `contactno`, `username`, `password`) VALUES
('boopathi', 'boopathisk7@gmail.com', '6374871838', 'boopathi', 'boopathi');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `compliant_tbl`
--
ALTER TABLE `compliant_tbl`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `compliant_tbl`
--
ALTER TABLE `compliant_tbl`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
