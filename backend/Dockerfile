FROM node:20-alpine
WORKDIR /app

# Build args so prisma generate works at build time without real DB creds.
# Real values are injected at container runtime via environment / env_file.
ARG DATABASE_URL=postgresql://placeholder/placeholder
ARG DATABASE_URL_DIRECT=postgresql://placeholder/placeholder
ENV DATABASE_URL=$DATABASE_URL
ENV DATABASE_URL_DIRECT=$DATABASE_URL_DIRECT

# Copy package files + schema first (layer cache)
COPY package*.json ./
COPY prisma ./prisma/

# Install — postinstall hook runs prisma generate automatically
RUN npm ci --only=production

# Copy remaining source
COPY . .

# Explicit generate (idempotent, ensures client matches schema)
RUN npx prisma generate

EXPOSE 5000
CMD ["node", "src/index.js"]
