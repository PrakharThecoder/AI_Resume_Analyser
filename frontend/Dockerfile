# Stage 1: Build the React Application
FROM node:20-alpine AS build

WORKDIR /app

# Copy package configurations and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code and build
COPY . .
# We use a build argument for VITE_API_URL so it can be injected at build time if needed
# However, Vite embeds env vars at build time. For dynamic runtime, consider window.env.
# But standard vite build uses .env.production.
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL:-http://backend:8000}

RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy the custom Nginx configuration
# Ensure the backend requests are properly routed or React Router handles history
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build artifacts from Stage 1
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
