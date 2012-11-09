-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generato il: Nov 06, 2012 alle 23:14
-- Versione del server: 5.5.24
-- Versione PHP: 5.4.4-7

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `xmppmessenger`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `presence`
--

CREATE TABLE `presence` (
  `userid` char(48) NOT NULL COMMENT 'User ID',
  `timestamp` datetime NOT NULL COMMENT 'Cache entry timestamp',
  `status` mediumtext CHARACTER SET utf8 COLLATE utf8_bin,
  `show` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`userid`)
) ENGINE=MyISAM DEFAULT CHARSET=ascii COMMENT='User presence cache';

-- --------------------------------------------------------

--
-- Struttura della tabella `servers`
--

CREATE TABLE `servers` (
  `fingerprint` char(40) NOT NULL COMMENT 'Server key fingerprint',
  `host` varchar(100) NOT NULL COMMENT 'Server address',
  PRIMARY KEY (`fingerprint`)
) ENGINE=MyISAM DEFAULT CHARSET=ascii COMMENT='Servers';

-- --------------------------------------------------------

--
-- Struttura della tabella `stanzas`
--

CREATE TABLE `stanzas` (
  `id` varchar(30) CHARACTER SET ascii COLLATE ascii_bin NOT NULL COMMENT 'Stanza ID',
  `sender` varchar(48) CHARACTER SET ascii NOT NULL COMMENT 'From',
  `recipient` varchar(48) CHARACTER SET ascii NOT NULL COMMENT 'To',
  `content` mediumblob NOT NULL COMMENT 'Stanza content',
  `timestamp` datetime NOT NULL COMMENT 'Stanza timestamp',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Pending stanzas';

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;