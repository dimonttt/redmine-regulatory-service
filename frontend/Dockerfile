FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Запускаем dev-сервер (для production лучше использовать сборку через Nginx)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]