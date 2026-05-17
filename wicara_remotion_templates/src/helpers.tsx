import React, {CSSProperties, ReactNode} from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export type StepSpec = {title: string; body: string};
export type BaseTemplateSpec = {
  id: string;
  row_index: number;
  concept_type: string;
  template_id: string;
  media_engine_family: string;
  audience_level: string;
  language: string;
  fps: number;
  width: number;
  height: number;
  durationInFrames: number;
  title: string;
  subtitle: string;
  steps: StepSpec[];
  summary: string;
  [key: string]: unknown;
};

export const palette = {
  bg: '#0f172a',
  panel: '#111827',
  panelSoft: '#1f2937',
  text: '#f8fafc',
  subtext: '#cbd5e1',
  blue: '#60a5fa',
  green: '#34d399',
  yellow: '#fbbf24',
  red: '#f87171',
  purple: '#a78bfa',
  teal: '#2dd4bf',
  orange: '#fb923c',
  pink: '#f472b6'
};

export const sceneBg: CSSProperties = {
  background: `radial-gradient(circle at top left, #1e293b 0%, #0f172a 45%, #020617 100%)`,
  color: palette.text,
  fontFamily: 'Inter, Arial, sans-serif',
};

export const useAppear = (delay = 0, duration = 18) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [delay, delay + duration], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
};

export const useLift = (delay = 0, from = 24) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [delay, delay + 18], [from, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
};

export const Card: React.FC<{x: number; y: number; w: number; h: number; title?: string; color?: string; children?: ReactNode; opacity?: number;}> = ({x,y,w,h,title,color=palette.panelSoft,children,opacity=1}) => {
  return (
    <div style={{position:'absolute', left:x, top:y, width:w, height:h, border:`2px solid ${color}`, borderRadius:18, background:'rgba(15,23,42,0.72)', boxShadow:'0 10px 26px rgba(0,0,0,0.25)', padding:16, opacity}}>
      {title ? <div style={{fontSize:20, fontWeight:700, color, marginBottom:10}}>{title}</div> : null}
      {children}
    </div>
  );
};

export const Pill: React.FC<{x?: number; y?: number; text: string; color?: string;}> = ({x=0,y=0,text,color=palette.blue}) => (
  <div style={{position:'absolute', left:x, top:y, padding:'6px 12px', borderRadius:999, border:`1px solid ${color}`, color, fontSize:14, fontWeight:700, background:'rgba(255,255,255,0.04)'}}>{text}</div>
);

export const Stage: React.FC<{spec: BaseTemplateSpec; children: ReactNode; tag?: string;}> = ({spec, children, tag='Remotion template'}) => {
  const titleOpacity = useAppear(0, 16);
  return (
    <AbsoluteFill style={sceneBg}>
      <div style={{position:'absolute', left:48, top:34, opacity:titleOpacity}}>
        <div style={{fontSize:38, fontWeight:800, lineHeight:1.1}}>{spec.title}</div>
        <div style={{fontSize:18, lineHeight:1.4, color:palette.subtext, marginTop:10, width:860}}>{spec.subtitle}</div>
      </div>
      <Pill x={1030} y={38} text={`${tag} • ${spec.audience_level.toUpperCase()}`} color={palette.teal} />
      <Pill x={1030} y={78} text={spec.template_id} color={palette.purple} />
      {children}
      <div style={{position:'absolute', left:48, bottom:28, right:48, fontSize:18, color:palette.subtext, borderTop:'1px solid rgba(148,163,184,0.22)', paddingTop:14}}>{spec.summary}</div>
    </AbsoluteFill>
  );
};

export const StepRail: React.FC<{steps: StepSpec[]; x?: number; y?: number;}> = ({steps, x=920, y=160}) => {
  return (
    <div style={{position:'absolute', left:x, top:y, width:310}}>
      {steps.slice(0,3).map((step, i) => (
        <div key={i} style={{marginBottom:12, border:'1px solid rgba(148,163,184,0.2)', borderRadius:14, padding:12, background:'rgba(15,23,42,0.6)'}}>
          <div style={{fontSize:15, fontWeight:800, color:palette.yellow, marginBottom:4}}>Langkah {i+1}: {step.title}</div>
          <div style={{fontSize:13, lineHeight:1.35, color:palette.subtext}}>{step.body}</div>
        </div>
      ))}
    </div>
  );
};

export const NodeBox: React.FC<{x:number;y:number;label:string;w?:number;h?:number;color?:string;sub?:string;}> = ({x,y,label,w=140,h=56,color=palette.blue,sub}) => (
  <div style={{position:'absolute', left:x, top:y, width:w, height:h, borderRadius:14, border:`2px solid ${color}`, background:'rgba(15,23,42,0.82)', display:'flex', flexDirection:'column', justifyContent:'center', alignItems:'center', textAlign:'center', padding:'6px 10px', boxSizing:'border-box'}}>
    <div style={{fontSize:16, fontWeight:700, color}}>{label}</div>
    {sub ? <div style={{fontSize:11, color:palette.subtext, marginTop:2}}>{sub}</div> : null}
  </div>
);

export const Dot: React.FC<{x:number;y:number;r?:number;color?:string;label?:string;}> = ({x,y,r=12,color=palette.blue,label}) => (
  <>
    <div style={{position:'absolute', left:x-r, top:y-r, width:r*2, height:r*2, borderRadius:'50%', background:color, boxShadow:`0 0 18px ${color}55`}} />
    {label ? <div style={{position:'absolute', left:x+16, top:y-8, fontSize:14, color:palette.text}}>{label}</div> : null}
  </>
);

export const SvgLayer: React.FC<{children: ReactNode;}> = ({children}) => (
  <svg viewBox="0 0 1280 720" style={{position:'absolute', inset:0, width:'100%', height:'100%'}}>{children}</svg>
);

export const lineStyle = {stroke: '#94a3b8', strokeWidth: 3, fill: 'none'} as const;
export const arrowMarker = (
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
    </marker>
  </defs>
);

export const LegendList: React.FC<{title: string; items: string[]; x:number; y:number; color?: string;}> = ({title, items, x, y, color=palette.green}) => (
  <Card x={x} y={y} w={220} h={Math.max(120, 44 + items.length * 22)} title={title} color={color}>
    <div style={{display:'flex', flexDirection:'column', gap:8}}>
      {items.map((it, idx) => (
        <div key={idx} style={{fontSize:14, color:palette.subtext}}>• {it}</div>
      ))}
    </div>
  </Card>
);