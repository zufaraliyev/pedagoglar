# PedTayyor — bo'lajak pedagoglar uchun raqamli tayyorgarlik platformasi

PedTayyor darslar, testlar, o'quv natijalari va AI yordamida ochiq topshiriqlarni baholashni birlashtiradi.

## Internetga joylash

Frontend va backend bitta Render Docker servisida, ma'lumotlar Neon PostgreSQL'da ishlaydi.

Bepul deploy bo'yicha bosqichma-bosqich yo'riqnoma: [PEDSTART/README.md](PEDSTART/README.md).

## Tuzilishi

- `PEDSTART/backend/` — FastAPI, SQLAlchemy va PostgreSQL/MySQL ulanishi
- `PEDSTART/frontend/` — Vue 3 va Vite
- `PEDSTART/DATA/` — kurs uchun manba hujjatlar
- `Dockerfile`, `render.yaml` — Render deploy konfiguratsiyasi
