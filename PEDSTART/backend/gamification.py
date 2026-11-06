from typing import Tuple, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models

LEVEL_THRESHOLDS = [
    (1, 0, 200, "Pedagog-izlanuvchi"),
    (2, 201, 500, "Metodist-amaliyotchi"),
    (3, 501, 1000, "Innovator-pedagog"),
    (4, 1001, 2000, "Etakchi murabbiy"),
    (5, 2001, float('inf'), "Mahoratli Ustoz"),
]

def calculate_level_and_status(xp: int) -> Tuple[int, str, int, int]:
    """
    XP asosida foydalanuvchi darajasi (level), unvoni (status),
    keyingi darajaga kerak bo'lgan ball va progress foizini hisoblaydi.
    """
    for level, min_xp, max_xp, status_title in LEVEL_THRESHOLDS:
        if xp <= max_xp:
            next_xp = int(max_xp) if max_xp != float('inf') else xp
            current_range_min = min_xp if min_xp > 0 else 0
            range_span = (max_xp - current_range_min) if max_xp != float('inf') else 1000
            progress_pct = min(100, max(0, int(((xp - current_range_min) / range_span) * 100)))
            return level, status_title, next_xp, progress_pct

    return 5, "Mahoratli Ustoz", 2001, 100

async def check_and_award_badges(
    user: models.User,
    db: AsyncSession,
    action_type: str = "open_task",
    score: int = 0,
    quiz_type: Optional[str] = None
) -> Optional[str]:
    """
    Foydalanuvchi erishgan natijalarga qarab nishonlar beradi va
    agar yangi nishon ochilsa, uning nomini qaytaradi.
    """
    stmt = select(models.UserBadge.badge_id).where(models.UserBadge.user_id == user.id)
    result = await db.execute(stmt)
    unlocked_badge_ids = set(result.scalars().all())

    all_badges_stmt = select(models.Badge)
    badges_res = await db.execute(all_badges_stmt)
    all_badges = badges_res.scalars().all()
    badge_map = {b.code: b for b in all_badges}

    new_badge_title = None

    # 1. "Birinchi qadam" nishoni
    if "first_step" in badge_map and badge_map["first_step"].id not in unlocked_badge_ids:
        badge = badge_map["first_step"]
        user_badge = models.UserBadge(user_id=user.id, badge_id=badge.id)
        db.add(user_badge)
        unlocked_badge_ids.add(badge.id)
        new_badge_title = badge.title

    # 2. "Dars Testi A'lochisi" (10 talik testda 90%+ ball)
    if action_type == "quiz" and quiz_type == "lesson" and score >= 90:
        if "quiz_master_10" in badge_map and badge_map["quiz_master_10"].id not in unlocked_badge_ids:
            badge = badge_map["quiz_master_10"]
            user_badge = models.UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            unlocked_badge_ids.add(badge.id)
            new_badge_title = badge.title

    # 3. "Modul Chempioni" (25 talik modul testida 80%+ ball)
    if action_type == "quiz" and quiz_type == "module" and score >= 80:
        if "module_champion_25" in badge_map and badge_map["module_champion_25"].id not in unlocked_badge_ids:
            badge = badge_map["module_champion_25"]
            user_badge = models.UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            unlocked_badge_ids.add(badge.id)
            new_badge_title = badge.title

    # 4. "Kurs Bitiruvchisi" (50 talik Kurs Yakuniy testida 75%+ ball)
    if action_type == "quiz" and quiz_type == "course_final" and score >= 75:
        if "course_graduate_50" in badge_map and badge_map["course_graduate_50"].id not in unlocked_badge_ids:
            badge = badge_map["course_graduate_50"]
            user_badge = models.UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            unlocked_badge_ids.add(badge.id)
            new_badge_title = badge.title

    # 5. "Refleksiv Tahlilchi" nishoni (Ochiq topshiriqda 80+ ball)
    if action_type == "open_task" and score >= 80:
        if "reflective_master" in badge_map and badge_map["reflective_master"].id not in unlocked_badge_ids:
            badge = badge_map["reflective_master"]
            user_badge = models.UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            unlocked_badge_ids.add(badge.id)
            new_badge_title = badge.title

    return new_badge_title
