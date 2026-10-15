# Serves production build via Vite preview (Node 20; devDependencies kept for the preview binary).
FROM node:20-alpine
WORKDIR /app
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_APP_TITLE=ERM Platform
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_TITLE=$VITE_APP_TITLE
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["./node_modules/.bin/vite", "preview", "--host", "0.0.0.0", "--port", "5173"]
