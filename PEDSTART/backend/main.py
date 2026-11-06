import os
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import engine, get_db, Base, ensure_mysql_database_exists
import models
import schemas
from security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from gamification import calculate_level_and_status, check_and_award_badges
from ai_evaluator import evaluate_pedagogical_task
from seed import seed_data

logger = logging.getLogger("pedstart.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_mysql_database_exists()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await seed_data()
    except Exception:
        logger.exception("Ma'lumotlar bazasini ishga tushirishda xatolik.")
        raise
    try:
        yield
    finally:
        await engine.dispose()

app = FastAPI(
    title="PedStart API",
    description="Bo'lajak pedagoglar uchun muvaffaqiyatli start va raqamli tayyorgarlik platformasi",
    version="1.0.0",
    lifespan=lifespan
)

def build_user_out(user: models.User, badge_codes: List[str] = None) -> schemas.UserOut:
    level, status_title, next_xp, progress_pct = calculate_level_and_status(user.xp)
    return schemas.UserOut(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        xp=user.xp,
        level=level,
        status_title=status_title,
        next_level_xp=next_xp,
        progress_percentage=progress_pct,
        badges=badge_codes or []
    )


# ==========================================
# 1. AUTENTIFIKATSIYA ENDPOINTLARI
# ==========================================

@app.post("/api/auth/register", response_model=schemas.TokenResponse)
async def register(payload: schemas.UserRegister, db: AsyncSession = Depends(get_db)):
    stmt = select(models.User).where(models.User.username == payload.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ushbu login band. Iltimos, boshqa login tanlang."
        )

    new_user = models.User(
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name or "Bo'lajak Pedagog",
        xp=0,
        level=1,
        status_title="Pedagog-izlanuvchi"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    badge_codes = []
    try:
        await check_and_award_badges(new_user, db, action_type="register")
        await db.commit()
        badge_codes = ["🌱"]
    except Exception as e:
        print(f"Boshlang'ich nishon berishda ogohlantirish: {e}")

    token = create_access_token(data={"sub": new_user.username})
    user_out = build_user_out(new_user, badge_codes=badge_codes)
    return schemas.TokenResponse(access_token=token, user=user_out)


@app.post("/api/auth/login", response_model=schemas.TokenResponse)
async def login(payload: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(models.User).where(models.User.username == payload.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login yoki parol noto'g'ri kiritildi"
        )

    badge_stmt = (
        select(models.Badge.icon)
        .join(models.UserBadge, models.Badge.id == models.UserBadge.badge_id)
        .where(models.UserBadge.user_id == user.id)
    )
    badge_res = await db.execute(badge_stmt)
    user_badges = badge_res.scalars().all()

    token = create_access_token(data={"sub": user.username})
    user_out = build_user_out(user, badge_codes=list(user_badges))
    return schemas.TokenResponse(access_token=token, user=user_out)


@app.get("/api/auth/me", response_model=schemas.UserOut)
async def get_current_user_profile(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    badge_stmt = (
        select(models.Badge.icon)
        .join(models.UserBadge, models.Badge.id == models.UserBadge.badge_id)
        .where(models.UserBadge.user_id == current_user.id)
    )
    badge_res = await db.execute(badge_stmt)
    user_badges = badge_res.scalars().all()
    return build_user_out(current_user, badge_codes=list(user_badges))


# ==========================================
# 2. MODULLAR VA DARSLAR STRUKTURASI
# ==========================================

@app.get("/api/modules", response_model=List[schemas.ModuleOut])
async def get_modules(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(models.Module)
        .options(
            selectinload(models.Module.lessons).selectinload(models.Lesson.tasks),
            selectinload(models.Module.tasks),
        )
        .order_by(models.Module.order)
    )
    result = await db.execute(stmt)
    modules = result.scalars().all()

    response = []
    for m in modules:
        final_tasks = [tk for tk in m.tasks if tk.is_module_final]

        response.append(schemas.ModuleOut(
            id=m.id,
            order=m.order,
            title=m.title,
            description=m.description,
            pedagogical_component=m.pedagogical_component,
            xp_reward=m.xp_reward,
            lessons=[
                schemas.LessonOut(
                    id=l.id,
                    module_id=l.module_id,
                    order=l.order,
                    title=l.title,
                    lesson_type=l.lesson_type,
                    content=l.content,
                    video_url=l.video_url,
                    reading_time_minutes=l.reading_time_minutes,
                    xp_reward=l.xp_reward,
                    quiz_questions_count=10,  # 10 ta test
                    tasks=[
                        schemas.TaskOut(
                            id=tk.id,
                            module_id=tk.module_id,
                            lesson_id=tk.lesson_id,
                            title=tk.title,
                            prompt=tk.prompt,
                            pedagogical_criteria=tk.pedagogical_criteria,
                            is_module_final=tk.is_module_final,
                            max_score=tk.max_score,
                            xp_reward=tk.xp_reward
                        ) for tk in l.tasks
                    ]
                ) for l in m.lessons
            ],
            final_quiz_questions_count=25,  # 25 ta modul yakuniy testi
            final_tasks=[
                schemas.TaskOut(
                    id=tk.id,
                    module_id=tk.module_id,
                    lesson_id=tk.lesson_id,
                    title=tk.title,
                    prompt=tk.prompt,
                    pedagogical_criteria=tk.pedagogical_criteria,
                    is_module_final=tk.is_module_final,
                    max_score=tk.max_score,
                    xp_reward=tk.xp_reward
                ) for tk in final_tasks
            ]
        ))
    return response


# ==========================================
# 3. TEST TOPSHIRIQLARI: 10 ta, 25 ta va 50 talik QUIZ
# ==========================================

@app.get("/api/quizzes/lesson/{lesson_id}", response_model=schemas.QuizDetailOut)
async def get_lesson_quiz(lesson_id: int, db: AsyncSession = Depends(get_db)):
    """Har bir ma'ruza va amaliyotdan so'ng 10 ta testli test topshirig'i"""
    stmt_lesson = select(models.Lesson).where(models.Lesson.id == lesson_id)
    res_l = await db.execute(stmt_lesson)
    lesson = res_l.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    stmt = (
        select(models.Test)
        .where(models.Test.lesson_id == lesson_id)
        .order_by(models.Test.order_in_quiz)
        .limit(10)
    )
    result = await db.execute(stmt)
    tests = result.scalars().all()

    return schemas.QuizDetailOut(
        quiz_type="lesson",
        title=f"{lesson.title} — Test topshirig'i (10 ta savol)",
        total_questions=len(tests),
        time_limit_minutes=15,
        lesson_id=lesson.id,
        module_id=lesson.module_id,
        questions=[
            schemas.QuizQuestionOut(
                id=t.id,
                order_in_quiz=t.order_in_quiz,
                question=t.question,
                options=t.options
            ) for t in tests
        ]
    )


@app.get("/api/quizzes/module/{module_id}", response_model=schemas.QuizDetailOut)
async def get_module_quiz(module_id: int, db: AsyncSession = Depends(get_db)):
    """Har bir modul yakunida 25 ta testli umumlashtiruvchi test topshirig'i"""
    stmt_mod = select(models.Module).where(models.Module.id == module_id)
    res_m = await db.execute(stmt_mod)
    module = res_m.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Modul topilmadi")

    stmt = (
        select(models.Test)
        .where(models.Test.module_id == module_id, models.Test.is_module_final == True)
        .order_by(models.Test.order_in_quiz)
        .limit(25)
    )
    result = await db.execute(stmt)
    tests = result.scalars().all()

    return schemas.QuizDetailOut(
        quiz_type="module",
        title=f"{module.title} — Modul Yakuniy Testi (25 ta savol)",
        total_questions=len(tests),
        time_limit_minutes=35,
        module_id=module.id,
        questions=[
            schemas.QuizQuestionOut(
                id=t.id,
                order_in_quiz=t.order_in_quiz,
                question=t.question,
                options=t.options
            ) for t in tests
        ]
    )


@app.get("/api/quizzes/course-final", response_model=schemas.QuizDetailOut)
async def get_course_final_quiz(db: AsyncSession = Depends(get_db)):
    """Kurs yakunida 50 ta testli katta yakuniy test topshirig'i (Attestatsiya)"""
    stmt = (
        select(models.Test)
        .where(models.Test.is_course_final == True)
        .order_by(models.Test.order_in_quiz)
        .limit(50)
    )
    result = await db.execute(stmt)
    tests = result.scalars().all()

    return schemas.QuizDetailOut(
        quiz_type="course_final",
        title="PedStart: Boshlang'ich ta'lim pedagogikasi kursi bo'yicha YAKUNIY ATTESTATSIYA (50 ta savol)",
        total_questions=len(tests),
        time_limit_minutes=60,
        questions=[
            schemas.QuizQuestionOut(
                id=t.id,
                order_in_quiz=t.order_in_quiz,
                question=t.question,
                options=t.options
            ) for t in tests
        ]
    )


@app.post("/api/quizzes/submit", response_model=schemas.QuizSubmitResponse)
async def submit_quiz(
    payload: schemas.QuizSubmitRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Test topshirig'i (10 talik, 25 talik yoki 50 talik) javoblarini to'liq tekshirish,
    ball/XP hisoblash va natijaviy tahlilni qaytarish.
    """
    # Qaysi testlar to'plami ekanligini aniqlash
    if payload.quiz_type == "lesson":
        stmt = (
            select(models.Test)
            .where(models.Test.lesson_id == payload.lesson_id)
            .order_by(models.Test.order_in_quiz)
        )
        title = "Dars bo'yicha test topshirig'i (10 ta savol)"
        xp_per_correct = 5
    elif payload.quiz_type == "module":
        stmt = (
            select(models.Test)
            .where(models.Test.module_id == payload.module_id, models.Test.is_module_final == True)
            .order_by(models.Test.order_in_quiz)
        )
        title = "Modul yakuniy test topshirig'i (25 ta savol)"
        xp_per_correct = 6
    else:  # course_final
        stmt = (
            select(models.Test)
            .where(models.Test.is_course_final == True)
            .order_by(models.Test.order_in_quiz)
        )
        title = "Kurs Yakuniy Attestatsiyasi (50 ta savol)"
        xp_per_correct = 10

    res = await db.execute(stmt)
    tests = res.scalars().all()

    if not tests:
        raise HTTPException(status_code=404, detail="Test savollari topilmadi")

    total_questions = len(tests)
    correct_count = 0
    questions_review = []

    for t in tests:
        user_choice = payload.answers.get(str(t.id))
        is_correct = (user_choice is not None and user_choice == t.correct_option)
        if is_correct:
            correct_count += 1

        questions_review.append(schemas.QuestionReviewOut(
            id=t.id,
            order_in_quiz=t.order_in_quiz,
            question=t.question,
            options=t.options,
            selected_option=user_choice,
            correct_option=t.correct_option,
            is_correct=is_correct,
            explanation=t.explanation
        ))

    score_percentage = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    passed = score_percentage >= 60
    earned_xp = correct_count * xp_per_correct

    # Gamifikatsiya va XP ni yangilash
    current_user.xp += earned_xp
    new_level, new_status, _, _ = calculate_level_and_status(current_user.xp)
    current_user.level = new_level
    current_user.status_title = new_status

    # Nishon tekshirish
    unlocked_badge = await check_and_award_badges(
        current_user, db, action_type="quiz", score=score_percentage, quiz_type=payload.quiz_type
    )

    # Urinishni saqlash
    quiz_attempt = models.QuizAttempt(
        user_id=current_user.id,
        quiz_type=payload.quiz_type,
        lesson_id=payload.lesson_id,
        module_id=payload.module_id,
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=score_percentage,
        xp_earned=earned_xp,
        user_answers=payload.answers
    )
    db.add(quiz_attempt)

    await db.commit()
    await db.refresh(current_user)

    return schemas.QuizSubmitResponse(
        quiz_type=payload.quiz_type,
        title=title,
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=score_percentage,
        xp_earned=earned_xp,
        user_xp=current_user.xp,
        user_level=current_user.level,
        user_status=current_user.status_title,
        passed=passed,
        new_badge_unlocked=unlocked_badge,
        questions_review=questions_review
    )


# ==========================================
# 4. OPENROUTER API VA SI TEKSHIRUVI
# ==========================================

@app.post("/api/tasks/submit-open", response_model=schemas.SubmitOpenTaskResponse)
async def submit_open_task(
    payload: schemas.SubmitOpenTaskRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(models.Task).where(models.Task.id == payload.task_id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Topshiriq topilmadi")

    ai_evaluation = await evaluate_pedagogical_task(
        task_title=task.title,
        task_prompt=task.prompt,
        criteria=task.pedagogical_criteria,
        student_answer=payload.answer_text
    )

    score = ai_evaluation["score"]
    feedback = ai_evaluation["feedback"]
    strengths = ai_evaluation["strengths"]
    improvements = ai_evaluation["improvements"]
    components = ai_evaluation["pedagogical_components"]

    earned_xp = int((score / 100.0) * task.xp_reward)

    submission = models.Submission(
        user_id=current_user.id,
        task_id=task.id,
        answer_text=payload.answer_text,
        ai_score=score,
        ai_feedback=feedback,
        strengths=strengths,
        improvements=improvements,
        pedagogical_analysis=components,
        xp_earned=earned_xp
    )
    db.add(submission)

    current_user.xp += earned_xp
    new_level, new_status, _, _ = calculate_level_and_status(current_user.xp)
    current_user.level = new_level
    current_user.status_title = new_status

    unlocked_badge = await check_and_award_badges(
        current_user, db, action_type="open_task", score=score
    )

    await db.commit()
    await db.refresh(submission)
    await db.refresh(current_user)

    return schemas.SubmitOpenTaskResponse(
        submission_id=submission.id,
        score=score,
        feedback=feedback,
        strengths=strengths,
        improvements=improvements,
        pedagogical_components=components,
        xp_earned=earned_xp,
        user_xp=current_user.xp,
        user_level=current_user.level,
        user_status=current_user.status_title,
        new_badge_unlocked=unlocked_badge
    )


# ==========================================
# 5. GAMIFIKATSIYA VA NISHONLAR
# ==========================================

@app.get("/api/gamification/badges", response_model=List[schemas.BadgeOut])
async def get_badges(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    all_badges_res = await db.execute(select(models.Badge).order_by(models.Badge.min_xp))
    badges = all_badges_res.scalars().all()

    user_badges_res = await db.execute(
        select(models.UserBadge.badge_id).where(models.UserBadge.user_id == current_user.id)
    )
    unlocked_ids = set(user_badges_res.scalars().all())

    return [
        schemas.BadgeOut(
            id=b.id,
            code=b.code,
            title=b.title,
            description=b.description,
            icon=b.icon,
            unlocked=(b.id in unlocked_ids)
        )
        for b in badges
    ]


@app.get("/health")
async def health_check():
    return {"status": "ok"}


frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
