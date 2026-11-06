FROM node:22-alpine AS frontend-build

WORKDIR /frontend
COPY PEDSTART/frontend/package.json PEDSTART/frontend/package-lock.json ./
RUN npm ci
COPY PEDSTART/frontend/ ./
RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend
COPY PEDSTART/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY PEDSTART/backend/ ./
COPY PEDSTART/DATA/ /app/DATA/
COPY --from=frontend-build /frontend/dist/ /app/frontend/dist/

EXPOSE 10000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
