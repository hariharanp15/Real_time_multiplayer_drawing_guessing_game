export type Player = { id: number; name: string; score: number };
export type Stroke = { points: {x:number;y:number}[]; color: string; size: number; erase?: boolean };
export type EventMessage = { event: string; data: any };
