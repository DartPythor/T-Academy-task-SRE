FROM node:22-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --no-cache

COPY . .
RUN npm run build

FROM nginx:stable-alpine

# nginx.conf — шаблон: официальный entrypoint nginx рендерит его через envsubst
# при старте контейнера. Фильтр обязателен, иначе envsubst затрёт собственные
# переменные nginx ($uri, $host, ...) пустыми строками и конфиг станет пустым.
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Значения по умолчанию для docker compose: сервис backend и встроенный
# DNS-резолвер compose. В Kubernetes переопределяются через BACKEND_HOST
# и DNS_RESOLVER (см. k8s/frontend-deployment.yaml).
ENV BACKEND_HOST=backend:8000 \
    DNS_RESOLVER=127.0.0.11 \
    NGINX_ENVSUBST_FILTER="^(BACKEND_HOST|DNS_RESOLVER)$"

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
