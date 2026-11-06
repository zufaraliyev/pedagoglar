from datetime import datetime
from typing import List, Optional, Any, Dict
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class User(Base):
    """
    Foydalanuvchilar modeli (MySQL jadvali: users).
    Ro'yxatdan o'tish va kirish faqat login va parol orqali amalga oshiriladi.
    """
    __tablename__ = "users"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(128), default="Bo'lajak Pedagog")
    role: Mapped[str] = mapped_column(String(32), default="student")

    # Gamifikatsiya
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    status_title: Mapped[str] = mapped_column(String(64), default="Pedagog-izlanuvchi")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Aloqalar
    submissions: Mapped[List["Submission"]] = relationship(
        "Submission", back_populates="user", cascade="all, delete-orphan"
    )
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="user", cascade="all, delete-orphan"
    )
    test_attempts: Mapped[List["TestAttempt"]] = relationship(
        "TestAttempt", back_populates="user", cascade="all, delete-orphan"
    )
    user_badges: Mapped[List["UserBadge"]] = relationship(
        "UserBadge", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} level={self.level} xp={self.xp}>"


class Module(Base):
    """
    O'quv kursi modullari (M.B. Muxamadaliyeva 4 ta komponenti asosida).
    """
    __tablename__ = "modules"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order: Mapped[int] = mapped_column(Integer, default=1, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    pedagogical_component: Mapped[str] = mapped_column(String(64), default="kognitiv")
    xp_reward: Mapped[int] = mapped_column(Integer, default=150)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order"
    )
    tests: Mapped[List["Test"]] = relationship(
        "Test", back_populates="module", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="module", cascade="all, delete-orphan"
    )


class Lesson(Base):
    """
    Modul darslari: 'lecture' (Ma'ruza) yoki 'practice' (Amaliyot).
    Har bir dars yakunida 10 ta testli test topshirig'i bo'ladi.
    """
    __tablename__ = "lessons"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    lesson_type: Mapped[str] = mapped_column(String(32), default="lecture")  # 'lecture' yoki 'practice'
    content: Mapped[str] = mapped_column(Text, default="")
    video_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    reading_time_minutes: Mapped[int] = mapped_column(Integer, default=10)
    xp_reward: Mapped[int] = mapped_column(Integer, default=20)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    module: Mapped["Module"] = relationship("Module", back_populates="lessons")
    tests: Mapped[List["Test"]] = relationship(
        "Test", back_populates="lesson", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="lesson", cascade="all, delete-orphan"
    )


class Test(Base):
    """
    Individual test savollari:
    - Dars yakunida: 10 ta test (`quiz_type = 'lesson'`)
    - Modul yakunida: 25 ta test (`quiz_type = 'module'`, `is_module_final = True`)
    - Kurs yakunida: 50 ta test (`quiz_type = 'course_final'`, `is_course_final = True`)
    """
    __tablename__ = "tests"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=True
    )
    lesson_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True
    )
    quiz_type: Mapped[str] = mapped_column(String(32), default="lesson")  # 'lesson', 'module', 'course_final'
    order_in_quiz: Mapped[int] = mapped_column(Integer, default=1)
    
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[Any] = mapped_column(JSON, nullable=False)  # JSON array: ["Variant A", "Variant B", ...]
    correct_option: Mapped[int] = mapped_column(Integer, nullable=False)  # 0, 1, 2, 3
    explanation: Mapped[str] = mapped_column(Text, default="")
    is_module_final: Mapped[bool] = mapped_column(Boolean, default=False)
    is_course_final: Mapped[bool] = mapped_column(Boolean, default=False)
    xp_reward: Mapped[int] = mapped_column(Integer, default=5)

    module: Mapped[Optional["Module"]] = relationship("Module", back_populates="tests")
    lesson: Mapped[Optional["Lesson"]] = relationship("Lesson", back_populates="tests")
    attempts: Mapped[List["TestAttempt"]] = relationship(
        "TestAttempt", back_populates="test", cascade="all, delete-orphan"
    )


class QuizAttempt(Base):
    """
    Butun test topshirig'i (10 talik, 25 talik yoki 50 talik) yechish tarixi va natijalari
    """
    __tablename__ = "quiz_attempts"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_type: Mapped[str] = mapped_column(String(32), nullable=False)  # 'lesson', 'module', 'course_final'
    lesson_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True)
    module_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=True)
    
    total_questions: Mapped[int] = mapped_column(Integer, default=10)  # 10, 25, 50
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    score_percentage: Mapped[int] = mapped_column(Integer, default=0)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    user_answers: Mapped[Any] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")


class Task(Base):
    """
    Ochiq savol va amaliy topshiriqlar (Sun'iy Intellekt baholaydi).
    """
    __tablename__ = "tasks"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=True
    )
    lesson_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    pedagogical_criteria: Mapped[str] = mapped_column(Text, default="")
    sample_solution: Mapped[str] = mapped_column(Text, default="")
    is_module_final: Mapped[bool] = mapped_column(Boolean, default=False)
    max_score: Mapped[int] = mapped_column(Integer, default=100)
    xp_reward: Mapped[int] = mapped_column(Integer, default=50)

    module: Mapped[Optional["Module"]] = relationship("Module", back_populates="tasks")
    lesson: Mapped[Optional["Lesson"]] = relationship("Lesson", back_populates="tasks")
    submissions: Mapped[List["Submission"]] = relationship(
        "Submission", back_populates="task", cascade="all, delete-orphan"
    )


class Submission(Base):
    """
    Ochiq amaliy javob va OpenRouter SI ekspertizasi natijalari.
    """
    __tablename__ = "submissions"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)

    ai_score: Mapped[int] = mapped_column(Integer, default=0)
    ai_feedback: Mapped[str] = mapped_column(Text, default="")
    strengths: Mapped[Any] = mapped_column(JSON, default=list)
    improvements: Mapped[Any] = mapped_column(JSON, default=list)
    pedagogical_analysis: Mapped[Any] = mapped_column(JSON, default=dict)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="submissions")
    task: Mapped["Task"] = relationship("Task", back_populates="submissions")


class TestAttempt(Base):
    """
    Alohida savol bo'yicha urinishlar
    """
    __tablename__ = "test_attempts"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    selected_option: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="test_attempts")
    test: Mapped["Test"] = relationship("Test", back_populates="attempts")


class Badge(Base):
    """
    Gamifikatsiya yutuq nishonlari
    """
    __tablename__ = "badges"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    icon: Mapped[str] = mapped_column(String(64), default="🏆")
    min_xp: Mapped[int] = mapped_column(Integer, default=0)

    user_badges: Mapped[List["UserBadge"]] = relationship(
        "UserBadge", back_populates="badge", cascade="all, delete-orphan"
    )


class UserBadge(Base):
    """
    Foydalanuvchi nishonlari
    """
    __tablename__ = "user_badges"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id: Mapped[int] = mapped_column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    awarded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="user_badges")
    badge: Mapped["Badge"] = relationship("Badge", back_populates="user_badges")
