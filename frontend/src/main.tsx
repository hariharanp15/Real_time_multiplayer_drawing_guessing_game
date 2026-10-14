import React, { useMemo, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import App from './App';
import { HomePage } from './pages/HomePage';
import { createAppTheme, type ColorMode } from './theme';
import './index.css';

function Root() {
  const [mode, setMode] = useState<ColorMode>(() => localStorage.getItem('sketch-theme') === 'light' ? 'light' : 'dark');
  const theme = useMemo(() => createAppTheme(mode), [mode]);
  const toggleTheme = () => setMode(current => { const next = current === 'dark' ? 'light' : 'dark'; localStorage.setItem('sketch-theme', next); return next; });
  return <ThemeProvider theme={theme}><CssBaseline /><div className={`app-shell ${mode}`}><BrowserRouter><Routes><Route path="/" element={<HomePage mode={mode} onToggleTheme={toggleTheme} />} /><Route path="/room/:code" element={<App />} /></Routes></BrowserRouter></div></ThemeProvider>;
}

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><Root /></React.StrictMode>);
