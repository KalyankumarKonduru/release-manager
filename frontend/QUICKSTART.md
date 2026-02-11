# Quick Start Guide

Get the DevOps Release Manager frontend running in minutes.

## Prerequisites

- Node.js 16+ (`node --version`)
- npm 7+ (`npm --version`)
- Backend API running on `http://localhost:8000`

## Installation & Run

### Step 1: Install Dependencies

```bash
cd /sessions/ecstatic-blissful-mayer/release-manager/frontend
npm install
```

This installs all required packages listed in `package.json`.

### Step 2: Start Development Server

```bash
npm run dev
```

The application will start on `http://localhost:3000`

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  press h to show help
```

### Step 3: Login

Open `http://localhost:3000` in your browser and login with:

**Demo Credentials:**
- Email: `demo@example.com`
- Password: `password123`

Or use your own backend credentials.

## What You Get

After logging in, you'll see:

### Dashboard
- KPI metrics (releases, deployments, success rate, MTTR)
- 30-day deployment trends chart
- Recent deployments timeline

### Releases Page
- Release list with search and filtering
- Release creation (with backend support)
- Deploy actions to different environments
- Release status tracking

### Deployments Page
- Pending approvals section
- Deployment list with pipeline visualization
- Approve/reject with comments
- Rollback functionality
- Pipeline stage details

### Analytics
- DORA metrics dashboard
- Deployment frequency trends
- Lead time distribution
- Change failure rate
- MTTR tracking
- Service breakdown

### Audit Logs
- Complete activity history
- Filterable by date, user, action
- CSV export
- Expandable details

### Runbooks
- Runbook repository with markdown rendering
- Search and category filtering
- Three sample runbooks included

### Services
- Service registry
- Repository links
- Last deployment info
- Deploy actions

### Settings
- User profile management
- Password management
- Notification preferences
- Security settings
- Team management

## Build for Production

### Create Optimized Build

```bash
npm run build
```

Creates a production-ready bundle in `dist/` directory (~200KB gzipped)

### Preview Production Build

```bash
npm run preview
```

Serves the production build locally for testing.

### Deploy to Production

#### Option 1: Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

#### Option 2: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

#### Option 3: Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Configuration

### API URL

Set the backend API URL in your environment:

**Development (default):**
```bash
# Uses http://localhost:8000
npm run dev
```

**Production:**
Create `.env.production`:
```env
VITE_API_URL=https://api.yourdomain.com
```

Then build:
```bash
npm run build
```

## Available Commands

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

## Troubleshooting

### Issue: "Cannot find module"

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Failed to fetch from API"

**Solution:** Ensure backend is running on `http://localhost:8000`

```bash
# Check if backend is accessible
curl http://localhost:8000/health
```

### Issue: "Login not working"

**Solution:** Check browser console for errors (F12 → Console tab)

Common causes:
- Backend API not running
- CORS issues (backend misconfigured)
- Invalid credentials
- Token expired

### Issue: "Types are not recognized"

**Solution:** Run type checking:
```bash
npm run type-check
```

Fix any TypeScript errors shown.

## Development Workflow

### 1. Start Dev Server

```bash
npm run dev
```

### 2. Make Changes

Edit files in `src/` directory. Changes hot-reload automatically.

### 3. Check Types

```bash
npm run type-check
```

### 4. Lint Code

```bash
npm run lint
```

### 5. Build & Test

```bash
npm run build
npm run preview
```

### 6. Deploy

```bash
npm run build
# Then deploy dist/ folder
```

## File Structure Quick Reference

```
src/
├── pages/           # Page components (Dashboard, Releases, etc.)
├── components/      # Reusable UI components
├── api/             # Backend integration
├── hooks/           # Custom React hooks
├── store/           # State management (Zustand)
├── types/           # TypeScript types
├── App.tsx          # Main app
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## Key Technologies

| Tech | Version | Purpose |
|------|---------|---------|
| React | 18 | UI Framework |
| TypeScript | 5 | Type Safety |
| Vite | 5 | Build Tool |
| Tailwind CSS | 3 | Styling |
| TanStack Query | 5 | Server State |
| Zustand | 4 | Client State |
| Axios | 1.6 | HTTP Client |
| Recharts | 2.10 | Charts |
| Lucide React | 0.294 | Icons |

## Next Steps

1. **Integrate with Backend**: Update API endpoints in `src/api/` to match your backend
2. **Customize Branding**: Update colors in `tailwind.config.js`
3. **Add Features**: Create new pages in `src/pages/`
4. **Deploy**: Use Vercel, Netlify, or Docker

## Support

For detailed documentation, see:
- `README.md` - Full documentation
- `FILE_MANIFEST.md` - Complete file list and structure
- Individual component files have JSDoc comments

## Demo Data

The application includes mock data for:
- Services (Services page)
- Runbooks (Runbooks page)
- Sample DORA metrics

Replace with real API data by updating the respective pages and hooks.

## Performance Tips

1. **Enable HTTP/2** on your server
2. **Use CDN** for static assets
3. **Enable gzip compression** in Nginx/Apache
4. **Cache API responses** appropriately
5. **Monitor bundle size** with `npm run build`

---

**Ready to use!** Open http://localhost:3000 and start managing your deployments.
