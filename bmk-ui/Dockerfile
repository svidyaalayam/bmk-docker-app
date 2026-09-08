# Build React app
FROM node:22-alpine AS build

WORKDIR /app

ARG VITE_APP_DOMAIN=localhost
ARG VITE_API_BASE_URL=
ARG VITE_APP_ENV=production
ARG VITE_SIKSHAVAHINI_URL=http://localhost:8180
ARG VITE_SUNAADAM_URL=http://localhost:8280

ENV VITE_APP_DOMAIN=$VITE_APP_DOMAIN \
    VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_APP_ENV=$VITE_APP_ENV \
    VITE_SIKSHAVAHINI_URL=$VITE_SIKSHAVAHINI_URL \
    VITE_SUNAADAM_URL=$VITE_SUNAADAM_URL

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# Serve with Nginx and reverse-proxy /api to Django
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
