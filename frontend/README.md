# DevOps Release Manager - Frontend

A professional, dark-themed React 18 + TypeScript dashboard for managing releases, deployments, and monitoring DevOps metrics.

## Features

### Release Management
- Release pipeline visualization (Build → Test → Security → Deploy)
- Release creation and version management
- Deployment status tracking across environments (Dev → Staging → Production)
- Release history and rollback functionality

### Deployment Workflow
- Approval workflow with pending approvals dashboard
- Pipeline stage visualization with real-time status
- Deployment logs and debugging tools
- Rollback capabilities with reason tracking

### Analytics & Monitoring
- DORA metrics dashboard:
  - Deployment Frequency
  - Lead Time for Changes
  - Change Failure Rate
  - Mean Time to Recovery (MTTR)
- Deployment trends over 30 days
- Service breakdown analytics
- Environment health status

### Audit & Compliance
- Comprehensive audit log viewer
- Filterable by action, user, and date range
- CSV export functionality
- Change tracking and history

### Additional Features
- Runbook viewer with markdown rendering
- Service registry with deployment info
- Settings and user management
- Real-time notifications
- Dark-themed UI matching Vercel/GitHub style

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **Axios** - HTTP client
- **date-fns** - Date utilities

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API integration layer
│   │   ├── client.ts     # Axios instance with interceptors
│   │   ├── auth.ts       # Authentication endpoints
│   │   ├── releases.ts   # Release management endpoints
│   │   ├── deployments.ts # Deployment endpoints
│   │   └── analytics.ts  # Analytics endpoints
│   ├── components/       # Reusable UI components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── MetricCard.tsx
│   │   ├── PipelineView.tsx
│   │   ├── ApprovalCard.tsx
│   │   ├── ReleaseCard.tsx
│   │   ├── DeploymentTimeline.tsx
│   │   ├── AuditLogTable.tsx
│   │   ├── EnvironmentStatus.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── EmptyState.tsx
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Releases.tsx
│   │   ├── Deployments.tsx
│   │   ├── Services.tsx
│   │   ├── Analytics.tsx
│   │   ├── AuditLogs.tsx
│   │   ├── Runbooks.tsx
│   │   ├── Settings.tsx
│   │   └── Login.tsx
│   ├── hooks/            # Custom React hooks
│   │   ├── useReleases.ts
│   │   ├── useDeployments.ts
│   │   └── useAnalytics.ts
│   ├── store/            # Zustand stores
│   │   └── auth.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── index.html
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint

# Type check
npm run type-check
```

The application will be available at `http://localhost:3000`

## Configuration

### API Configuration

The API base URL is configured in `src/api/client.ts`. By default, it connects to:
- Development: `http://localhost:8000`
- Production: `process.env.VITE_API_URL`

### Authentication

The application uses JWT token-based authentication. The token is:
- Stored in `localStorage` under the key `auth_token`
- Automatically included in all API requests
- Refreshed automatically when expired

### Environment Variables

Create a `.env.local` file for environment-specific configuration:

```env
VITE_API_URL=http://localhost:8000
```

## Authentication

### Login Flow

1. User enters credentials on the login page
2. Backend returns JWT access token
3. Token is stored in localStorage
4. Token is included in all subsequent API requests
5. If token expires, the app automatically attempts to refresh it
6. If refresh fails, user is redirected to login

### Demo Credentials

- Email: `demo@example.com`
- Password: `password123`

## Key Components

### Header Component
- Search functionality
- Notifications dropdown
- User profile menu with logout

### Sidebar Navigation
- Main navigation menu
- Active page highlighting
- User info and logout button
- Mobile-responsive toggle

### Status Badge
- Color-coded status indicators
- Animated loading states
- Compact and normal sizes

### Pipeline View
- Horizontal and vertical layouts
- Stage-by-stage progress tracking
- Duration calculation
- Status visualization

### Approval Card
- Deployment details display
- Approve/Reject buttons
- Comment functionality
- Auto-calculated durations

### Metric Cards
- KPI visualization
- Trend indicators
- Customizable colors
- Icon support

## Styling

### Tailwind CSS Configuration
- Dark mode enabled by default
- Custom color scheme with indigo accents
- Brand colors:
  - Primary: Indigo (`#4f46e5`)
  - Secondary: Purple (`#8b5cf6`)
- Dark palette:
  - Background: `gray-950`
  - Cards: `gray-800`
  - Borders: `gray-700`
  - Text: `gray-100`

### CSS Classes

Common utility classes defined in `index.css`:
- `btn-primary` - Primary action button
- `btn-secondary` - Secondary action button
- `btn-danger` - Destructive action button
- `card` - Card component styling
- `input-field` - Form input styling
- `transition-smooth` - Smooth transitions

## API Integration

### Query Hooks

The application uses TanStack Query for server state management:

```typescript
// Fetching data
const { data, isLoading, error } = useReleases(page, pageSize, filters)

// Mutations
const { mutate, isPending } = useDeployRelease()
```

### Cache Management

- Queries are cached for 30-60 seconds by default
- Mutations automatically invalidate related queries
- Stale time and cache time are configurable per hook

## Performance Optimizations

1. **Code Splitting**: Pages are loaded on-demand via React Router
2. **Query Caching**: TanStack Query prevents redundant API calls
3. **Memoization**: Components use React.memo where appropriate
4. **Lazy Loading**: Images and heavy components are lazy-loaded
5. **Build Optimization**: Vite provides tree-shaking and minification

## Development Guidelines

### Component Structure

```typescript
import React from 'react'
import { Icon } from 'lucide-react'

interface ComponentProps {
  label: string
  onClick: () => void
}

export function MyComponent({ label, onClick }: ComponentProps) {
  return (
    <div className="space-y-4">
      {/* Content */}
    </div>
  )
}
```

### Naming Conventions

- Components: PascalCase
- Functions: camelCase
- Types/Interfaces: PascalCase
- Constants: UPPER_CASE
- CSS classes: kebab-case

### Type Safety

- All props are explicitly typed
- Avoid `any` type
- Use discriminated unions for complex states
- Export types from `src/types/index.ts`

## Debugging

### Console Logs
Development mode includes detailed console logs for:
- API requests and responses
- State changes
- Component renders

### React DevTools
Install the React DevTools browser extension for:
- Component tree inspection
- Props and state inspection
- Performance profiling

### Network Tab
Monitor API calls in the browser's Network tab to:
- Verify request/response payloads
- Check authentication headers
- Debug API errors

## Testing

### Unit Tests
```bash
npm run test
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

## Deployment

### Production Build

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

### Deployment Options

- **Vercel**: Push to GitHub and connect to Vercel
- **Netlify**: Connect GitHub repo to Netlify
- **Docker**: Use Nginx to serve the `dist/` directory
- **Traditional Server**: Upload `dist/` to your web server

### Environment Configuration

Create a `.env.production` file:

```env
VITE_API_URL=https://api.yourdomain.com
```

## Troubleshooting

### Common Issues

**Issue**: API requests return 401
- **Solution**: Check token in localStorage, ensure backend is running

**Issue**: Blank page after login
- **Solution**: Check browser console for errors, verify API URL

**Issue**: Slow page loads
- **Solution**: Check Network tab for slow API calls, enable caching headers

**Issue**: Styles not loading
- **Solution**: Rebuild with `npm run build`, clear browser cache

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari iOS 14+

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact the development team.
