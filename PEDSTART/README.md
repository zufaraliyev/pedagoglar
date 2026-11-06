# PedStart

Bo'lajak boshlang'ich sinf o'qituvchilari uchun darslar, testlar, gamifikatsiya va AI yordamida baholash platformasi.

## Deploy arxitekturasi

- **Render**: bitta bepul Docker web service; FastAPI API va Vue frontend shu servisda ishlaydi.
- **Neon**: PostgreSQL ma'lumotlar bazasi uchun bepul reja.
- **OpenRouter**: ixtiyoriy. Kalit berilmasa ochiq topshiriqlar ichki baholash usuli bilan ishlaydi.

Frontend va API bir domen ostida beriladi. Vue ilovasi `/api` manzillaridan foydalanadi, shuning uchun productionda lokal proxy yoki alohida frontend API manzili kerak emas.

## Internetga joylash

1. Repositoriyani GitHub'ga push qiling.
2. [Neon](https://neon.tech) da bepul PostgreSQL loyihasi yarating. Connection stringni pooled connection string sifatida oling; unda `sslmode=require` bo'lishi kerak.
3. [Render](https://render.com) akkauntida GitHub repositoriyasidan **Blueprint** yarating va `zufaraliyev/pedagoglar` repositoriyasini tanlang.
4. Blueprint `DATABASE_URL` so'raganda Neon connection stringini kiriting. `SECRET_KEY` Render tomonidan avtomatik yaratiladi.
5. Deploy tugagach, Render bergan `https://...onrender.com` manzilini oching. `/health` endpointi `{ "status": "ok" }` qaytarishi kerak.

Render Blueprint konfiguratsiyasi repozitoriya ildizidagi [`render.yaml`](../render.yaml) faylida, Docker build esa [`Dockerfile`](../Dockerfile) faylida.

### Bepul reja cheklovlari

Render bepul web service faol bo'lmaganda uxlaydi, shu sababli uzoq tanaffusdan keyingi birinchi ochilish sekinroq bo'lishi mumkin. Neon bepul bazasining limitlari va bepul tariflar vaqt o'tishi bilan o'zgarishi mumkin. Ishga tushirish uchun OpenRouter API kaliti shart emas.

## Foydalanuvchi va ma'lumotlar

- Demo parol bilan umumiy hisob yaratilmaydi; foydalanuvchi saytda ro'yxatdan o'tadi.
- Kurs ma'lumotlari faqat bo'sh bazaga birinchi ishga tushganda qo'shiladi.
- Keyingi deploy/restartlarda talaba hisoblari va natijalari qayta o'chirilmaydi.
- Dars matnlari `DATA/` dagi mavjud `.docx` va `.pptx` fayllardan olinadi; fayl yo'q bo'lsa, dars uchun o'rnatilgan zaxira matn ishlatiladi.
