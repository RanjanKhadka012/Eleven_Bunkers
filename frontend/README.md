# Bunker Game Frontend

React + Vite frontend for the Bunker social survival game.

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Development

- **Dev Server:** `npm run dev`
- **Build:** `npm run build`
- **Preview:** `npm run preview`

## API Integration

The frontend is configured to proxy API requests to `http://localhost:8000/api/`

Make sure the Django backend is running:
```bash
cd backend
venv\Scripts\activate
python manage.py runserver
```

## Folder Structure

- `src/` - React components and styles
- `index.html` - Main HTML file
- `vite.config.js` - Vite configuration with API proxy

## Technologies

- React 18
- Vite 4
- Axios for HTTP requests
