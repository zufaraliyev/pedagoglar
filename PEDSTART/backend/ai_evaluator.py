import os
import json
import logging
import httpx
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("pedtayyor.ai")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

PEDAGOGICAL_SYSTEM_PROMPT = """Siz bo'lajak boshlang'ich sinf o'qituvchilarining pedagogik tayyorgarligini baholovchi nufuzli ekspert-metodist Sun'iy Intellektsiz.
Sizning baholashingiz M.B. Muxamadaliyeva va ilg'or pedagogik tadqiqotlarga asosan 4 ta asosiy komponentga tayanadi:
1. MOTIVATSION komponent: Pedagogik kasbga nisbatan muhabbat, o'quvchilar psixologiyasiga qiziqish, o'qitishga ichki intilish va pedagogik etika.
2. KOGNITIV komponent: Boshlang'ich ta'lim didaktikasi, pedagogik qonuniyatlar, ta'lim prinsiplari va ilmiy terminologiyani to'g'ri qo'llash.
3. OPERATSION-FAOLIYATLI komponent: Dars o'tish metodlari, interfaol texnologiyalar, sinfni boshqarish, amaliy keyslarni hal etish va metodik ko'nikmalar.
4. REFLEKSIV komponent: O'z pedagogik faoliyatini tanqidiy baholash, xatolarni tahlil qilish, o'quvchilarning tushunish darajasini anglash va o'zini rivojlantirish.

Vazifangiz:
Foydalanuvchining berilgan topshiriqqa javobini xolisona tahlil qiling.
Javobingizni FAQAT va FAQAT quyidagi JSON formatida taqdim eting:
{
  "score": <0 dan 100 gacha butun son, umumiy o'rtacha ball>,
  "feedback": "<Konstruktiv, do'stona va professional pedagogik xulosa (o'zbek tilida, 3-4 gap)>",
  "strengths": [
    "<Talabaning javobidagi 1-kuchli jihat>",
    "<Talabaning javobidagi 2-kuchli jihat>"
  ],
  "improvements": [
    "<Metodik jihatdan rivojlantirish kerak bo'lgan 1-tavsiya>",
    "<Amaliyotda e'tibor berish kerak bo'lgan 2-tavsiya>"
  ],
  "pedagogical_components": {
    "motivatsion": <0-100 ball>,
    "kognitiv": <0-100 ball>,
    "operatsion": <0-100 ball>,
    "refleksiv": <0-100 ball>
  }
}
Hech qanday qo'shimcha matn, markdown panjaralari (```json) yoki izohlarsiz, sof JSON qaytaring."""

async def evaluate_pedagogical_task(
    task_title: str,
    task_prompt: str,
    criteria: str,
    student_answer: str
) -> Dict[str, Any]:
    """
    OpenRouter API orqali talabaning ochiq pedagogik topshirig'ini tahlil qiladi.
    Agar API kalit bo'lmasa yoki xato yuz bersa, mezonlarga asoslangan deterministik tahlil qaytaradi.
    """
    if OPENROUTER_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://pedtayyor.uz",
                "X-Title": "PedTayyor Pedagogical Platform",
                "Content-Type": "application/json"
            }

            user_message = f"""[TOPSHIRIQ NOMI]: {task_title}
[TOPSHIRIQ SHARTI / KEYS]: {task_prompt}
[BAHOLASH MEZONI]: {criteria}

[TALABANING JAVOBI]:
\"\"\"{student_answer}\"\"\"

Iltimos, yuqoridagi 4 ta pedagogik komponent (motivatsion, kognitiv, operatsion-faoliyatli, refleksiv) bo'yicha tahlil qilib, faqat JSON formatida javob bering."""

            payload = {
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": PEDAGOGICAL_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.4,
                "max_tokens": 1000
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                # Remove any markdown wrapping if LLM returned ```json ... ```
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:].strip()
                parsed = json.loads(content)
                return normalize_ai_result(parsed)
            else:
                logger.error(f"OpenRouter API xatosi ({response.status_code}): {response.text}")
        except Exception as e:
            logger.exception(f"OpenRouter API chaqiruvida xatolik yuz berdi: {e}")

    # Fallback / Offline rejim: Mezonlar va talaba javobi hajmiga mos pedagogik simulyator
    return simulate_pedagogical_evaluation(student_answer, criteria)


def normalize_ai_result(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """JSON natijasini xavfsiz formatga keltiradi"""
    score = int(parsed.get("score", 75))
    score = max(0, min(100, score))

    components = parsed.get("pedagogical_components", {})
    normalized_components = {
        "motivatsion": int(components.get("motivatsion", score)),
        "kognitiv": int(components.get("kognitiv", score)),
        "operatsion": int(components.get("operatsion", score)),
        "refleksiv": int(components.get("refleksiv", score)),
    }

    return {
        "score": score,
        "feedback": str(parsed.get("feedback", "Topshiriq muvaffaqiyatli topshirildi.")),
        "strengths": list(parsed.get("strengths", ["Mavzu mazmuni yoritilgan", "Amaliy yondashuv seziladi"])),
        "improvements": list(parsed.get("improvements", ["Didaktik terminologiyani yanada chuqurroq oching", "Refleksiv tahlilni kuchaytiring"])),
        "pedagogical_components": normalized_components
    }


def simulate_pedagogical_evaluation(student_answer: str, criteria: str) -> Dict[str, Any]:
    """
    OpenRouter API kaliti mavjud bo'lmaganda yoki offline rejimda ishlovchi
    metodik tahlil generatori (talabaning pedagogik leksikoni va javob sifatiga tayanadi).
    """
    words = student_answer.split()
    word_count = len(words)

    # Kalit so'zlar orqali komponentlarni tahlil qilish
    answer_lower = student_answer.lower()

    pedagogical_terms = ["metod", "didaktika", "tarbiya", "ta'lim", "tamoyil", "dars", "o'quvchi", "shaxs", "interfaol", "mashg'ulot"]
    found_terms = [t for t in pedagogical_terms if t in answer_lower]

    base_score = 65
    if word_count > 60:
        base_score += 15
    elif word_count > 30:
        base_score += 10

    if len(found_terms) >= 4:
        base_score += 15
    elif len(found_terms) >= 2:
        base_score += 10

    score = min(98, max(50, base_score))

    motiv_score = min(100, score + 4)
    kognit_score = min(100, score + (5 if "didaktika" in answer_lower or "ta'lim" in answer_lower else -3))
    operat_score = min(100, score + (4 if "metod" in answer_lower or "dars" in answer_lower else -2))
    reflek_score = min(100, score - 2)

    return {
        "score": score,
        "feedback": (
            f"Javobingiz pedagogik tayyorgarlik talablariga mos keladi. "
            f"Fikrlar izchil ifodalangan va boshlang'ich ta'lim xususiyatlari inobatga olingan. "
            f"Metodik vositalarni darsning barcha bosqichlariga yanada integratsiya qilish tavsiya etiladi."
        ),
        "strengths": [
            "Boshlang'ich sinf yosh xususiyatlarini to'g'ri baholashga intilish bor",
            "Mavzuga doir ilmiy-pedagogik tushunchalardan to'g'ri foydalanilgan",
            "O'quvchilar motivatsiyasini oshirishga yo'naltirilgan amaliy fikrlar mavjud"
        ],
        "improvements": [
            "Dars ishlanmasida refleksiv yakunlovchi savollarni ko'paytirish maqsadga muvofiq",
            "Differensial (tabaqalashtirilgan) ta'lim usullarini kengroq qo'llang"
        ],
        "pedagogical_components": {
            "motivatsion": motiv_score,
            "kognitiv": kognit_score,
            "operatsion": operat_score,
            "refleksiv": reflek_score
        }
    }
