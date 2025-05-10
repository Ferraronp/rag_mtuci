# frontend/Dockerfile
FROM node:18-alpine AS build

WORKDIR /app
COPY . .

RUN npm install
RUN npm run build

# Production nginx image
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
