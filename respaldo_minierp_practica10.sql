-- MySQL dump 10.13  Distrib 8.4.11, for Linux (x86_64)
--
-- Host: localhost    Database: minierp
-- ------------------------------------------------------
-- Server version	8.4.11

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alumnos`
--

DROP TABLE IF EXISTS `alumnos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumnos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Nctrl` varchar(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `promedio` decimal(4,2) DEFAULT NULL,
  `carrera` varchar(100) DEFAULT NULL,
  `semestre` int DEFAULT NULL,
  `sexo` char(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `Nctrl` (`Nctrl`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alumnos`
--

LOCK TABLES `alumnos` WRITE;
/*!40000 ALTER TABLE `alumnos` DISABLE KEYS */;
INSERT INTO `alumnos` VALUES (2,'23670002','Carlos Perez',8.50,'Sistemas Computacionales',5,'M'),(3,'23670003','Maria Garcia',9.40,'Informatica',3,'F'),(4,'23670004','Ramiro Diaz',8.50,'Contador Publico',1,'M'),(5,'23670005','Jasmin Trejo',9.50,'Sistemas Computacionales',5,'F'),(7,'23670007','Laura Soto',9.00,'Sistemas Computacionales',6,'F'),(8,'23670006','Ana Torres Actualizada',9.50,'Sistemas Computacionales',6,'F'),(15,'SEC001','Alumno Seguridad',9.20,'Sistemas Computacionales',7,'M'),(16,'SEC002','Alumno Consulta',8.50,'Sistemas Computacionales',6,'M'),(19,'SEC999','Alumno Seguridad',8.50,'Sistemas Computacionales',5,'M'),(21,'2367008','Joana Valdez',7.90,'Sistemas Computacionales',1,'F');
/*!40000 ALTER TABLE `alumnos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `rol` varchar(20) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `create_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin','scrypt:32768:8:1$lO0nluhDj1kwvcAj$deb68f799ede0de02c866ddc06d590ae7520eff3652f0e1b027f676e8a3a2081800f16ffa789b25acb71e321729daf985f07b15043faa6ed5506f2cb32b36252','admin',1,'2026-09-29 18:05:49'),(2,'consulta','scrypt:32768:8:1$vI5JOit8WxzdkBmJ$e5980e851c93d50e2e2b32643278d3e3d2227db7a25df41bc9de4481b63202ad26a05f1e8281286875cb0c530a78c6ec34f2bb4dfe8a24efa87446f617284ae9','consulta',1,'2026-09-29 18:05:49');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-01 19:23:11
