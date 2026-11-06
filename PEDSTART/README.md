# PedStart — Bo'lajak pedagoglar uchun raqamli tayyorgarlik platformasi

> **Slogan:** "Bo'lajak pedagoglar uchun muvaffaqiyatli start va raqamli tayyorgarlik makoni."

Ushbu platforma bo'lajak boshlang'ich sinf o'qituvchilarining pedagogik tayyorgarligini M.B. Muxamadaliyeva va boshqa tadqiqotchilarning 4 ta asosiy komponenti (**Motivatsion**, **Kognitiv**, **Operatsion-faoliyatli**, **Refleksiv**) asosida rivojlantirish va Sun'iy Intellekt (OpenRouter API) yordamida baholashga mo'ljallangan.

---

## 🛠 Texnologik Stek
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 ORM, Pydantic v2, HTTPX.
- **Frontend:** Vue.js 3 (Composition API / `<script setup>`), Tailwind CSS, Pinia, Axios.
- **Ma'lumotlar bazasi:** **MySQL 8.0+** (aiomysql / pymysql drayveri, `utf8mb4` kodlash).
- **Sun'iy Intellekt:** OpenRouter API (`openai/gpt-4o-mini` yoki `anthropic/claude-3-haiku`).

---

## 🗄 1. MySQL Ma'lumotlar Bazasini Sozlash

### A) Avtomatik yaratish:
FastAPI backend ishga tushganda yoki `python seed.py` buyrug'i berilganda, agar `pedstart_db` bazasi mavjud bo'lmasa, uni **avtomatik** `utf8mb4_unicode_ci` kodi bilan yaratadi.

### B) Qo'lda yaratish (ixtiyoriy):
Agar MySQL terminali yoki phpMyAdmin orqali yaratmoqchi bo'lsangiz:
```sql
CREATE DATABASE pedstart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Yoki tayyor [`backend/schema.sql`](file:///d:/Antigravity/PEDSTART/backend/schema.sql) faylini phpMyAdmin yoki quyidagi buyruq orqali import qilishingiz mumkin:
```bash
mysql -u root -p < backend/schema.sql
```

### C) `.env` faylida ulanishni ko'rsatish:
`backend/.env` faylida MySQL parolingizni kiritasiz:
```env
DB_USER=root
DB_PASSWORD=sizning_parolingiz
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pedstart_db

DATABASE_URL=mysql+aiomysql://root:sizning_parolingiz@localhost:3306/pedstart_db?charset=utf8mb4
```

---

## 🚀 2. Backendni Ishga Tushirish (FastAPI + MySQL)

```bash
cd backend

# Virtual muhit (ixtiyoriy)
python -m venv venv
venv\Scripts\activate

# Kerakli kutubxonalarni o'rnatish:
pip install -r requirements.txt

# MySQL bazasiga boshlang'ich modullar va ma'lumotlarni yozish:
python seed.py

# FastAPI serverini ishga tushirish:
uvicorn main:app --reload --port 8000
```

Swagger API interfeysi: `http://127.0.0.1:8000/docs`

---

## 💻 3. Frontendni Ishga Tushirish (Vue.js 3 + Tailwind CSS)

```bash
cd frontend

# Paketlarni o'rnatish:
npm install

# Loyihani dev rejimda ishga tushirish:
npm run dev
```

Brauzerda: `http://localhost:5173`

---

## 🔑 Demo Foydalanuvchi
- **Login:** `talaba`
- **Parol:** `talaba123`
*(Yoki yangi login/parol kiritib, verifikatsiyasiz darhol ro'yxatdan o'tishingiz mumkin).*
