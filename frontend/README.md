# SlideSpeak Frontend - PowerPoint to PDF Converter

![SlideSpeak Banner](https://github.com/SlideSpeak/slidespeak-webapp/assets/5519740/8ea56893-3c7a-42ee-906c-01e5797287af)

A modern, responsive web application for converting PowerPoint files to PDF format. Built with Next.js, TypeScript, and Tailwind CSS, featuring a clean UI with drag-and-drop functionality and real-time conversion progress tracking.

## 🚀 Features

- **Drag & Drop Upload**: Intuitive file upload with drag-and-drop support
- **Real-time Progress**: Live conversion status updates with polling mechanism
- **Responsive Design**: Works seamlessly across desktop and mobile devices
- **Type Safety**: Full TypeScript implementation for better development experience
- **Modern UI**: Clean, accessible interface built with Tailwind CSS
- **Error Handling**: Comprehensive error states with user-friendly messages
- **File Validation**: Supports only .pptx files with proper validation
- **Download Management**: Secure file download with presigned URLs

## 🏗️ Architecture

### Tech Stack

- **Framework**: [Next.js 14.2.2](https://nextjs.org/) - React framework with App Router
- **Language**: [TypeScript 5.4.5](https://www.typescriptlang.org/) - Type-safe JavaScript
- **Styling**: [Tailwind CSS 3.4.3](https://tailwindcss.com/) - Utility-first CSS framework
- **UI Components**: Custom components with [Tailwind CSS](https://tailwindcss.com/)
- **Package Manager**: [Bun](https://bun.sh/) - Fast JavaScript runtime and package manager
- **Testing**: [Jest](https://jestjs.io/) + [React Testing Library](https://testing-library.com/)
- **Linting**: [ESLint](https://eslint.org/) with Airbnb configuration
- **Formatting**: [Prettier](https://prettier.io/) for code formatting

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Interface│────│  State Management│────│   API Layer     │
│                 │    │                 │    │                 │
│ - File Upload   │    │ - useConvert    │    │ - FastAPI       │
│ - Progress UI   │    │ - Status States │    │ - File Upload   │
│ - Download UI   │    │ - Error Handling│    │ - Status Polling│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
frontend/
├── public/                    # Static assets
│   ├── android-chrome-*.png   # PWA icons
│   ├── favicon.ico           # Favicon
│   └── site.webmanifest      # PWA manifest
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── globals.css       # Global styles
│   │   ├── layout.tsx        # Root layout component
│   │   └── page.tsx          # Home page
│   ├── components/           # React components
│   │   ├── ChooseFileStep/   # File selection component
│   │   ├── ConfirmStep/      # File confirmation component
│   │   ├── ConverterFlow/    # Main workflow orchestrator
│   │   ├── ErrorBanner/      # Error display component
│   │   ├── ProgressStep/     # Conversion progress component
│   │   └── ResultStep/       # Success & download component
│   ├── hooks/                # Custom React hooks
│   │   └── useConvert.ts     # Main conversion state hook
│   ├── icons/                # SVG icon components
│   │   ├── CheckIcon/        # Success checkmark
│   │   ├── LoadingIndicatorIcon/ # Spinner icon
│   │   ├── PdfIcon/          # PDF file icon
│   │   └── UploadIcon/       # Upload arrow icon
│   └── utils/                # Utility functions
│       └── cn.ts             # Tailwind class merging utility
├── __tests__/                # Test configuration
├── components.json           # shadcn/ui configuration
├── jest.config.js           # Jest testing configuration
├── jest.setup.js            # Test setup and mocks
├── next.config.js           # Next.js configuration
├── package.json             # Dependencies and scripts
├── postcss.config.js        # PostCSS configuration
├── prettier.config.js       # Prettier formatting rules
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## 🔄 State Management

### useConvert Hook

The `useConvert` hook manages the entire conversion workflow:

```typescript
export type Status =
  | "idle"
  | "ready"
  | "uploading"
  | "processing"
  | "done"
  | "error";

interface ConvertState {
  status: Status;
  file?: File;
  jobId?: string;
  url?: string;
  error?: string;
}

interface ConvertActions {
  select(file: File): void;
  upload(): Promise<void>;
  complete(url: string): void;
  fail(message: string): void;
  reset(): void;
}
```

### State Flow

```
idle → ready → uploading → processing → done
  ↑                                        ↓
  └────────── reset() ←─────────────────────┘
              ↑
              └─── error (on failure)
```

## 🎨 UI Components

### ChooseFileStep

- **Purpose**: Initial file selection interface
- **Features**: Drag & drop, file input, .pptx validation
- **Props**: `onSelect(file: File)`

### ConfirmStep

- **Purpose**: File confirmation and conversion options
- **Features**: File info display, conversion preview
- **Props**: `file: File`, `onCancel()`, `onConfirm()`

### ProgressStep

- **Purpose**: Real-time conversion progress tracking
- **Features**: Status polling, timeout handling, progress animations
- **Props**: `jobId?: string`, `file: File`, `onDone(url)`, `onError(msg)`

### ResultStep

- **Purpose**: Success state and file download
- **Features**: Download button, conversion restart
- **Props**: `url: string`, `onReset()`

### ErrorBanner

- **Purpose**: Error message display
- **Features**: Consistent error styling
- **Props**: `message: string`

## 🎨 Styling System

### Tailwind Configuration

Custom color palette and animations:

```javascript
colors: {
  accent: '#FCFCFD',
  blue: {
    25: '#F5FAFF',
    50: '#EFF8FF',
    // ... extended blue palette
  },
  gray: {
    25: '#FCFCFD',
    50: '#F9FAFB',
    // ... extended gray palette
  },
  error: { /* ... */ },
  warning: { /* ... */ },
  success: { /* ... */ }
}
```

### Custom Animations

- `spin-pretty`: Smooth rotation animation
- `bounce200/400/600`: Staggered bounce effects
- `enter/leave`: Fade and scale transitions

## 🧪 Testing Strategy

### Test Structure

```
src/
├── components/__tests__/     # Component tests
├── hooks/__tests__/          # Hook tests
├── icons/__tests__/          # Icon tests
└── utils/__tests__/          # Utility tests
```

### Testing Tools

- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing utilities
- **@testing-library/user-event**: User interaction simulation
- **@testing-library/jest-dom**: Extended DOM matchers

### Test Coverage

- ✅ Component rendering
- ✅ User interactions
- ✅ Hook state management
- ✅ Error handling
- ✅ File upload validation
- ✅ Status polling logic

### Running Tests

```bash
# Run all tests
bun test

# Run tests in watch mode
bun test:watch

# Run tests with coverage
bun test:coverage
```

## 🛠️ Development Setup

### Prerequisites

- [Bun](https://bun.sh/) (latest version)
- Node.js 18+ (for compatibility)
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd frontend

# Install dependencies
bun install

# Set up environment variables
cp .env.local.example .env.local
```

### Environment Variables

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_POLL_INTERVAL=2000      # Status polling interval (ms)
NEXT_PUBLIC_POLL_TIMEOUT=300000     # Conversion timeout (ms)
```

### Development Commands

```bash
# Start development server
bun dev

# Build for production
bun build

# Start production server
bun start

# Run linter
bun lint

# Run tests
bun test
```

## 📱 Responsive Design

### Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Mobile Optimizations

- Touch-friendly file selection
- Optimized loading animations
- Responsive typography scaling
- Mobile-first CSS approach

## 🔧 Configuration Files

### Next.js Configuration

```javascript
// next.config.js
const nextConfig = {
  webpack: config => {
    config.resolve.alias.canvas = false;
    return config;
  },
};
```

### TypeScript Configuration

- Strict mode enabled
- Path aliases configured (`@/*` → `./src/*`)
- Next.js plugin integration

### ESLint Configuration

- Airbnb TypeScript configuration
- Next.js specific rules
- Prettier integration
- Custom rules for React components

## 🔄 API Integration

### File Upload Flow

1. **File Selection**: User selects .pptx file
2. **Upload Request**: POST to `/convert` with FormData
3. **Job Creation**: Backend returns `jobId`
4. **Status Polling**: GET `/status/{jobId}` every 2 seconds
5. **Completion**: Receive download URL or error message

### Error Handling

- **Network Errors**: Connection timeouts, server unavailable
- **Validation Errors**: Invalid file types, missing files
- **Conversion Errors**: Processing failures, timeout exceeded
- **User-Friendly Messages**: All errors display helpful feedback

## 🚀 Performance Optimizations

### Bundle Optimization

- Tree-shaking for unused code elimination
- Dynamic imports for code splitting
- Next.js automatic optimizations

### Runtime Performance

- Efficient polling with cleanup
- Minimal re-renders with proper state management
- Optimized images and SVGs
- CSS-in-JS avoided for better performance

## 🔐 Security Considerations

### File Upload Security

- Client-side file type validation
- File size limitations
- Secure form submission
- CORS properly configured

### Data Privacy

- No file content stored locally
- Temporary server-side processing
- Secure download URLs with expiration
- No tracking or analytics

## 🌐 Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## 📝 Code Quality

### Linting Rules

- Airbnb TypeScript configuration
- Consistent code formatting with Prettier
- Import/export organization
- React best practices enforcement

### Type Safety

- 100% TypeScript coverage
- Strict type checking
- Interface definitions for all props
- Proper error type handling

## 🔮 Future Enhancements

### Planned Features

- [ ] Multiple file upload support
- [ ] Conversion format options (PNG, JPEG)
- [ ] File preview before conversion
- [ ] Conversion history
- [ ] User accounts and file management
- [ ] Progressive Web App (PWA) features

### Technical Improvements

- [ ] Server-sent events for real-time updates
- [ ] Service worker for offline support
- [ ] Advanced error recovery
- [ ] Performance monitoring
- [ ] A/B testing framework

## 🤝 Contributing

### Development Workflow

1. Create feature branch from `main`
2. Follow conventional commit messages
3. Write tests for new features
4. Run linting and tests before commit
5. Create pull request with detailed description

### Commit Message Format

```
feat: add drag and drop file upload
fix: resolve polling timeout issue
docs: update component documentation
test: add unit tests for useConvert hook
```

### Code Style Guidelines

- Use functional components with hooks
- Prefer TypeScript interfaces over types
- Follow Tailwind CSS utility-first approach
- Write descriptive component and variable names
- Add JSDoc comments for complex functions
