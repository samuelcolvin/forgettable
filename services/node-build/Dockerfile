FROM node:22-slim

# Enable corepack for pnpm
RUN corepack enable && corepack prepare pnpm@10.24.0 --activate

WORKDIR /app

# Copy package files for dependency caching
COPY package.json pnpm-lock.yaml ./

# Install all dependencies (including devDependencies for Vite builds)
RUN pnpm install --frozen-lockfile

# Copy source and compile TypeScript
COPY tsconfig.json ./
COPY src ./src
RUN pnpm build

ENV PORT=3000

EXPOSE 3000

CMD ["node", "dist/index.js"]
