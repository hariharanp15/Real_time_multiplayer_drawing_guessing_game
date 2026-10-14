import { useState } from 'react';
import { Box, Button, TextField, Typography } from '@mui/material';

export function GuessPanel({ disabled, onGuess, messages }: { disabled: boolean; onGuess: (s: string) => void; messages: string[] }) {
  const [guess, setGuess] = useState('');
  const submit = (event: React.FormEvent) => { event.preventDefault(); if (guess.trim()) { onGuess(guess); setGuess(''); } };
  return <Box>
    <Typography variant="h6">💬 Live guesses</Typography>
    <Box sx={{ height: 170, overflow: 'auto', mt: 1, p: 1, borderRadius: 2, bgcolor: 'rgba(3, 6, 20, .58)', border: '1px solid rgba(255,255,255,.10)' }}>
      {messages.length === 0 ? <Typography variant="body2" color="text.secondary" sx={{ p: 1 }}>Guesses will appear here.</Typography> : messages.map((message, index) => <Box key={index} sx={{ px: 1, py: .75, mb: .5, borderRadius: 1.5, bgcolor: message.includes('guessed correctly!') ? 'rgba(52, 211, 153, .18)' : 'rgba(255,255,255,.055)' }}><Typography variant="body2" sx={{ color: message.includes('guessed correctly!') ? '#86efac' : 'text.primary', overflowWrap: 'anywhere' }}>{message}</Typography></Box>)}
    </Box>
    <Box component="form" onSubmit={submit} display="flex" gap={1} mt={1.5}>
      <TextField size="small" fullWidth value={guess} onChange={event => setGuess(event.target.value)} disabled={disabled} placeholder={disabled ? 'Drawer cannot guess' : 'Type your guess'} />
      <Button type="submit" variant="contained" disabled={disabled}>Send</Button>
    </Box>
  </Box>;
}
