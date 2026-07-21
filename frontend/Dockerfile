# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

# Production stage using Nginx
FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf

# 🟢 FIX: Vite outputs compiled files to 'dist', not 'build'
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]