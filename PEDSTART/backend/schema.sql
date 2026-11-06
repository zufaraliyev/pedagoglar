-- ====================================================================
-- PEDSTART PLATFORMASI: MySQL Ma'lumotlar Bazasi Sxemasi (schema.sql)
-- Kodlash: utf8mb4_unicode_ci (O'zbek lotin va kirill alifbosi uchun)
-- ====================================================================

CREATE DATABASE IF NOT EXISTS `pedstart_db`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `pedstart_db`;

-- 1. Foydalanuvchilar (Users)
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(64) NOT NULL UNIQUE,
  `hashed_password` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(128) NOT NULL DEFAULT 'Bo\'lajak Pedagog',
  `role` VARCHAR(32) NOT NULL DEFAULT 'student',
  `xp` INT NOT NULL DEFAULT 0,
  `level` INT NOT NULL DEFAULT 1,
  `status_title` VARCHAR(64) NOT NULL DEFAULT 'Pedagog-izlanuvchi',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Modullar (Modules)
CREATE TABLE IF NOT EXISTS `modules` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order` INT NOT NULL DEFAULT 1,
  `title` VARCHAR(255) NOT NULL,
  `description` TEXT,
  `pedagogical_component` VARCHAR(64) NOT NULL DEFAULT 'kognitiv',
  `xp_reward` INT NOT NULL DEFAULT 150,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_modules_order` (`order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Darslar (Lessons: Ma'ruza va Amaliyot)
CREATE TABLE IF NOT EXISTS `lessons` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `module_id` INT NOT NULL,
  `order` INT NOT NULL DEFAULT 1,
  `title` VARCHAR(255) NOT NULL,
  `lesson_type` VARCHAR(32) NOT NULL DEFAULT 'lecture',
  `content` LONGTEXT,
  `reading_time_minutes` INT NOT NULL DEFAULT 10,
  `xp_reward` INT NOT NULL DEFAULT 20,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`module_id`) REFERENCES `modules`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Test Savollari (Tests: 10 talik dars testi, 25 talik modul testi, 50 talik kurs attestatsiyasi)
CREATE TABLE IF NOT EXISTS `tests` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `module_id` INT NULL,
  `lesson_id` INT NULL,
  `quiz_type` VARCHAR(32) NOT NULL DEFAULT 'lesson', -- 'lesson', 'module', 'course_final'
  `order_in_quiz` INT NOT NULL DEFAULT 1,
  `question` TEXT NOT NULL,
  `options` JSON NOT NULL,
  `correct_option` INT NOT NULL,
  `explanation` TEXT,
  `is_module_final` BOOLEAN NOT NULL DEFAULT FALSE,
  `is_course_final` BOOLEAN NOT NULL DEFAULT FALSE,
  `xp_reward` INT NOT NULL DEFAULT 5,
  FOREIGN KEY (`module_id`) REFERENCES `modules`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`lesson_id`) REFERENCES `lessons`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Test Topshiriqlari Yechish Tarixi (Quiz Attempts)
CREATE TABLE IF NOT EXISTS `quiz_attempts` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `quiz_type` VARCHAR(32) NOT NULL, -- 'lesson', 'module', 'course_final'
  `lesson_id` INT NULL,
  `module_id` INT NULL,
  `total_questions` INT NOT NULL DEFAULT 10,
  `correct_answers` INT NOT NULL DEFAULT 0,
  `score_percentage` INT NOT NULL DEFAULT 0,
  `xp_earned` INT NOT NULL DEFAULT 0,
  `user_answers` JSON NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`lesson_id`) REFERENCES `lessons`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`module_id`) REFERENCES `modules`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Ochiq Topshiriqlar (Tasks)
CREATE TABLE IF NOT EXISTS `tasks` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `module_id` INT NULL,
  `lesson_id` INT NULL,
  `title` VARCHAR(255) NOT NULL,
  `prompt` TEXT NOT NULL,
  `pedagogical_criteria` TEXT,
  `sample_solution` TEXT,
  `is_module_final` BOOLEAN NOT NULL DEFAULT FALSE,
  `max_score` INT NOT NULL DEFAULT 100,
  `xp_reward` INT NOT NULL DEFAULT 50,
  FOREIGN KEY (`module_id`) REFERENCES `modules`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`lesson_id`) REFERENCES `lessons`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Ochiq Topshiriq Topshirilishi va SI Bahosi (Submissions)
CREATE TABLE IF NOT EXISTS `submissions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `task_id` INT NOT NULL,
  `answer_text` LONGTEXT NOT NULL,
  `ai_score` INT NOT NULL DEFAULT 0,
  `ai_feedback` TEXT,
  `strengths` JSON,
  `improvements` JSON,
  `pedagogical_analysis` JSON,
  `xp_earned` INT NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`task_id`) REFERENCES `tasks`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Alohida Test Natijalari (Test Attempts)
CREATE TABLE IF NOT EXISTS `test_attempts` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `test_id` INT NOT NULL,
  `selected_option` INT NOT NULL,
  `is_correct` BOOLEAN NOT NULL,
  `xp_earned` INT NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`test_id`) REFERENCES `tests`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Nishonlar (Badges)
CREATE TABLE IF NOT EXISTS `badges` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `code` VARCHAR(64) NOT NULL UNIQUE,
  `title` VARCHAR(128) NOT NULL,
  `description` TEXT,
  `icon` VARCHAR(64) NOT NULL DEFAULT '🏆',
  `min_xp` INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Foydalanuvchi Nishonlari (User Badges)
CREATE TABLE IF NOT EXISTS `user_badges` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `badge_id` INT NOT NULL,
  `awarded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`badge_id`) REFERENCES `badges`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
