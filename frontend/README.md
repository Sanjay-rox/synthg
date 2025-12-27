# 🎨 SynthGuard Unified Frontend

Modern, dark-themed React interface for the SynthGuard identity verification system.

---

## 🎯 Features

✅ **Single-page workflow** - Complete verification in one interface  
✅ **Real-time progress** - Live updates as layers process  
✅ **Interactive visualizations** - Circular scores, graphs, breakdowns  
✅ **Document upload** - Drag & drop with preview  
✅ **Detailed results** - Layer breakdown, red flags, trust indicators  
✅ **Export reports** - Download JSON reports  
✅ **Responsive design** - Works on desktop, tablet, mobile  
✅ **Dark cyberpunk theme** - Modern aesthetic with neon accents

---

## 📋 Prerequisites

- **Node.js 18+** (check with `node --version`)
- **npm or yarn** package manager
- **Orchestrator running** on port 9000

---

## 🚀 Quick Start

### Step 1: Navigate to Frontend Directory

```bash
cd synthguard2/unified-frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Start Development Server

```bash
npm run dev
```

The app will open automatically at: **http://localhost:3000**

---

## 🛠️ Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## 📁 Project Structure

```
unified-frontend/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/             # React components
│   │   ├── IdentityForm.jsx           # Identity input form
│   │   ├── DocumentUpload.jsx         # Document file upload
│   │   ├── LiveProgress.jsx           # Real-time progress tracker
│   │   ├── ScoreDisplay.jsx           # Circular score display
│   │   ├── LayerBreakdown.jsx         # Individual layer details
│   │   ├── VerdictDisplay.jsx         # Final verdict card
│   │   └── RedFlagsPanel.jsx          # Warnings & trust signals
│   ├── services/
│   │   └── api.js              # Orchestrator API client
│   ├── App.jsx                 # Main application
│   ├── App.css                 # Global styles
│   └── main.jsx                # React entry point
├── package.json                # Dependencies
├── vite.config.js              # Vite configuration
└── README.md                   # This file
```

---

## 🔌 API Configuration

The frontend connects to the orchestrator at **http://localhost:9000** by default.

### Change API URL

Create `.env` file in the root:

```bash
VITE_API_URL=http://your-orchestrator-url:9000
```

Or modify `src/services/api.js`:

```javascript
const API_BASE_URL = "http://localhost:9000";
```

---

## 🎨 Component Overview

### **IdentityForm**

- Collects identity data (name, email, phone, Aadhaar, PAN, etc.)
- Form validation
- Required field indicators
- Grouped sections (Basic, Documents, Address, Professional)

### **DocumentUpload**

- Drag & drop file upload
- Image preview thumbnails
- Document type selector
- File validation (size, type)
- Remove documents

### **LiveProgress**

- Shows all 4 layers processing
- Real-time status updates
- Animated progress bars
- Layer-specific icons and colors

### **ScoreDisplay**

- Animated circular progress ring
- Score counting animation (0 → final score)
- Large verdict badge
- Confidence level
- Expandable interpretation guide

### **LayerBreakdown**

- Expandable layer cards
- Individual scores and contributions
- Key findings for each layer
- Processing time display
- Summary statistics

### **VerdictDisplay**

- Large animated verdict icon
- Detailed explanation
- Recommendation message
- Verification ID (copyable)
- Download report button
- Print report button

### **RedFlagsPanel**

- Tabbed interface (Red Flags / Trust Indicators)
- Severity-based color coding
- Sorted by severity (Critical → Low)
- Layer attribution
- Summary statistics

---

## 🧪 Testing the Frontend

### Test with Mock Data

1. **Start the frontend:**

   ```bash
   npm run dev
   ```

2. **Fill the form with test data:**

   ```
   Name: Test User
   Email: test@example.com
   Phone: +91 9876543210
   DOB: 1990-01-01
   Aadhaar: 123456789012
   PAN: ABCDE1234F
   Location: Bangalore 560001
   ```

3. **Click "Verify Identity"**

4. **Expected behavior:**
   - Progress indicators animate
   - Results appear after ~5-10 seconds
   - Score displays with verdict
   - Layer breakdown shows details

### Test with Documents

1. **Prepare test images** (any JPG/PNG)
2. **Drag & drop** into upload area
3. **Select document type** (Aadhaar/PAN)
4. **Submit verification**

---

## 🎨 Customization

### Change Theme Colors

Edit `src/App.css`:

```css
:root {
  --accent-cyan: #00d9ff; /* Primary accent */
  --accent-purple: #a855f7; /* Secondary accent */
  --bg-primary: #0a0e27; /* Background */
  --color-verified: #10b981; /* Success color */
  --color-suspicious: #f59e0b; /* Warning color */
  --color-reject: #ef4444; /* Error color */
}
```

### Modify Verdict Thresholds

The frontend displays verdicts based on orchestrator thresholds. To change labels or styling, edit `src/components/VerdictDisplay.jsx`.

---

## 🚨 Troubleshooting

### Issue: "Failed to fetch" error

**Solution:**

- Ensure orchestrator is running on port 9000
- Check `npm run dev` shows correct proxy in Vite config
- Try: `curl http://localhost:9000/health`

### Issue: CORS errors

**Solution:**

- Orchestrator should allow CORS from `localhost:3000`
- Check orchestrator `.env`:
  ```bash
  CORS_ORIGINS=http://localhost:3000,http://localhost:5173
  ```

### Issue: Components not loading

**Solution:**

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: Styles not applying

**Solution:**

- Check browser console for CSS errors
- Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
- Verify `App.css` is imported in `App.jsx`

### Issue: Upload not working

**Solution:**

- Check file size (max 5MB)
- Check file type (JPG, PNG, WEBP only)
- Check browser console for errors

---

## 📱 Responsive Design

The frontend is fully responsive:

- **Desktop (1400px+)**: Full layout with all features
- **Tablet (768px-1400px)**: Stacked cards, adjusted spacing
- **Mobile (< 768px)**: Single column, touch-optimized

---

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

Output: `dist/` folder

### Deploy to Static Hosting

#### **Vercel**

```bash
npm install -g vercel
vercel
```

#### **Netlify**

```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

#### **GitHub Pages**

```bash
npm run build
# Push dist/ folder to gh-pages branch
```

### Environment Variables for Production

Create `.env.production`:

```bash
VITE_API_URL=https://your-production-orchestrator.com
```

---

## 🔒 Security Notes

### Browser Storage

Currently, the frontend does NOT store any sensitive data:

- No localStorage/sessionStorage
- No cookies
- All data exists only in React state during session

### API Communication

- All requests go through HTTPS in production
- No sensitive data in URL parameters
- Document data sent as base64 in POST body

### Production Checklist

- [ ] Use HTTPS for orchestrator
- [ ] Set proper CORS origins
- [ ] Implement rate limiting on orchestrator
- [ ] Add authentication if needed
- [ ] Enable CSP headers
- [ ] Minimize bundle size
- [ ] Enable gzip compression

---

## 🎯 Features Roadmap

### Current Version (v1.0)

- ✅ Identity form with validation
- ✅ Document upload
- ✅ Real-time progress tracking
- ✅ Score visualization
- ✅ Layer breakdown
- ✅ Red flags & trust indicators

### Future Enhancements

- [ ] Graph visualization (vis-network integration)
- [ ] Behavioral tracking (Layer 4)
- [ ] Real-time WebSocket updates
- [ ] Multi-language support
- [ ] Dark/Light theme toggle
- [ ] Comparison mode (multiple verifications)
- [ ] Export PDF reports
- [ ] Save verification history

---

## 🤝 Contributing

### Code Style

- Use functional components with hooks
- Follow ESLint rules
- Add PropTypes for components
- Comment complex logic
- Keep components under 300 lines

### Component Guidelines

- One component per file
- Props at top of file
- Event handlers prefixed with `handle`
- Styles inline for component-specific
- Global styles in `App.css`

---

## 📊 Performance

### Bundle Size

- **Initial load:** ~200KB (gzipped)
- **With chunks:** ~50KB per route
- **Images:** Lazy loaded

### Optimization Tips

```bash
# Analyze bundle
npm run build
npx vite-bundle-visualizer
```

### Lighthouse Scores (Target)

- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 90+

---

## 🐛 Known Issues

1. **Graph visualization not implemented** - Placeholder message shown
2. **Layer 4 disabled** - Will be enabled when backend ready
3. **No offline support** - Requires internet connection

---

## 📞 Support

For issues or questions:

1. Check this README
2. Check browser console for errors
3. Test orchestrator with `curl http://localhost:9000/health`
4. Review Vite dev server output

---

## 📄 License

Part of SynthGuard - PEC Hacks 3.0 FinTech Track

---

**Built with React + Vite + ❤️**

**Ready to detect synthetic identities!** 🛡️
