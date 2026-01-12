FROM node:22-slim

# Enable corepack for pnpm
RUN corepack enable && corepack prepare pnpm@10.24.0 --activate

WORKDIR /app

# Copy package files for dependency caching
COPY package.json pnpm-lock.yaml ./

# Install all dependencies (including devDependencies for Vite builds)
RUN pnpm install --frozen-lockfile

# Biome config is required at runtime (build validation step)
COPY biome.jsonc ./

# Copy source and compile TypeScript
COPY tsconfig.json ./
COPY src ./src
RUN pnpm build

# Copy shadcn components for use in builds
COPY shadcn ./shadcn

EXPOSE 3002

CMD ["node", "--import", "./dist/instrumentation.js", "dist/index.js"]
