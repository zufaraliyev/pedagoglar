# Pedagoglar

Bo'lajak pedagoglar uchun raqamli tayyorgarlik platformasi.

## Loyihani tarkibi
- `PEDSTART/` - asosiy loyiha kodi
- `pedstart_db.sql` - ma'lumotlar bazasi fayli

## Texnologiyalar
- Python + FastAPI
- Vue 3 + Vite + Tailwind
- MySQL
- OpenRouter AI

## Ishga tushirish
1. `cd PEDSTART/backend`
2. `pip install -r requirements.txt`
3. `python seed.py`
4. `uvicorn main:app --reload --port 8000`
5. `cd ../frontend && npm install && npm run dev`

## Maqsad
Bo'lajak boshlang'ich sinf o'qituvchilarining pedagogik tayyorgarligini rivojlantirish va AI yordamida baholash.
