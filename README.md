# BAO

I'll check your current directory first, then walk you through every step in order.
Good — you're in the right directory. Here is the complete setup, step by step.
________________________________________
Step 1 — Install NestJS CLI and create the backend
# Install NestJS CLI globally (one-time)
npm install -g @nestjs/cli
# Scaffold the NestJS app into panda-app/backend
mkdir -p "panda-app" && cd "panda-app" && nest new backend --package-manager npm --skip-git
________________________________________
Step 2 — Install all backend packages
cd backend
npm install @nestjs/jwt @nestjs/passport passport passport-jwt @prisma/client prisma bcrypt class-validator class-transformer @nestjs/websockets @nestjs/platform-socket.io socket.io @nestjs/config
npm install -D @types/passport-jwt @types/bcrypt
________________________________________
Step 3 — Replace main.ts to run on port 3001 with CORS
Create/replace panda-app/backend/src/main.ts with this exact content:
// panda-app/backend/src/main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.enableCors({
    origin: 'http://localhost:3000',
    credentials: true,
  });

  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));

  await app.listen(3001);
  console.log('Panda backend running on http://localhost:3001');
}
bootstrap();
________________________________________
Step 4 — Initialize Prisma
# Still inside panda-app/backend
npx prisma init
This creates prisma/schema.prisma and a .env file. Open .env and set your database URL:
# panda-app/backend/.env
DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/panda_db"
________________________________________
Step 5 — Create the Next.js frontend
Open a new terminal tab, go back to panda-app/:
cd ..   # now in panda-app/
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*" \
  --skip-install \
  --no-git
Flags explained: --typescript = TS, --tailwind = Tailwind, --app = App Router, --no-src-dir = files at root not under src/.
cd frontend
npm install

	This part is completed 
________________________________________
Step 6 — Install all frontend packages
# Still in panda-app/frontend
npm install framer-motion zustand socket.io-client axios react-hot-toast
________________________________________
Step 7 — Final folder structure
After the above steps your tree will look like this:
panda-app/
├── backend/
│   ├── src/
│   │   ├── app.controller.ts
│   │   ├── app.module.ts
│   │   ├── app.service.ts
│   │   └── main.ts          ← edited in Step 3
│   ├── prisma/
│   │   └── schema.prisma
│   ├── .env
│   └── package.json
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   └── page.tsx
    ├── public/
    ├── tailwind.config.ts
    ├── tsconfig.json
    └── package.json
________________________________________
Step 8 — Verify both apps start
Terminal 1 — backend:
cd panda-app/backend
npm run start:dev
# Expected: "Panda backend running on http://localhost:3001"
Terminal 2 — frontend:
cd panda-app/frontend
npm run dev
# Expected: "Ready - started server on http://localhost:3000"
________________________________________
Quick sanity check
# Confirm backend is alive (from any terminal)
curl http://localhost:3001
# Should return: "Hello World!"

# Frontend — open in browser
# http://localhost:3000
________________________________________
What you have now:
•	Backend: NestJS on port 3001, CORS open to :3000, Prisma wired, JWT/Passport/WebSocket packages installed, global ValidationPipe active.
•	Frontend: Next.js 14 App Router, TypeScript, Tailwind CSS, plus framer-motion, zustand, socket.io-client, axios, react-hot-toast ready to import.
Let me know when both servers are green and we'll move on to auth, WebSocket rooms, or the UI — whichever you want first.
