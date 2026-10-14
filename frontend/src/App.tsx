import { useCallback, useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { Alert, CssBaseline } from '@mui/material';
import { LobbyPage } from './pages/LobbyPage';
import { GamePage } from './pages/GamePage';
import { FinalLeaderboardPage } from './pages/FinalLeaderboardPage';
import { useGameSocket } from './hooks/useGameSocket';
import type { EventMessage, Player, Stroke } from './types';

export default function App() {
  const { code = '' } = useParams(); const playerId = Number(new URLSearchParams(useLocation().search).get('player'));
  const [phase, setPhase] = useState('lobby'); const [players, setPlayers] = useState<Player[]>([]); const [ready, setReady] = useState<number[]>([]); const [adminId, setAdminId] = useState<number>();
  const [drawerId, setDrawerId] = useState<number>(); const [word, setWord] = useState(''); const [seconds, setSeconds] = useState(0); const [round, setRound] = useState(0); const [totalRounds, setTotalRounds] = useState(0);
  const [strokes, setStrokes] = useState<Stroke[]>([]); const [messages, setMessages] = useState<string[]>([]); const [notice, setNotice] = useState('');
  const onEvent = useCallback((m: EventMessage) => { const d = m.data; switch (m.event) {
    case 'lobby_update': setPlayers(d.players); setReady(d.ready); setAdminId(d.room.adminPlayerId); setRound(d.room.currentRound); setTotalRounds(d.room.totalRounds); if (d.room.status === 'playing') setPhase('game'); break;
    case 'round_started': setPhase('game'); setDrawerId(d.drawerId); setRound(d.round); setTotalRounds(d.totalRounds); setWord('_ '.repeat(d.wordLength)); setSeconds(d.seconds); setStrokes([]); setMessages([]); break;
    case 'secret_word': setWord(d.word); break; case 'timer': setSeconds(d.remaining); break; case 'canvas_state': setStrokes(d.strokes); break;
    case 'stroke': if (d.senderId !== playerId) setStrokes(s => [...s, d]); break; case 'canvas_clear': setStrokes([]); break;
    case 'chat_guess': setMessages(x => [...x, `${players.find(p => p.id === d.playerId)?.name || 'A player'}: ${d.text}`]); break;
    case 'score_update': setPlayers(d.players); break; case 'round_ended': setWord(`Word: ${d.word}`); setPlayers(d.scores); setNotice(`Round ended: ${d.reason}`); break;
    case 'game_completed': setPlayers(d.leaderboard); setPhase('final'); break; case 'error': setNotice(d.message); break;
  } }, [players, playerId]);
  const { connected, send } = useGameSocket(code, playerId, onEvent);
  if (!playerId) return <Alert severity="error">Invalid player link.</Alert>;
  if (phase === 'final') return <FinalLeaderboardPage players={players} />;
  if (phase === 'lobby') return <><CssBaseline /><LobbyPage code={code} players={players} ready={ready} playerId={playerId} adminId={adminId} onReady={() => send('ready')} onStart={() => send('start_game')} />{!connected && <Alert severity="warning">Reconnecting…</Alert>}{notice && <Alert severity="info">{notice}</Alert>}</>;
  return <><CssBaseline /><GamePage playerId={playerId} players={players} drawerId={drawerId} word={word} seconds={seconds} round={round} totalRounds={totalRounds} isAdmin={adminId === playerId} strokes={strokes} messages={messages} onStroke={s => { setStrokes(x => [...x, s]); send('stroke', s); }} onClear={() => send('canvas_clear')} onGuess={text => send('guess', { text })} onEnd={() => send('end_game')} /></>;
}
