import { useEffect, useRef, useState } from 'react';
import type { EventMessage } from '../types';
export function useGameSocket(code: string, playerId: number, onEvent: (e: EventMessage) => void) {
  const socket = useRef<WebSocket | null>(null); const handler = useRef(onEvent); const [connected, setConnected] = useState(false);
  useEffect(() => { handler.current = onEvent; }, [onEvent]);
  useEffect(() => { const base = (import.meta.env.VITE_WS_URL || 'ws://localhost:8000').replace(/\/$/, ''); const ws = new WebSocket(`${base}/ws/rooms/${code}/${playerId}`); socket.current = ws; ws.onopen = () => setConnected(true); ws.onclose = () => setConnected(false); ws.onmessage = e => handler.current(JSON.parse(e.data)); return () => ws.close(); }, [code, playerId]);
  return { connected, send: (event: string, data: object = {}) => socket.current?.readyState === WebSocket.OPEN && socket.current.send(JSON.stringify({ event, data })) };
}
