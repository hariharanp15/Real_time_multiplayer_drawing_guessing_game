import { Alert, Box, Button, Chip, Container, Grid, Paper, Typography } from '@mui/material';
import { DrawingCanvas } from '../components/DrawingCanvas';
import { GuessPanel } from '../components/GuessPanel';
import { Scoreboard } from '../components/Scoreboard';
import type { Player, Stroke } from '../types';

type Props = { playerId: number; players: Player[]; drawerId?: number; word: string; seconds: number; round: number; totalRounds: number; isAdmin: boolean; strokes: Stroke[]; messages: string[]; onStroke: (x: Stroke) => void; onClear: () => void; onGuess: (x: string) => void; onEnd: () => void };

export function GamePage({ playerId, players, drawerId, word, seconds, round, totalRounds, isAdmin, strokes, messages, onStroke, onClear, onGuess, onEnd }: Props) {
  const drawer = drawerId === playerId;
  return <Container maxWidth="xl" sx={{ py: { xs: 2, md: 4 } }}>
    <Paper sx={{ p: { xs: 2, sm: 2.5 }, mb: 2 }}>
      <Box display="flex" alignItems="center" justifyContent="space-between" gap={2}>
        <Box>
          <Typography className="game-logo" variant="body1"><span>✦</span> Sketch & Guess</Typography>
          <Typography variant="h4" mt={1}>{drawer ? `Your word: ${word}` : `Guess: ${word}`}</Typography>
          <Typography color="text.secondary">Round {round} of {totalRounds}</Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip color={seconds < 15 ? 'error' : 'primary'} label={`${seconds}s`} />
          {isAdmin && <Button color="error" variant="outlined" onClick={onEnd}>End game</Button>}
        </Box>
      </Box>
    </Paper>
    <Grid container spacing={2}>
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 1.5 }}><DrawingCanvas enabled={drawer} strokes={strokes} onStroke={onStroke} onClear={onClear} /></Paper>
        {drawer && <Alert severity="info" sx={{ mt: 1 }}>You are the drawer. Keep the word secret!</Alert>}
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2, mb: 2 }}><GuessPanel disabled={drawer} onGuess={onGuess} messages={messages} /></Paper>
        <Scoreboard players={players} drawerId={drawerId} />
      </Grid>
    </Grid>
  </Container>;
}
