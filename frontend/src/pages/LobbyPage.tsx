import { Box, Button, Paper, Stack, Typography } from '@mui/material';
import { PlayerList } from '../components/PlayerList';
import type { Player } from '../types';

type Props = { code: string; players: Player[]; ready: number[]; playerId: number; adminId?: number; onReady: () => void; onStart: () => void };

export function LobbyPage({ code, players, ready, playerId, adminId, onReady, onStart }: Props) {
  const isAdmin = playerId === adminId;
  const allReady = players.length >= 2 && players.every(player => ready.includes(player.id));
  const readyCount = players.filter(player => ready.includes(player.id)).length;
  return <Paper sx={{ p: { xs: 2.5, sm: 4 }, maxWidth: 680, mx: 'auto', mt: { xs: 3, sm: 7 } }}>
    <Typography className="game-logo" variant="h6"><span>✦</span> Waiting room</Typography>
    <Box className="glass-inset" textAlign="center" py={2} mt={2}>
      <Typography variant="overline" color="secondary.main">Share this room code</Typography>
      <Typography variant="h2" letterSpacing={8}>{code}</Typography>
    </Box>
    <Typography color="text.secondary" mt={2}>{isAdmin ? 'You are the room admin. The game unlocks when every player is ready.' : 'Get ready — the admin starts once the whole squad is ready.'}</Typography>
    <Box className="glass-inset" px={2} mt={2}><PlayerList players={players} ready={ready} /></Box>
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mt={3}>
      <Button fullWidth variant="outlined" onClick={onReady}>{ready.includes(playerId) ? 'Cancel ready' : 'I am ready'}</Button>
      {isAdmin && <Button fullWidth variant="contained" onClick={onStart} disabled={!allReady}>Start game ({readyCount}/{players.length} ready)</Button>}
    </Stack>
  </Paper>;
}
