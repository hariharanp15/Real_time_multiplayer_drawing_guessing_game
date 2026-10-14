import { Paper, Typography } from '@mui/material'; import { PlayerList } from './PlayerList'; import type { Player } from '../types';
export function Scoreboard({players,drawerId}:{players:Player[];drawerId?:number}) { return <Paper sx={{p:2}}><Typography variant="h6">🏆 Scoreboard</Typography><PlayerList players={[...players].sort((a,b)=>b.score-a.score)} drawerId={drawerId}/></Paper> }
