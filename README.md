# MyDaily — Universal Productivity & Life Management Platform

MyDaily is a modern, responsive personal productivity and life-management web application. It serves as a unified system to organize daily schedules, tasks, learning tracks, habits, goals, notes, and analytics.

---

## 🌟 Core Architectural Principles

1. **Completely Dynamic & Non-Hardcoded**:
   - Zero hardcoded personal subjects or activities (such as German, Automotive, Programming, Math).
   - All categories, topics, priorities, habits, and schedules are 100% database-driven and customizable per user.
2. **Pure CSS3 Design System**:
   - Built entirely with pure CSS3 custom properties (design tokens).
   - No external CSS frameworks (Tailwind, Bootstrap, etc.) to guarantee ultra-fast load times and complete styling control.
   - Minimalist theme default (`#F8FAFC` canvas, `#FFFFFF` crisp cards, `#4F46E5` accent, `#E2E8F0` hairline borders) with dark theme alternative.
3. **Advanced Recurrence Engine**:
   - Handles `none`, `daily`, `weekly`, `selected_weekdays`, `monthly`, and `custom` recurrences.
   - Computes virtual instances across any date range (daily, weekly, monthly, agenda) **without duplicating database rows**.
   - Tracks individual instance completions, skips, and rescheduling via `ActivityInstanceLog`.
   - Real-time time conflict detection to prevent overlapping events.
4. **Calculated Production Metrics**:
   - Dashboard stats, streaks, completion percentages, and study hours are calculated dynamically from database records.

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: Nuxt 4 (compatibility mode in Nuxt 3)
- **Component Engine**: Vue 3 (Composition API)
- **Language**: JavaScript (ES modules)
- **Styling**: Pure CSS3 (`assets/css/main.css`) with responsive design tokens
- **Icons**: Custom SVG component library (`components/AppIcon.vue`)
- **PWA & Web Push**: Progressive Web App manifest (`manifest.json`) and Service Worker (`sw.js`)

### Backend
- **Language**: Python 3.11+
- **Framework**: Django 5.2
- **REST Engine**: Django REST Framework (DRF)
- **Authentication**: Simple JWT (Bearer tokens with automatic refresh)
- **Database**: SQLite for development, configured for seamless migration to PostgreSQL or MySQL
- **CORS**: `django-cors-headers` enabled for web, PWA, mobile (Capacitor), and remote Cloudflare Tunnels

---

## 📱 The 11 Core Application Modules

| # | Module | Route | Key Capabilities |
|---|--------|-------|------------------|
| 1 | **Dashboard** | `/` | 8 real-time calculated DB stat cards, Today's schedule with completion/skip toggles, quick tasks, habit streaks, goals, learning progress, upcoming reminders, customizable widgets. |
| 2 | **Timetable** | `/timetable` | 4 calendar views (Daily, Weekly, Monthly, Agenda), conflict detection, recurrence rules, reschedule, duplicate, filter by category/priority. |
| 3 | **Tasks** | `/tasks` | Multi-status backlog (To Do, In Progress, Completed), interactive subtasks checklist, priorities, deadlines, estimated minutes. |
| 4 | **Learning** | `/learning` | Universal learning tracks (any skill or subject), target hours vs logged hours, syllabus, milestone dates, learning resources. |
| 5 | **Study Sessions**| `/study-sessions` | Pomodoro focus timer (25m / 5m), stopwatch, manual session logger, automatic synchronization with learning tracks. |
| 6 | **Habits & Routines** | `/habits` | Daily/weekly rituals, time of day grouping, current & best streak counters, interactive 7-day completion grid. |
| 7 | **Goals** | `/goals` | Short-term (<3mo), Medium-term (3-12mo), and Long-term (1yr+) quantifiable targets with progress sliders and milestones. |
| 8 | **Notes** | `/notes` | Markdown-supported knowledge base, search by title and content, pin to top, category tagging. |
| 9 | **Notifications** | `/notifications` | Schedule reminders, streak alerts, system messages, web push notification subscription support. |
| 10 | **Analytics** | `/analytics` | 30-day focus trends, category distribution breakdown (activities vs tasks vs study time), achievement metrics. |
| 11 | **Settings** | `/settings` | Dynamic category manager (create/edit/delete categories with custom colors and icons), profile settings, dark/light theme switcher. |

---

## 🚀 Getting Started

### 1. Backend Setup (Django)

```bash
# In the project root, activate the Python virtual environment:
.\venv\Scripts\Activate.ps1

# Navigate to backend
cd backend

# Run database migrations
python manage.py migrate

# (Optional) Seed demo user with starter data
python manage.py shell -c "from django.contrib.auth.models import User; from accounts.seed_data import seed_user_data; user, _ = User.objects.get_or_create(username='demo', defaults={'email':'demo@mydaily.local'}); user.set_password('password123'); user.first_name='Alex'; user.last_name='Morgan'; user.save(); seed_user_data(user); print('Demo ready!')"

# Start the Django development server (runs on port 8000)
python manage.py runserver 127.0.0.1:8000
```

### 2. Frontend Setup (Nuxt 4 / Vue 3)

```bash
# In a new terminal, navigate to frontend:
cd frontend

# Start the Nuxt development server (runs on port 3000)
npm run dev

# Or build for production:
npm run build
```

Open `http://localhost:3000` in your browser.

---

## 🏭 Production Mode & Deployment

MyDaily is configured with production optimizations for both the backend (Django + WhiteNoise + Waitress/Gunicorn) and the frontend (Nuxt SPA / Static / Nitro Node server).

### Production Configuration Summary

| Layer | Production Settings |
|-------|---------------------|
| **Backend** | `DEBUG=False` by default; WhiteNoise static caching (`CompressedManifestStaticFilesStorage`); Security headers (`X-Frame-Options: DENY`, `nosniff`, proxy SSL support); Rotating file logging (`logs/mydaily.log`); Configurable via `.env`. |
| **Frontend** | Devtools disabled; Static assets cached immutably; Cache headers configured in `routeRules`; Optimized minified bundle (~1.7 MB total, ~430 KB gzip); PWA Service Worker caching & background sync enabled. |
| **Reverse Proxy** | Production Nginx configuration provided (`nginx/nginx.conf`) handling Gzip, SSL proxy headers, `/api/` routing, and `/static/` caching. |

---

### Running in Production

#### Option 1: Docker Compose (Recommended for Containers & Cloud)
Run the complete production stack (Backend + Frontend + Nginx):
```bash
docker-compose up -d --build
```
Access the application at `http://localhost`.

#### Option 2: Windows Production Run (Native)
Run the production runner script:
```cmd
start-production.bat
```
This automatically runs `collectstatic`, starts the production WSGI server (`waitress-serve`) on `127.0.0.1:8000`, and starts the production Nuxt server on `localhost:3000`.

#### Option 3: Linux / macOS / VPS Production Run
```bash
chmod +x start-production.sh
./start-production.sh
```
This runs Gunicorn with 3 workers and the Nuxt production Node server.

#### Option 4: Android Phone as Server (via Termux)
Host MyDaily directly on your Android device so any laptop, tablet, or PC on your Wi-Fi can connect to it:
```bash
# 1. First-time setup on Android:
chmod +x termux-setup.sh termux-server.sh
./termux-setup.sh

# 2. Start as a background server (persists with screen off):
./termux-server.sh start

# 3. Check status & get your phone's Wi-Fi URL:
./termux-server.sh status

# 4. View logs or stop:
./termux-server.sh logs
./termux-server.sh stop
```
- Access from your Android phone: `http://localhost:3000`
- Access from your laptop/PC on the same Wi-Fi: `http://<phone-ip>:3000` (auto-displayed by `./termux-server.sh status`).

#### Option 5: 100% Static Frontend Hosting (Cloudflare Pages, Vercel, Netlify)
Generate pure static HTML/JS/CSS assets:
```bash
cd frontend
npm run generate
```
The output in `frontend/.output/public` is fully self-contained and can be deployed directly to any static web hosting or CDN.

---

## 🔑 Demo Account Credentials

For quick local testing and evaluation:
- **Username**: `demo`
- **Password**: `password123`
*(Or click the "Quick Demo Login" button on `/login` to sign in instantly).*

---

## 🌐 Remote Access & Mobile Readiness

- **Cloudflare Tunnel**:
  Run `cloudflared tunnel --url http://localhost:3000` to expose the frontend securely with remote HTTPS.
- **Capacitor Android**:
  The frontend is configured in client-side SPA mode (`ssr: false`) with PWA manifest and service worker. You can initialize Capacitor at any time with:
  ```bash
  cd frontend
  npx @capacitor/cli create
  ```

