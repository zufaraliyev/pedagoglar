import os
import json
import asyncio
import re
from pathlib import Path
import docx
from pptx import Presentation
from sqlalchemy import select, delete
from database import engine, AsyncSessionLocal, Base, ensure_mysql_database_exists
import models

DATA_DIR = Path(__file__).resolve().parent.parent / "DATA"

def clean_uz_text(text):
    if not text:
        return ""
    text = text.replace('\ufffd', "'")
    text = text.replace('‘', "'").replace('’', "'").replace('`', "'").replace('ʻ', "'").replace('ʼ', "'")
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def load_lecture_content(num):
    lecture_files = {
        1: "1-ma'ruza.docx",
        2: "2-mavzu.docx",
        3: "3-mavzu.docx",
        4: "4.1-mavzu.docx",
        5: "5-mavzu.docx",
        6: "6-mavzu.docx",
        7: "7-mavzu.docx",
        8: "Pedagogika, 8-ma'ruza.pptx",
        9: "9-mavzu.docx",
        10: "10-mavzu.docx",
        11: "11-mavzu.docx",
        12: "12-mavzu.docx",
        13: "13-mavzu.docx",
        14: "14-dars.docx",
        15: "15-mavzu.docx",
    }
    fname = lecture_files.get(num)
    if not fname:
        return ""
    fpath = os.path.join(DATA_DIR, fname)
    if not os.path.exists(fpath):
        return ""

    if fname.endswith('.docx'):
        doc = docx.Document(fpath)
        pars = [clean_uz_text(p.text) for p in doc.paragraphs if clean_uz_text(p.text)]
        return "\n\n".join(pars[:45])  # Eng muhim 40-50 ta paragrafni ixcham maqola formatida saqlaymiz
    elif fname.endswith('.pptx'):
        prs = Presentation(fpath)
        texts = []
        for slide in prs.slides:
            slide_texts = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    t = clean_uz_text(shape.text_frame.text)
                    if t:
                        slide_texts.append(t)
            if slide_texts:
                texts.append("\n".join(slide_texts))
        return "\n\n---\n\n".join(texts)

# 15 ta Ma'ruza va 15 ta Amaliyot darslari ma'lumotlari
LESSONS_INFO = [
    # 1-MODUL: Kognitiv komponent (1 - 4)
    {
        "module_order": 1,
        "lecture_num": 1,
        "lecture_title": "1-Ma'ruza: Boshlang'ich ta'lim pedagogikasi fanining mazmuni, predmeti va ilmiy-tadqiqot metodlari",
        "lecture_video": "xBIzptn-30I",
        "practice_title": "1-Amaliyot: Ilmiy-tadqiqot metodlarini qo'llash va pedagogik kuzatuv kundaligini yuritish",
        "practice_video": "xBIzptn-30I",
        "practice_task": "Boshlang'ich 2-sinf darsida o'quvchilarning bilish faolligi va diqqatini o'rganish bo'yicha pedagogik kuzatuv rejasini tuzing. Qanday mezonlar asosida kognitiv qiziqishni qayd etasiz? (100-150 so'z)",
    },
    {
        "module_order": 1,
        "lecture_num": 2,
        "lecture_title": "2-Ma'ruza: Boshlang'ich maktabda pedagogik jarayonning zamonaviy tendensiyalari",
        "lecture_video": "PDLXPWO98LM",
        "practice_title": "2-Amaliyot: Zamonaviy dars tahlili va pedagogik tendensiyalar xaritasini shakllantirish",
        "practice_video": "PDLXPWO98LM",
        "practice_task": "Zamonaviy darsda an'anaviy ta'limdan farqli ravishda o'quvchi subyekt sifatida qanday faoliyat ko'rsatishi kerak? O'zingiz tanlagan bitta boshlang'ich fan misolida tushuntiring.",
    },
    {
        "module_order": 1,
        "lecture_num": 3,
        "lecture_title": "3-Ma'ruza: An'anaviy va innovatsion ta'limning qiyosiy tahlili",
        "lecture_video": "XTaN9jt_AFo",
        "practice_title": "3-Amaliyot: 'Venn diagrammasi' vositasida an'anaviy va innovatsion ta'lim modellarini qiyoslash",
        "practice_video": "XTaN9jt_AFo",
        "practice_task": "An'anaviy va innovatsion ta'limning 3 tadan kuchli va zaif tomonlarini M.B. Muxamadaliyeva konsepsiyasidagi kognitiv va operatsion mezonlar asosida solishtirib yozing.",
    },
    {
        "module_order": 1,
        "lecture_num": 4,
        "lecture_title": "4-Ma'ruza: Boshlang'ich ta'lim fanlarini o'qitishda innovatsion yondashuv",
        "lecture_video": "Vcn6Y1tw1-M",
        "practice_title": "4-Amaliyot: 1-4-sinflar uchun innovatsion kirish bosqichi dars ishlanmasini tuzish",
        "practice_video": "Vcn6Y1tw1-M",
        "practice_task": "O'quvchilarda yangi mavzuga qiziqish uyg'otuvchi muammoli vaziyat yoki kutilmagan savol (Muammoli ta'lim metodi) orqali darsni boshlash ssenariysini yozing.",
    },

    # 2-MODUL: Operatsion-faoliyatli komponent (5 - 8)
    {
        "module_order": 2,
        "lecture_num": 5,
        "lecture_title": "5-Ma'ruza: Hozirgi davrda jahon mamlakatlari masofaviy ta'lim tizimi",
        "lecture_video": "LTXMBF7yBy0",
        "practice_title": "5-Amaliyot: Masofaviy va raqamli ta'lim platformalari (LMS, interfaol ilovalar) bilan ishlash",
        "practice_video": "LTXMBF7yBy0",
        "practice_task": "Boshlang'ich sinf o'quvchilari uchun masofaviy ta'limda qiziqarli mustaqil ta'lim topshirig'i (masalan, multimedia va viktorina vositasida) loyihasini ishlab chiqing.",
    },
    {
        "module_order": 2,
        "lecture_num": 6,
        "lecture_title": "6-Ma'ruza: Boshlang'ich ta'lim fanlarini o'qitishda zamonaviy pedagogik texnologiyalar",
        "lecture_video": "5jRaSgMIPmw",
        "practice_title": "6-Amaliyot: 'Aqliy hujum', 'Klaster' va 'Insert' metodlari asosida dars ishlanmasi",
        "practice_video": "5jRaSgMIPmw",
        "practice_task": "Ona tili yoki Tabiiy fanlar darsida 'Klaster' usulidan foydalanib o'quvchilarni guruhda ishlashga undovchi 15 daqiqalik bosqich rejasini tuzing.",
    },
    {
        "module_order": 2,
        "lecture_num": 7,
        "lecture_title": "7-Ma'ruza: Innovatsiyalarni ta'lim jarayoniga tatbiq etish mexanizmlari",
        "lecture_video": "5jRaSgMIPmw",
        "practice_title": "7-Amaliyot: Ta'limiy loyihalash (Project-based learning) texnologiyasi asosida dars loyihasi",
        "practice_video": "5jRaSgMIPmw",
        "practice_task": "3-sinf o'quvchilari uchun 'Tabiatni asraymiz' mavzusida 1 haftalik kichik ta'limiy loyiha ssenariysi va baholash mezonlarini yozing.",
    },
    {
        "module_order": 2,
        "lecture_num": 8,
        "lecture_title": "8-Ma'ruza: Bolalar jamoasida tarbiya va yagona pedagogik jarayon",
        "lecture_video": "2G2ODT_fFM0",
        "practice_title": "8-Amaliyot: Boshlang'ich sinfda jamoaviy hamkorlik va sog'lom psixologik muhit mashqlari",
        "practice_video": "2G2ODT_fFM0",
        "practice_task": "Sinfda yangi kelgan va jamoaga qo'shilishga qiynalayotgan o'quvchini jamoaga moslashtirish (ijtimoiy adaptatsiya) bo'yicha pedagogik yechimingizni bayon eting.",
    },

    # 3-MODUL: Motivatsion komponent (9 - 12)
    {
        "module_order": 3,
        "lecture_num": 9,
        "lecture_title": "9-Ma'ruza: Boshlang'ich maktabda innovatsiya va integratsiyaning o'zaro aloqadorligi",
        "lecture_video": "xBIzptn-30I",
        "practice_title": "9-Amaliyot: Integratsiyalashgan ta'limiy maqsadlar va motivatsiyani rejalashtirish",
        "practice_video": "xBIzptn-30I",
        "practice_task": "Fanlararo integratsiya qanday qilib o'quvchining darsga bo'lgan ichki motivatsiyasini oshiradi? Aniq bitta misol keltiring.",
    },
    {
        "module_order": 3,
        "lecture_num": 10,
        "lecture_title": "10-Ma'ruza: Integratsiya — ta'limning muhim didaktik prinsipi",
        "lecture_video": "Vcn6Y1tw1-M",
        "practice_title": "10-Amaliyot: Ona tili va O'qish savodxonligi darslarini integratsiyalash keysi",
        "practice_video": "Vcn6Y1tw1-M",
        "practice_task": "Matn ustida ishlash jarayonida ham imlo qoidalarini, ham adabiy tahlil ko'nikmalarini birlashtiruvchi amaliy topshiriq tuzing.",
    },
    {
        "module_order": 3,
        "lecture_num": 11,
        "lecture_title": "11-Ma'ruza: Boshlang'ich maktabda integratsiyalashgan ta'limdan foydalanish metodikasi",
        "lecture_video": "PDLXPWO98LM",
        "practice_title": "11-Amaliyot: Matematika va Tabiiy fanlar (Science) fanlararo bog'lanishli amaliy dars ishlanmasi",
        "practice_video": "PDLXPWO98LM",
        "practice_task": "Matematik hisob-kitoblar (qo'shish, ayirish, foiz)ni tabiiy fanlardagi tajribalar bilan bog'lovchi 1 ta amaliy topshiriq ishlab chiqing.",
    },
    {
        "module_order": 3,
        "lecture_num": 12,
        "lecture_title": "12-Ma'ruza: Boshlang'ich sinf darslarini integratsiyalash texnologiyasi",
        "lecture_video": "5jRaSgMIPmw",
        "practice_title": "12-Amaliyot: 'Mavzuli kun' (Thematic day) formatida integratsiyalashgan mashg'ulot modellashtirish",
        "practice_video": "5jRaSgMIPmw",
        "practice_task": "Masalan 'Oltin kuz' mavzusida kun davomidagi 3 ta dars (Ona tili, Matematika, Tasviriy san'at)ning o'zaro integratsiyalashgan dars ssenariysini yozing.",
    },

    # 4-MODUL: Refleksiv komponent (13 - 15)
    {
        "module_order": 4,
        "lecture_num": 13,
        "lecture_title": "13-Ma'ruza: Maktab va oila integratsiyasi hamda hamkorlik pedagogikasi",
        "lecture_video": "0gAb9YZAIec",
        "practice_title": "13-Amaliyot: Ota-onalar bilan interfaol muloqot va hamkorlikdagi loyiha rejasini ishlab chiqish",
        "practice_video": "0gAb9YZAIec",
        "practice_task": "Ota-onalar va o'quvchilar birgalikda bajaradigan oilaviy kitobxonlik yoki ijodiy tadbir konsepsiyasini ishlab chiqing.",
    },
    {
        "module_order": 4,
        "lecture_num": 14,
        "lecture_title": "14-Ma'ruza: Innovatsion ta'lim muhitida o'qituvchining kreativligi va pedagogik mahorati",
        "lecture_video": "2G2ODT_fFM0",
        "practice_title": "14-Amaliyot: Pedagogik vaziyatlar (keys-stadi)ni tahlil qilish va refleksiv o'z-o'zini baholash",
        "practice_video": "2G2ODT_fFM0",
        "practice_task": "Dars jarayonida reja bo'yicha ketmagan va kutilmagan vaziyat yuz berganda o'qituvchining kreativ refleksiv javob berish algoritmini yozing.",
    },
    {
        "module_order": 4,
        "lecture_num": 15,
        "lecture_title": "15-Ma'ruza: Markaziy Osiyo va MDH davlatlarida integratsiyalashgan ta'lim tajribalari",
        "lecture_video": "LTXMBF7yBy0",
        "practice_title": "15-Amaliyot: Xalqaro tajribalarni qiyosiy o'rganish va shaxsiy kasbiy rivojlanish traektoriyasini tuzish",
        "practice_video": "LTXMBF7yBy0",
        "practice_task": "Boshlang'ich ta'lim bo'yicha ilg'or xorijiy tajribalardan qaysi birini O'zbekiston umumta'lim maktablarida samarali joriy etish mumkin deb hisoblaysiz? Tahlil qiling.",
    },
]

MODULES_CONFIG = [
    {
        "order": 1,
        "title": "1-Modul: Boshlang'ich ta'lim pedagogikasi asoslari va metodologiyasi",
        "description": "Boshlang'ich ta'lim pedagogikasining maqsadi, vazifalari, ilmiy-tadqiqot metodlari, zamonaviy tendensiyalari va innovatsion yondashuvlar.",
        "component": "kognitiv",
        "xp_reward": 250,
        "final_task_title": "1-Modul Yakuniy Topshirig'i: Kognitiv kompetensiyani shakllantirish modeli",
        "final_task_prompt": "1-Modul bo'yicha o'rganilgan bilimlar asosida boshlang'ich sinf o'qituvchisining kognitiv tayyorgarlik darajasi dars sifatiga qanday ta'sir ko'rsatishini ilmiy asoslab bering."
    },
    {
        "order": 2,
        "title": "2-Modul: Didaktika, loyihalash texnologiyasi va zamonaviy metodlar",
        "description": "Masofaviy ta'lim tizimi, interfaol metodlar (Aqliy hujum, Klaster), loyihalash texnologiyasi va bolalar jamoasida tarbiyaviy jarayon.",
        "component": "operatsion-faoliyatli",
        "xp_reward": 250,
        "final_task_title": "2-Modul Yakuniy Topshirig'i: Innovatsion dars texnologiyasi loyihasi",
        "final_task_prompt": "Didaktik prinsiplar va interfaol metodlar uyg'unligida boshlang'ich sinf uchun 45 daqiqalik darsning to'liq texnologik xaritasini shakllantiring."
    },
    {
        "order": 3,
        "title": "3-Modul: Fanlararo integratsiya va o'quvchilar motivatsiyasi",
        "description": "Integratsiya tamoyili, boshlang'ich sinf darslarini o'zaro bog'lash metodikasi, mavzuli kunlar va o'quvchilar bilish motivatsiyasi.",
        "component": "motivatsion",
        "xp_reward": 250,
        "final_task_title": "3-Modul Yakuniy Topshirig'i: Integratsiyalashgan ta'limiy dastur konsepsiyasi",
        "final_task_prompt": "Boshlang'ich ta'limda integratsiyalashgan darslarning o'quvchilar dunyoqarashini kengaytirishdagi o'rnini pedagogik tahlil qiling."
    },
    {
        "order": 4,
        "title": "4-Modul: Pedagogik mahorat, maktab-oila integratsiyasi va refleksiv tahlil",
        "description": "Oila va maktab hamkorligi, o'qituvchining kreativligi, xalqaro ta'limiy tajribalar hamda kasbiy faoliyat refleksiyasi.",
        "component": "refleksiv",
        "xp_reward": 250,
        "final_task_title": "4-Modul Yakuniy Topshirig'i: Bo'lajak o'qituvchining kasbiy mahorat va refleksiv xaritasi",
        "final_task_prompt": "M.B. Muxamadaliyeva konsepsiyasidagi barcha 4 ta komponent (motivatsion, kognitiv, operatsion, refleksiv) bo'yicha o'z kasbiy portretingizni loyihalashtiring."
    }
]

async def seed_full_database():
    ensure_mysql_database_exists()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        existing_module = await db.scalar(select(models.Module.id).limit(1))
        if existing_module is not None:
            print("Boshlang'ich ma'lumotlar mavjud; foydalanuvchi ma'lumotlari saqlandi.")
            return

    # 300 ta testni o'qish
    tests_file = os.path.join(os.path.dirname(__file__), "all_tests.json")
    with open(tests_file, "r", encoding="utf-8") as f:
        all_questions = json.load(f)

    print(f"Barcha yuklangan testlar: {len(all_questions)} ta")

    async with AsyncSessionLocal() as db:
        print("Mavjud eski ma'lumotlar tozalanmoqda...")
        await db.execute(delete(models.TestAttempt))
        await db.execute(delete(models.QuizAttempt))
        await db.execute(delete(models.Test))
        await db.execute(delete(models.Submission))
        await db.execute(delete(models.Task))
        await db.execute(delete(models.Lesson))
        await db.execute(delete(models.Module))
        await db.execute(delete(models.UserBadge))
        await db.execute(delete(models.Badge))

        # 1. Badges
        badges = [
            models.Badge(code="first_step", title="Birinchi Qadam", description="Ilk dars testi yoki topshiriqni bajarganlik uchun", icon="🌱", min_xp=10),
            models.Badge(code="quiz_master_10", title="Dars Testi A'lochisi", description="10 talik dars testida 90%+ natija ko'rsatganlik uchun", icon="🎯", min_xp=50),
            models.Badge(code="reflective_master", title="Refleksiv Tahlilchi", description="Ochiq pedagogik topshiriqda Sun'iy Intellektdan 85+ ball olganlik uchun", icon="💡", min_xp=100),
            models.Badge(code="module_champion_25", title="Modul Chempioni", description="Modul yakuniy 25 talik testini a'lo bahoga topshirganlik uchun", icon="🏅", min_xp=300),
            models.Badge(code="course_graduate_50", title="Kurs Bitiruvchisi (50/50)", description="50 talik Katta Attestatsiya Testini muvaffaqiyatli topshirganlik uchun", icon="🏆", min_xp=700),
        ]
        db.add_all(badges)
        await db.flush()

        # 2. Modullar va 15 ta Ma'ruza + 15 ta Amaliyot darslari
        module_instances = {}
        for m_cfg in MODULES_CONFIG:
            m = models.Module(
                order=m_cfg["order"],
                title=m_cfg["title"],
                description=m_cfg["description"],
                pedagogical_component=m_cfg["component"],
                xp_reward=m_cfg["xp_reward"]
            )
            db.add(m)
            await db.flush()
            module_instances[m_cfg["order"]] = m

        q_idx = 0
        total_lessons_count = 0

        for info in LESSONS_INFO:
            mod = module_instances[info["module_order"]]
            
            # --- A. MA'RUZA (Lecture) ---
            lecture_text = load_lecture_content(info["lecture_num"])
            if not lecture_text:
                lecture_text = f"Mazkur dars boshlang'ich ta'lim pedagogikasining eng muhim yo'nalishlaridan birini o'rganishga bag'ishlangan. Mazmun M.B. Muxamadaliyeva tomonidan ilgari surilgan pedagogik tayyorgarlik mezonlariga mos keladi."

            lecture = models.Lesson(
                module_id=mod.id,
                order=(info["lecture_num"] * 2) - 1,
                title=info["lecture_title"],
                lesson_type="lecture",
                video_url=info["lecture_video"],
                reading_time_minutes=15,
                xp_reward=25,
                content=lecture_text
            )
            db.add(lecture)
            await db.flush()
            total_lessons_count += 1

            # Ma'ruza uchun 10 TA TEST
            lecture_tests = []
            for i in range(10):
                q = all_questions[q_idx % len(all_questions)]
                q_idx += 1
                lecture_tests.append(models.Test(
                    module_id=mod.id,
                    lesson_id=lecture.id,
                    quiz_type="lesson",
                    order_in_quiz=i + 1,
                    question=q["question"],
                    options=q["options"],
                    correct_option=q["correct_option"],
                    explanation=q.get("explanation", "Boshlang'ich ta'lim nazariyasi va metodikasi talablari asosidagi to'g'ri javob."),
                    is_module_final=False,
                    is_course_final=False,
                    xp_reward=5
                ))
            db.add_all(lecture_tests)

            # Ma'ruza uchun SI Ochiq Topshirig'i
            db.add(models.Task(
                module_id=mod.id,
                lesson_id=lecture.id,
                title=f"{info['lecture_num']}-Mavzu SI Topshirig'i: Nazariy tahlil va pedagogik asos",
                prompt=f"Mavzu: {info['lecture_title']}.\nUshbu mavzuning boshlang'ich sinf ta'lim jarayonidagi ahamiyatini M.B. Muxamadaliyeva konsepsiyasidagi 4 ta komponent (motivatsion, kognitiv, operatsion, refleksiv) nuqtai nazaridan qisqacha tahlil qiling. (100-150 so'z)",
                pedagogical_criteria="Motivatsion (qiziqish), Kognitiv (ilmiy asos), Operatsion (amaliy usul) va Refleksiv (o'zini tahlil qilish).",
                is_module_final=False,
                max_score=100,
                xp_reward=50
            ))

            # --- B. AMALIYOT (Practice) ---
            practice_text = f"""# {info['practice_title'].upper()}

### 🎯 Mashg'ulotning asosiy maqsadi:
Nazariy bilimlarni bevosita sinf amaliyotida, simulyatsion dars bosqichlari va pedagogik keyslar orqali qo'llash ko'nikmalarini shakllantirish.

### 📋 Amaliy ish bosqichlari:
1. **Didaktik maqsadni belgilash:** Boshlang'ich sinf o'quvchilarining yosh xususiyatlariga mos vazifalar tanlash.
2. **Interfaol metodlarni qo'llash:** Mavzuga mos klaster, aqliy hujum, keys-stadi yoki loyiha metodini dars bosqichlariga kiritish.
3. **Refleksiv tahlil:** Dars yakunida o'quvchilarning o'zlashtirish darajasini va o'qituvchining o'z faoliyatini xolisona baholash.

### 💡 Metodik ko'rsatma:
Ushbu amaliy mashg'ulot M.B. Muxamadaliyeva tomonidan ishlab chiqilgan **operatsion-faoliyatli** va **refleksiv** komponentlarni rivojlantirishga qaratilgan bo'lib, bo'lajak o'qituvchining darsni mustaqil loyihalay olish mahoratini oshiradi.
"""
            practice = models.Lesson(
                module_id=mod.id,
                order=(info["lecture_num"] * 2),
                title=info["practice_title"],
                lesson_type="practice",
                video_url=info["practice_video"],
                reading_time_minutes=20,
                xp_reward=35,
                content=practice_text
            )
            db.add(practice)
            await db.flush()
            total_lessons_count += 1

            # Amaliyot uchun 10 TA TEST
            practice_tests = []
            for i in range(10):
                q = all_questions[q_idx % len(all_questions)]
                q_idx += 1
                practice_tests.append(models.Test(
                    module_id=mod.id,
                    lesson_id=practice.id,
                    quiz_type="lesson",
                    order_in_quiz=i + 1,
                    question=q["question"],
                    options=q["options"],
                    correct_option=q["correct_option"],
                    explanation=q.get("explanation", "Boshlang'ich ta'lim amaliy metodikasi talablari asosida to'g'ri yechim."),
                    is_module_final=False,
                    is_course_final=False,
                    xp_reward=5
                ))
            db.add_all(practice_tests)

            # Amaliyot uchun SI Ochiq Topshirig'i
            db.add(models.Task(
                module_id=mod.id,
                lesson_id=practice.id,
                title=f"{info['lecture_num']}-Amaliyot SI Topshirig'i: Keys va amaliy yechim",
                prompt=info["practice_task"],
                pedagogical_criteria="Aniq dars bosqichlari, pedagogik usulning to'g'ri tanlanganligi, o'quvchi faolligini ta'minlash.",
                is_module_final=False,
                max_score=100,
                xp_reward=60
            ))

        # 4. Modullar Yakuniy 25 TALIK TESTLARI VA YAKUNIY TOPSHIRIQLAR
        for m_cfg in MODULES_CONFIG:
            mod = module_instances[m_cfg["order"]]
            module_final_tests = []
            for i in range(25):
                q = all_questions[q_idx % len(all_questions)]
                q_idx += 1
                module_final_tests.append(models.Test(
                    module_id=mod.id,
                    lesson_id=None,
                    quiz_type="module",
                    order_in_quiz=i + 1,
                    question=q["question"],
                    options=q["options"],
                    correct_option=q["correct_option"],
                    explanation=q.get("explanation", f"{mod.title} bo'yicha yakuniy nazorat mezoniga mos."),
                    is_module_final=True,
                    is_course_final=False,
                    xp_reward=6
                ))
            db.add_all(module_final_tests)

            # Modul Yakuniy SI Topshirig'i
            db.add(models.Task(
                module_id=mod.id,
                lesson_id=None,
                title=m_cfg["final_task_title"],
                prompt=m_cfg["final_task_prompt"],
                pedagogical_criteria="Barcha 4 ta komponent (motivatsion, kognitiv, operatsion, refleksiv) to'liq yoritilganligi va shaxsiy pedagogik yondashuv.",
                is_module_final=True,
                max_score=100,
                xp_reward=80
            ))

        # 5. KURS YAKUNIY KATTA ATTESTATSIYA TESTI (50 TA TEST)
        course_final_tests = []
        for i in range(50):
            q = all_questions[q_idx % len(all_questions)]
            q_idx += 1
            course_final_tests.append(models.Test(
                module_id=None,
                lesson_id=None,
                quiz_type="course_final",
                order_in_quiz=i + 1,
                question=q["question"],
                options=q["options"],
                correct_option=q["correct_option"],
                explanation=q.get("explanation", "Boshlang'ich ta'lim pedagogikasi kursi bo'yicha davlat attestatsiya standarti javobi."),
                is_module_final=False,
                is_course_final=True,
                xp_reward=10
            ))
        db.add_all(course_final_tests)

        await db.commit()

        print("=== BAZA MUVAFFAQIYATLI TO'LDIRILDI! ===")
        print(f"Jami modullar: {len(MODULES_CONFIG)} ta")
        print(f"Jami darslar (15 ma'ruza + 15 amaliyot): {total_lessons_count} ta dars")
        print(f"Har bir darsda 10 ta test: {total_lessons_count * 10} ta test")
        print(f"Har bir modul yakunida 25 ta test: {4 * 25} ta test")
        print(f"Kurs yakuniy attestatsiyasida: 50 ta test")
        print(f"Bazada jami saqlangan testlar: {total_lessons_count * 10 + 100 + 50} ta test!")

if __name__ == "__main__":
    asyncio.run(seed_full_database())
