from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

# --- Auth Schemas ---
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Foydalanuvchi logini")
    password: str = Field(..., min_length=4, max_length=100, description="Parol")
    full_name: Optional[str] = Field("Bo'lajak Pedagog", description="F.I.Sh.")

class UserLogin(BaseModel):
    username: str = Field(..., description="Foydalanuvchi logini")
    password: str = Field(..., description="Parol")

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    xp: int
    level: int
    status_title: str
    next_level_xp: int
    progress_percentage: int
    badges: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# --- Gamification Schemas ---
class BadgeOut(BaseModel):
    id: int
    code: str
    title: str
    description: str
    icon: str
    unlocked: bool = False

    model_config = ConfigDict(from_attributes=True)

# --- Test & Quiz Schemas ---
class QuizQuestionOut(BaseModel):
    """Test topshirig'i ichidagi savol (to'g'ri javob yashirilgan)"""
    id: int
    order_in_quiz: int
    question: str
    options: List[str]

    model_config = ConfigDict(from_attributes=True)

class QuizDetailOut(BaseModel):
    """Test topshirig'i (10 talik dars testi, 25 talik modul testi, 50 talik kurs yakuniy testi)"""
    quiz_type: str  # 'lesson', 'module', 'course_final'
    title: str
    total_questions: int
    time_limit_minutes: int
    lesson_id: Optional[int] = None
    module_id: Optional[int] = None
    questions: List[QuizQuestionOut]

class QuizSubmitRequest(BaseModel):
    quiz_type: str  # 'lesson', 'module', 'course_final'
    lesson_id: Optional[int] = None
    module_id: Optional[int] = None
    answers: Dict[str, int] = Field(..., description="Savol ID si va tanlangan variant indeksi: {'101': 0, '102': 2}")

class QuestionReviewOut(BaseModel):
    id: int
    order_in_quiz: int
    question: str
    options: List[str]
    selected_option: Optional[int] = None
    correct_option: int
    is_correct: bool
    explanation: str

class QuizSubmitResponse(BaseModel):
    quiz_type: str
    title: str
    total_questions: int
    correct_answers: int
    score_percentage: int
    xp_earned: int
    user_xp: int
    user_level: int
    user_status: str
    passed: bool
    new_badge_unlocked: Optional[str] = None
    questions_review: List[QuestionReviewOut]

# Individual Test Schema (backward compatibility)
class TestOut(BaseModel):
    id: int
    module_id: Optional[int]
    lesson_id: Optional[int]
    quiz_type: str
    order_in_quiz: int
    question: str
    options: List[str]
    is_module_final: bool
    is_course_final: bool
    xp_reward: int

    model_config = ConfigDict(from_attributes=True)

class TaskOut(BaseModel):
    id: int
    module_id: Optional[int]
    lesson_id: Optional[int]
    title: str
    prompt: str
    pedagogical_criteria: str
    is_module_final: bool
    max_score: int
    xp_reward: int

    model_config = ConfigDict(from_attributes=True)

class LessonOut(BaseModel):
    id: int
    module_id: int
    order: int
    title: str
    lesson_type: str
    content: str
    video_url: Optional[str] = None
    reading_time_minutes: int
    xp_reward: int
    quiz_questions_count: int = 10  # Har bir darsdan so'ng 10 ta test
    tasks: List[TaskOut] = []

    model_config = ConfigDict(from_attributes=True)

class ModuleOut(BaseModel):
    id: int
    order: int
    title: str
    description: str
    pedagogical_component: str
    xp_reward: int
    lessons: List[LessonOut] = []
    final_quiz_questions_count: int = 25  # Har bir modul yakunida 25 ta test
    final_tasks: List[TaskOut] = []

    model_config = ConfigDict(from_attributes=True)

# --- Task Submission & AI Evaluation Schemas ---
class SubmitOpenTaskRequest(BaseModel):
    task_id: int
    answer_text: str = Field(..., min_length=20, description="Pedagogik topshiriqqa javob")

class SubmitOpenTaskResponse(BaseModel):
    submission_id: int
    score: int
    feedback: str
    strengths: List[str]
    improvements: List[str]
    pedagogical_components: Dict[str, int]
    xp_earned: int
    user_xp: int
    user_level: int
    user_status: str
    new_badge_unlocked: Optional[str] = None

# Individual closed test submission (for instant single-question runner)
class SubmitClosedTestRequest(BaseModel):
    test_id: int
    selected_option: int

class SubmitClosedTestResponse(BaseModel):
    test_id: int
    is_correct: bool
    correct_option: int
    explanation: str
    xp_earned: int
    user_xp: int
    user_level: int
    user_status: str
