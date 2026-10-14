import { createTheme } from '@mui/material/styles';

export type ColorMode = 'light' | 'dark';

export const createAppTheme = (mode: ColorMode) => createTheme({
  palette: mode === 'dark'
    ? { mode, primary: { main: '#8b5cf6' }, secondary: { main: '#22d3ee' }, success: { main: '#34d399' }, error: { main: '#fb7185' }, background: { default: '#090b1a', paper: 'rgba(22, 27, 56, 0.82)' }, text: { primary: '#f7f7ff', secondary: '#aeb7d5' } }
    : { mode, primary: { main: '#6d28d9' }, secondary: { main: '#0891b2' }, success: { main: '#059669' }, error: { main: '#e11d48' }, background: { default: '#f5f3ff', paper: 'rgba(255,255,255,.86)' }, text: { primary: '#191534', secondary: '#625d7c' } },
  typography: { fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', h3: { fontWeight: 800, letterSpacing: '-0.045em' }, h4: { fontWeight: 750, letterSpacing: '-0.035em' }, h5: { fontWeight: 750 } },
  shape: { borderRadius: 18 },
  components: {
    MuiPaper: { styleOverrides: { root: { backgroundImage: mode === 'dark' ? 'linear-gradient(135deg, rgba(35, 42, 82, .88), rgba(16, 19, 43, .88))' : 'linear-gradient(135deg, rgba(255,255,255,.95), rgba(241,238,255,.90))', border: mode === 'dark' ? '1px solid rgba(167, 139, 250, .18)' : '1px solid rgba(109, 40, 217, .12)', boxShadow: mode === 'dark' ? '0 24px 70px rgba(0,0,0,.25)' : '0 20px 55px rgba(76,29,149,.12)', backdropFilter: 'blur(18px)' } } },
    MuiButton: { styleOverrides: { root: { borderRadius: 12, fontWeight: 750, textTransform: 'none', padding: '10px 18px' }, contained: { boxShadow: '0 10px 24px rgba(124, 58, 237, .32)' } } },
    MuiTextField: { styleOverrides: { root: { '& .MuiOutlinedInput-root': { background: mode === 'dark' ? 'rgba(255,255,255,.045)' : 'rgba(109,40,217,.035)' } } } },
    MuiChip: { styleOverrides: { root: { fontWeight: 800, borderRadius: 10 } } },
  },
});
