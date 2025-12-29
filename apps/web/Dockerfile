FROM node:20-slim

WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json* /app/
RUN npm install
COPY apps/web /app

EXPOSE 5173
CMD ["sh", "-c", "export PATH=/app/node_modules/.bin:$PATH && vite --host 0.0.0.0"]
