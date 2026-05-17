import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Sequence, Easing} from 'remotion';
import {RemotionConceptSpec, VideoStep} from '../types';

export const colors = {
  bg:'#07111f', panel:'#0d1c31', panel2:'#10253d', text:'#f3f8ff', muted:'#a8bdd6',
  cyan:'#5ee7ff', blue:'#5aa7ff', purple:'#a78bfa', pink:'#ff6b9b', red:'#ff5565',
  yellow:'#ffd166', green:'#77f2a8', orange:'#ff9f1c', white:'#f8fafc', dark:'#06111f'
};
export const clamp = (v:number, min=0, max=1) => Math.max(min, Math.min(max, v));
export const fade = (frame:number, start:number, end:number) => interpolate(frame,[start,end],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
export const fadeOut = (frame:number, start:number, end:number) => interpolate(frame,[start,end],[1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
export const stageProgress = (frame:number, step?:VideoStep) => !step ? 0 : clamp((frame-step.start)/step.duration);
export const activeStep = (steps:VideoStep[], frame:number) => [...steps].reverse().find((s)=>frame>=s.start) ?? steps[0];

export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = Math.sin(frame/85)*16;
  return <AbsoluteFill style={{background:'radial-gradient(circle at 20% 10%, rgba(94,231,255,.18), transparent 24%), radial-gradient(circle at 82% 78%, rgba(167,139,250,.16), transparent 30%), #07111f', overflow:'hidden'}}>
    <div style={{position:'absolute', inset:0, backgroundImage:'linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px)', backgroundSize:'54px 54px', opacity:.16, transform:`translate(${drift}px,${drift*.5}px)`}} />
    <div style={{position:'absolute', width:520, height:520, borderRadius:999, background:'rgba(94,231,255,.08)', filter:'blur(50px)', left:-180, top:-120}} />
    <div style={{position:'absolute', width:520, height:520, borderRadius:999, background:'rgba(255,107,155,.07)', filter:'blur(55px)', right:-120, bottom:-160}} />
  </AbsoluteFill>;
};

export const TitleCard: React.FC<{spec:RemotionConceptSpec}> = ({spec}) => {
  const frame = useCurrentFrame(); const {fps}=useVideoConfig();
  const s = spring({frame, fps, config:{damping:150, stiffness:120, mass:.7}});
  const out = fadeOut(frame,72,90);
  return <AbsoluteFill style={{justifyContent:'center', alignItems:'center', opacity:out, transform:`scale(${.92+s*.08})`}}>
    <div style={{width:960, padding:'48px 58px', borderRadius:36, background:'linear-gradient(180deg, rgba(16,38,64,.94), rgba(8,18,34,.94))', border:'1px solid rgba(255,255,255,.14)', boxShadow:'0 28px 100px rgba(0,0,0,.45)', textAlign:'center'}}>
      <div style={{fontSize:24, color:colors.cyan, fontWeight:900, marginBottom:14, letterSpacing:1}}>WICARA VISUAL TEMPLATE • {spec.domain.toUpperCase()}</div>
      <div style={{fontSize:54, lineHeight:1.08, fontWeight:950, letterSpacing:-2.2, color:colors.text}}>{spec.title}</div>
      <div style={{marginTop:18, fontSize:24, lineHeight:1.36, color:colors.muted}}>{spec.subtitle}</div>
    </div>
  </AbsoluteFill>;
};

export const StepPanel: React.FC<{spec:RemotionConceptSpec}> = ({spec}) => {
  const frame = useCurrentFrame();
  const step = activeStep(spec.steps, frame);
  const local = frame-step.start;
  const appear = fade(local,0,18);
  const bar = clamp(local/step.duration);
  return <div style={{position:'absolute', left:56, bottom:38, width:770, borderRadius:26, padding:'21px 26px', background:'linear-gradient(180deg, rgba(15,35,60,.92), rgba(6,15,29,.94))', border:'1px solid rgba(255,255,255,.14)', boxShadow:'0 20px 70px rgba(0,0,0,.45)', opacity:appear}}>
    <div style={{fontSize:24, color:colors.text, fontWeight:950, letterSpacing:-.5}}>{step.title}</div>
    <div style={{marginTop:8, fontSize:20, lineHeight:1.38, color:colors.muted}}>{step.narration}</div>
    <div style={{marginTop:14, height:7, width:'100%', borderRadius:99, background:'rgba(255,255,255,.12)', overflow:'hidden'}}><div style={{height:'100%', width:`${bar*100}%`, background:`linear-gradient(90deg, ${colors.cyan}, ${colors.green})`, borderRadius:99}} /></div>
  </div>;
};

export const KeyIdea: React.FC<{spec:RemotionConceptSpec}> = ({spec}) => {
  const frame=useCurrentFrame(); const op=fade(frame,110,160)*fadeOut(frame,1210,1270);
  return <div style={{position:'absolute', right:54, top:44, width:312, padding:'18px 20px', borderRadius:22, background:'rgba(255,255,255,.07)', border:'1px solid rgba(255,255,255,.14)', color:colors.muted, fontSize:17, lineHeight:1.35, opacity:op}}>
    <div style={{color:colors.text, fontSize:22, fontWeight:950, marginBottom:8}}>Key idea</div>{spec.keyIdea}
  </div>;
};

export const LabelTag: React.FC<{x:number;y:number;text:string;color?:string;opacity?:number}> = ({x,y,text,color=colors.cyan,opacity=1}) => <div style={{position:'absolute', left:x, top:y, padding:'9px 13px', borderRadius:999, background:'rgba(255,255,255,.09)', border:`1px solid ${color}88`, color, fontSize:17, fontWeight:850, boxShadow:`0 0 20px ${color}33`, opacity, whiteSpace:'nowrap'}}>{text}</div>;

export const Callout: React.FC<{x1:number;y1:number;x2:number;y2:number;color?:string;opacity?:number}> = ({x1,y1,x2,y2,color=colors.cyan,opacity=1}) => <svg width="1280" height="720" style={{position:'absolute', inset:0, opacity, pointerEvents:'none'}}><defs><marker id="calloutArrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill={color}/></marker></defs><line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth="3" strokeLinecap="round" strokeDasharray="7 7" markerEnd="url(#calloutArrow)"/></svg>;

export const FinalSummary: React.FC<{spec:RemotionConceptSpec}> = ({spec}) => {
  const frame=useCurrentFrame(); const op=fade(frame,1230,1285);
  return <AbsoluteFill style={{justifyContent:'center', alignItems:'center', opacity:op, background:'radial-gradient(circle at center, rgba(7,17,31,.90), rgba(7,17,31,.35), rgba(7,17,31,0))'}}>
    <div style={{width:930, borderRadius:34, padding:'40px 54px', background:'linear-gradient(180deg, rgba(16,40,68,.96), rgba(7,16,31,.96))', border:'1px solid rgba(255,255,255,.16)', boxShadow:'0 24px 110px rgba(0,0,0,.58)', textAlign:'center'}}>
      <div style={{fontSize:42, fontWeight:950, color:colors.text, letterSpacing:-1, marginBottom:22}}>Ringkasan</div>
      <div style={{fontSize:25, lineHeight:1.44, color:colors.muted}}>{spec.summarySequence.join(' → ')}</div>
    </div>
  </AbsoluteFill>;
};

export const VideoShell: React.FC<{spec:RemotionConceptSpec; children:React.ReactNode; zoom?:number}> = ({spec, children, zoom=1}) => {
  const frame=useCurrentFrame();
  const cameraZoom = interpolate(frame,[90,520,980],[1,1.035,zoom],{extrapolateLeft:'clamp',extrapolateRight:'clamp', easing:Easing.inOut(Easing.ease)});
  return <AbsoluteFill>
    <Background />
    <div style={{position:'absolute', inset:0, transform:`scale(${cameraZoom})`, transformOrigin:'center'}}>{children}</div>
    <StepPanel spec={spec}/><KeyIdea spec={spec}/><FinalSummary spec={spec}/>
    <Sequence from={0} durationInFrames={95}><TitleCard spec={spec}/></Sequence>
  </AbsoluteFill>;
};

export const SafeBox: React.FC<{x:number;y:number;w:number;h:number;children?:React.ReactNode;title?:string;color?:string;opacity?:number}> = ({x,y,w,h,children,title,color=colors.cyan,opacity=1}) => <div style={{position:'absolute', left:x, top:y, width:w, height:h, borderRadius:24, background:'rgba(9,20,36,.44)', border:`1px solid ${color}55`, boxShadow:'0 24px 80px rgba(0,0,0,.25)', opacity, overflow:'hidden'}}>{title && <div style={{position:'absolute', left:22, top:18, fontSize:22, fontWeight:950, color}}>{title}</div>}{children}</div>;