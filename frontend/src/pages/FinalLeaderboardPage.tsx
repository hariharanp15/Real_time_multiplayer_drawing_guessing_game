import { useEffect, useState } from 'react';
import { Box, Button, Container, Paper, Stack, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import type { Player } from '../types';

export function FinalLeaderboardPage({ players }: { players: Player[] }) {
  const navigate = useNavigate(); const [remaining, setRemaining] = useState(8);
  const ranking = [...players].sort((left, right) => right.score - left.score);
  const winner = ranking[0]; const runnerUp = ranking[1]; const others = ranking.slice(2);
  useEffect(() => { if (!remaining) { navigate('/'); return; } const timer = window.setTimeout(() => setRemaining(value => value - 1), 1000); return () => window.clearTimeout(timer); }, [remaining, navigate]);
  const featured = (player: Player | undefined, title: string, icon: string, tone: string) => player && <Paper sx={{ p: 2.5, flex: 1, minWidth: 0, backgroundImage: `linear-gradient(135deg, ${tone}, rgba(16,19,43,.92))`, borderColor: tone }}><Typography variant="overline">{icon} {title}</Typography><Typography variant="h5" noWrap>{player.name}</Typography><Typography color="secondary.main" fontWeight={900} fontSize="1.35rem">{player.score} points</Typography></Paper>;
  return <Container maxWidth="md" sx={{ pt: { xs: 5, md: 9 }, pb: 5 }}>
    <Paper sx={{ p: { xs: 2.5, sm: 4 }, textAlign: 'center' }}>
      <Typography className="game-logo" variant="h6"><span>★</span> Match results</Typography>
      <Typography variant="h3" mt={2}>That’s a wrap!</Typography>
      <Typography color="text.secondary" mb={3}>Final points — returning to the main page in {remaining} seconds.</Typography>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mb={3}>{featured(winner, 'Winner', '👑', 'rgba(245,158,11,.25)')}{featured(runnerUp, 'Runner-up', '🥈', 'rgba(148,163,184,.22)')}</Stack>
      {others.length > 0 && <Box className="glass-inset" textAlign="left" p={2}><Typography variant="h6" mb={1}>Full ranking</Typography>{others.map((player, index) => <Box key={player.id} display="flex" alignItems="center" justifyContent="space-between" py={1} borderBottom={index < others.length - 1 ? '1px solid rgba(255,255,255,.08)' : 'none'}><Typography><Box component="span" color="text.secondary" mr={1}>#{index + 3}</Box>{player.name}</Typography><Typography fontWeight={800}>{player.score} pts</Typography></Box>)}</Box>}
      <Button sx={{ mt: 3 }} variant="contained" onClick={() => navigate('/')}>Create or join a new room →</Button>
    </Paper>
  </Container>;
}
