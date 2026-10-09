FROM node:24.15-bookworm AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build -- --configuration production --output-path=dist/minierp

FROM nginx:alpine

COPY --from=build \
    /app/dist/minierp/browser \
    /usr/share/nginx/html
