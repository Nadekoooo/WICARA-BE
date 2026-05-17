import React from 'react';
import {useCurrentFrame} from 'remotion';
import {BaseTemplateSpec, Card, Dot, LegendList, NodeBox, Pill, Stage, StepRail, SvgLayer, arrowMarker, lineStyle, palette, useAppear} from './helpers';

const centerStyle = {display:'flex', alignItems:'center', justifyContent:'center'} as const;

const fadeStyle = (opacity:number, dx=0, dy=0) => ({opacity, transform:`translate(${dx}px, ${dy}px)`});

export const BioEcosystemNetworkTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const op = useAppear(12, 18);
  const nodes = (spec.nodes as string[]) || [];
  const threats = (spec.threats as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={44} y={150} w={820} h={460} title={String(spec.central_node || 'Ekosistem')} color={palette.green} opacity={op}>
      <SvgLayer>{arrowMarker}
        <line x1="265" y1="180" x2="385" y2="88" {...lineStyle} markerEnd="url(#arrow)" />
        <line x1="405" y1="180" x2="515" y2="88" {...lineStyle} markerEnd="url(#arrow)" />
        <line x1="545" y1="180" x2="635" y2="88" {...lineStyle} markerEnd="url(#arrow)" />
        <line x1="265" y1="180" x2="385" y2="300" {...lineStyle} markerEnd="url(#arrow)" />
        <line x1="405" y1="180" x2="515" y2="300" {...lineStyle} markerEnd="url(#arrow)" />
        <line x1="545" y1="180" x2="635" y2="300" {...lineStyle} markerEnd="url(#arrow)" />
      </SvgLayer>
      <NodeBox x={300} y={175} label={String(spec.central_node || 'Ekosistem')} w={180} h={70} color={palette.green} />
      {nodes.slice(0,6).map((n, i) => {
        const pos = [[160,80],[360,80],[560,80],[160,300],[360,300],[560,300]][i];
        return <NodeBox key={i} x={pos[0]} y={pos[1]} label={n} w={150} h={58} color={[palette.blue,palette.teal,palette.yellow,palette.purple,palette.orange,palette.red][i%6]} />;
      })}
    </Card>
    <LegendList title="Gangguan" items={threats} x={70} y={490} color={palette.red} />
  </Stage>;
};

export const BioOrganSystemFlowTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const systems = (spec.systems as string[]) || [];
  const regs = (spec.regulators as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={50} y={170} w={830} h={420} title="Aliran antar sistem" color={palette.blue}>
      {systems.slice(0,4).map((s, i) => <NodeBox key={i} x={80+i*180} y={160} label={s} w={140} h={64} color={[palette.orange,palette.red,palette.blue,palette.green][i]} />)}
      <SvgLayer>{arrowMarker}
        <line x1="200" y1="362" x2="380" y2="362" {...lineStyle} markerEnd="url(#arrow)"/>
        <line x1="380" y1="362" x2="560" y2="362" {...lineStyle} markerEnd="url(#arrow)"/>
        <line x1="560" y1="362" x2="740" y2="362" {...lineStyle} markerEnd="url(#arrow)"/>
        <line x1="420" y1="130" x2="420" y2="190" {...lineStyle} markerEnd="url(#arrow)"/>
        <line x1="560" y1="130" x2="560" y2="190" {...lineStyle} markerEnd="url(#arrow)"/>
      </SvgLayer>
      <NodeBox x={300} y={60} label={regs[0] || 'Otak'} w={150} h={56} color={palette.purple} />
      <NodeBox x={500} y={60} label={regs[1] || 'Hormon'} w={150} h={56} color={palette.purple} />
      <div style={{position:'absolute', left:120, top:255, fontSize:17, color:palette.subtext}}>nutrisi</div>
      <div style={{position:'absolute', left:300, top:255, fontSize:17, color:palette.subtext}}>oksigen</div>
      <div style={{position:'absolute', left:500, top:255, fontSize:17, color:palette.subtext}}>zat sisa</div>
    </Card>
  </Stage>;
};

export const EarthSpaceSystemTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const bodies = (spec.bodies as string[]) || [];
  const phenomena = (spec.phenomena as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={45} y={155} w={840} h={445} title="Model benda langit" color={palette.yellow}>
      <SvgLayer>
        <circle cx="250" cy="300" r="62" fill="#fbbf24" opacity="0.95" />
        <circle cx="510" cy="300" r="38" fill="#60a5fa" opacity="0.95" />
        <circle cx="615" cy="260" r="18" fill="#cbd5e1" opacity="0.95" />
        <ellipse cx="510" cy="300" rx="175" ry="115" stroke="#475569" strokeWidth="3" fill="none" />
        <ellipse cx="510" cy="300" rx="100" ry="65" stroke="#334155" strokeWidth="2" fill="none" />
      </SvgLayer>
      <Pill x={180} y={240} text={bodies[0] || 'Matahari'} color={palette.yellow} />
      <Pill x={470} y={340} text={bodies[1] || 'Bumi'} color={palette.blue} />
      <Pill x={625} y={245} text={bodies[2] || 'Bulan'} color={palette.subtext} />
      <LegendList title="Fenomena" items={phenomena} x={620} y={95} color={palette.teal} />
    </Card>
  </Stage>;
};

export const ChemBondingMoleculeTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const examples = (spec.examples as string[]) || [];
  const bondTypes = (spec.bond_types as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={50} y={170} w={540} h={400} title="Contoh molekul" color={palette.teal}>
      <div style={{position:'absolute', left:40, top:90}}><MoleculePreview label={examples[0] || 'NaCl'} type="ionic" /></div>
      <div style={{position:'absolute', left:210, top:90}}><MoleculePreview label={examples[1] || 'H₂O'} type="bent" /></div>
      <div style={{position:'absolute', left:380, top:90}}><MoleculePreview label={examples[2] || 'CO₂'} type="linear" /></div>
      <div style={{position:'absolute', left:210, top:240}}><MoleculePreview label={examples[3] || 'NH₃'} type="pyramid" /></div>
    </Card>
    <LegendList title="Jenis ikatan" items={bondTypes} x={640} y={200} color={palette.orange} />
  </Stage>;
};

const MoleculePreview: React.FC<{label:string; type:string}> = ({label, type}) => {
  const positions: Record<string, [number,number][]> = {
    ionic: [[35,55],[95,55]],
    bent: [[35,70],[95,70],[65,28]],
    linear: [[20,55],[65,55],[110,55]],
    pyramid: [[30,90],[100,90],[65,45],[65,12]],
  };
  const pts = positions[type] || positions.linear;
  return <div style={{position:'relative', width:130, height:120}}>
    <svg width="130" height="120">
      {pts.length>1 ? pts.slice(1).map((p, i)=><line key={i} x1={pts[0][0]} y1={pts[0][1]} x2={p[0]} y2={p[1]} stroke="#94a3b8" strokeWidth="3" />):null}
    </svg>
    {pts.map((p, i)=><div key={i} style={{position:'absolute', left:p[0]-12, top:p[1]-12, width:24, height:24, borderRadius:'50%', background:[palette.blue,palette.red,palette.green,palette.yellow][i%4]}} />)}
    <div style={{position:'absolute', left:0, bottom:0, width:'100%', textAlign:'center', color:palette.text, fontSize:14}}>{label}</div>
  </div>;
};

export const BioFlowSystemTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const systems = (spec.systems as string[]) || [];
  const outputs = (spec.outputs as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={60} y={160} w={830} h={430} title="Sistem tubuh" color={palette.green}>
      <div style={{position:'absolute', left:120, top:60, width:180, height:300, border:'2px dashed rgba(148,163,184,0.45)', borderRadius:30}} />
      {systems.slice(0,4).map((s, i) => <NodeBox key={i} x={340 + (i%2)*190} y={90 + Math.floor(i/2)*120} label={s} w={160} h={70} color={[palette.orange,palette.blue,palette.red,palette.purple][i]} />)}
      <SvgLayer>{arrowMarker}
        <line x1="300" y1="190" x2="340" y2="125" {...lineStyle} markerEnd="url(#arrow)"/>
        <line x1="300" y1="240" x2="340" y2="245" {...lineStyle} markerEnd="url(#arrow)"/>
        <line x1="300" y1="290" x2="340" y2="365" {...lineStyle} markerEnd="url(#arrow)"/>
      </SvgLayer>
      <LegendList title="Keluaran penting" items={outputs} x={610} y={315} color={palette.teal} />
    </Card>
  </Stage>;
};

export const BioTaxonomyBiodiversityTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const levels = (spec.levels as string[]) || [];
  const examples = (spec.biodiversity_examples as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={55} y={170} w={400} h={410} title="Tangga klasifikasi" color={palette.purple}>
      {levels.slice(0,5).map((l, i) => <NodeBox key={i} x={60+i*18} y={70+i*56} label={l} w={260-i*15} h={44} color={palette.purple} />)}
    </Card>
    <Card x={490} y={170} w={390} h={410} title="Keanekaragaman" color={palette.green}>
      {examples.slice(0,3).map((e, i) => <NodeBox key={i} x={30 + (i%2)*180} y={90 + Math.floor(i/2)*120} label={e} w={150} h={72} color={[palette.green,palette.teal,palette.blue][i]} />)}
      <div style={{position:'absolute', left:30, bottom:40, width:320, color:palette.subtext, lineHeight:1.4}}>Konservasi menjaga keragaman pada tingkat gen, spesies, dan ekosistem.</div>
    </Card>
  </Stage>;
};

export const BioBiotechProcessTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const pipe = (spec.pipeline as string[]) || [];
  const ex = (spec.examples as string[]) || [];
  const ethics = (spec.ethics as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={50} y={180} w={840} h={390} title="Pipeline bioteknologi" color={palette.teal}>
      {pipe.slice(0,3).map((p, i) => <NodeBox key={i} x={85+i*240} y={110} label={p} w={180} h={80} color={[palette.green,palette.blue,palette.orange][i]} />)}
      <SvgLayer>{arrowMarker}<line x1="265" y1="330" x2="325" y2="330" {...lineStyle} markerEnd="url(#arrow)"/><line x1="505" y1="330" x2="565" y2="330" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
      <LegendList title="Contoh" items={ex} x={85} y={240} color={palette.yellow} />
      <LegendList title="Etika" items={ethics} x={575} y={240} color={palette.red} />
    </Card>
  </Stage>;
};

export const ChemAtomicPeriodicTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const subs = (spec.subparticles as string[]) || [];
  const groups = (spec.periodic_groups as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={55} y={170} w={360} h={410} title="Model atom" color={palette.blue}>
      <SvgLayer>
        <circle cx="235" cy="375" r="42" fill="#fb923c" opacity="0.9" />
        <circle cx="235" cy="375" r="96" stroke="#60a5fa" strokeWidth="3" fill="none" />
        <circle cx="235" cy="375" r="140" stroke="#a78bfa" strokeWidth="3" fill="none" />
      </SvgLayer>
      <Dot x={235} y={375} r={10} color={palette.yellow} label={String(spec.example_element || 'Na')} />
      <Dot x={235} y={279} r={8} color={palette.blue} />
      <Dot x={375} y={375} r={8} color={palette.purple} />
      <LegendList title="Partikel" items={subs} x={80} y={105} color={palette.orange} />
    </Card>
    <Card x={455} y={170} w={425} h={410} title="Sistem periodik" color={palette.green}>
      {groups.slice(0,3).map((g,i)=><NodeBox key={i} x={40+i*120} y={80} label={g} w={110} h={54} color={palette.green} />)}
      <div style={{position:'absolute', left:40, top:170, display:'grid', gridTemplateColumns:'repeat(6, 54px)', gap:10}}>
        {Array.from({length:18}).map((_,i)=><div key={i} style={{width:54,height:54,borderRadius:10,border:'1px solid rgba(148,163,184,0.4)', background:i===0||i===5||i===11? 'rgba(52,211,153,0.18)':'rgba(255,255,255,0.03)'}} />)}
      </div>
    </Card>
  </Stage>;
};

export const ChemAcidBaseTitrationTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const samples = (spec.samples as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={45} y={170} w={400} h={400} title="Skala pH" color={palette.teal}>
      <div style={{position:'absolute', left:40, top:125, width:300, height:26, borderRadius:14, background:'linear-gradient(90deg, #ef4444 0%, #fbbf24 50%, #22c55e 100%)'}} />
      <div style={{position:'absolute', left:38, top:165, width:304, display:'flex', justifyContent:'space-between', color:palette.subtext, fontSize:13}}>{Array.from({length:15}).map((_,i)=><span key={i}>{i}</span>)}</div>
      {samples.slice(0,4).map((s, i)=><Pill key={i} x={35 + i*80} y={215 + (i%2)*42} text={s} color={[palette.red,palette.orange,palette.blue,palette.green][i]} />)}
    </Card>
    <Card x={480} y={170} w={405} h={400} title="Setup titrasi" color={palette.purple}>
      <SvgLayer>
        <rect x="560" y="210" width="12" height="150" fill="#94a3b8"/>
        <rect x="538" y="195" width="56" height="15" rx="6" fill="#94a3b8"/>
        <rect x="560" y="150" width="12" height="45" fill="#cbd5e1"/>
        <path d="M 655 360 L 735 360 L 710 260 L 680 260 Z" fill="#1d4ed8" opacity="0.3" stroke="#60a5fa" strokeWidth="3"/>
        <path d="M 566 195 L 566 240" stroke="#f8fafc" strokeWidth="3"/>
      </SvgLayer>
      <Pill x={530} y={115} text={String(spec.indicator || 'Fenolftalein')} color={palette.purple} />
      <div style={{position:'absolute', left:520, top:390, color:palette.subtext, fontSize:14}}>Titik ekuivalen sekitar pH {String(spec.equivalence_ph || 7)}</div>
    </Card>
  </Stage>;
};

export const SdEcosystemFoodChainTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const chain = (spec.chain as string[]) || [];
  const adaptations = (spec.adaptations as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={45} y={175} w={840} h={400} title={String(spec.habitat || 'Habitat')} color={palette.green}>
      {chain.slice(0,5).map((c, i) => <NodeBox key={i} x={60+i*145} y={150} label={c} w={120} h={66} color={[palette.green,palette.yellow,palette.teal,palette.purple,palette.red][i]} />)}
      <SvgLayer>{arrowMarker}{Array.from({length:4}).map((_,i)=><line key={i} x1={180+i*145} y1="358" x2={205+i*145} y2="358" {...lineStyle} markerEnd="url(#arrow)"/>)}</SvgLayer>
      <LegendList title="Adaptasi" items={adaptations} x={610} y={70} color={palette.orange} />
    </Card>
  </Stage>;
};

export const SdEnergyFormsTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const forms = (spec.forms as string[]) || [];
  const ex = (spec.examples as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={170} w={840} h={405} title="Bentuk energi" color={palette.yellow}>
      <NodeBox x={340} y={145} label="Energi" w={170} h={76} color={palette.yellow} />
      {forms.slice(0,5).map((f, i) => <NodeBox key={i} x={[80,240,600,120,560][i]} y={[95,300,95,200,300][i]} label={f} w={130} h={58} color={[palette.red,palette.blue,palette.purple,palette.orange,palette.green][i]} />)}
      <LegendList title="Contoh alat" items={ex} x={610} y={185} color={palette.teal} />
    </Card>
  </Stage>;
};

export const BioStructureLabelingTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const parts = (spec.parts as string[]) || [];
  const clas = (spec.classification as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={55} y={170} w={520} h={420} title={String(spec.organism || 'Organisme')} color={palette.green}>
      <SvgLayer>
        <line x1="300" y1="370" x2="300" y2="250" stroke="#34d399" strokeWidth="8" />
        <ellipse cx="255" cy="300" rx="48" ry="18" fill="#22c55e" opacity="0.5" transform="rotate(-30 255 300)"/>
        <ellipse cx="345" cy="300" rx="48" ry="18" fill="#22c55e" opacity="0.5" transform="rotate(30 345 300)"/>
        <ellipse cx="255" cy="240" rx="48" ry="18" fill="#22c55e" opacity="0.5" transform="rotate(-30 255 240)"/>
        <ellipse cx="345" cy="240" rx="48" ry="18" fill="#22c55e" opacity="0.5" transform="rotate(30 345 240)"/>
        <circle cx="300" cy="205" r="24" fill="#fbbf24" opacity="0.9"/>
      </SvgLayer>
      {parts.slice(0,4).map((p,i)=><Pill key={i} x={[40,40,390,390][i]} y={[320,250,250,175][i]} text={p} color={[palette.orange,palette.teal,palette.blue,palette.yellow][i]} />)}
      <LegendList title="Klasifikasi" items={clas} x={315} y={305} color={palette.purple} />
    </Card>
  </Stage>;
};

export const BioVirusLifecycleTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const stages = (spec.stages as string[]) || [];
  const prevention = (spec.prevention as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={55} y={170} w={540} h={420} title="Siklus virus" color={palette.red}>
      {stages.slice(0,5).map((s, i) => <NodeBox key={i} x={[90,285,420,285,90][i]} y={[55,95,210,325,365][i]} label={s} w={120} h={52} color={palette.red} />)}
      <SvgLayer>{arrowMarker}
        <path d="M 250 95 Q 310 75 360 110" {...lineStyle} markerEnd="url(#arrow)" />
        <path d="M 480 250 Q 420 300 360 335" {...lineStyle} markerEnd="url(#arrow)" />
        <path d="M 225 392 Q 165 345 150 280" {...lineStyle} markerEnd="url(#arrow)" />
        <path d="M 135 155 Q 160 100 210 88" {...lineStyle} markerEnd="url(#arrow)" />
      </SvgLayer>
    </Card>
    <LegendList title="Pencegahan" items={prevention} x={640} y={230} color={palette.green} />
  </Stage>;
};

export const BioEvolutionSelectionTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const vars = (spec.variation as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={52} y={175} w={840} h={400} title="Seleksi alam" color={palette.orange}>
      <Pill x={90} y={95} text="Populasi awal" color={palette.blue} />
      {Array.from({length:8}).map((_,i)=><Dot key={i} x={150 + (i%4)*75} y={210 + Math.floor(i/4)*90} r={12} color={[palette.blue,palette.green,palette.orange][i%3]} label={i<3? vars[i] : undefined} />)}
      <NodeBox x={410} y={170} label={String(spec.environment || 'Lingkungan')} w={170} h={70} color={palette.red} />
      <SvgLayer>{arrowMarker}<line x1="330" y1="300" x2="410" y2="230" {...lineStyle} markerEnd="url(#arrow)"/><line x1="580" y1="230" x2="690" y2="300" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
      <Pill x={690} y={95} text="Populasi akhir" color={palette.green} />
      {Array.from({length:6}).map((_,i)=><Dot key={i} x={770 + (i%3)*75} y={210 + Math.floor(i/3)*90} r={12} color={i<4? palette.green:palette.orange} />)}
    </Card>
  </Stage>;
};

export const ChemParticleReactionRateTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const factors = (spec.factors as string[]) || [];
  const particles = (spec.particles as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={52} y={175} w={540} h={400} title="Tumbukan partikel" color={palette.yellow}>
      <div style={{position:'absolute', left:48, top:85, width:430, height:250, border:'2px solid rgba(148,163,184,0.45)', borderRadius:24}} />
      {Array.from({length:5}).map((_,i)=><Dot key={`a${i}`} x={120 + (i%3)*120} y={145 + Math.floor(i/3)*100} r={14} color={palette.blue} label={i===0?particles[0]:undefined} />)}
      {Array.from({length:5}).map((_,i)=><Dot key={`b${i}`} x={200 + (i%3)*115} y={195 + Math.floor(i/3)*90} r={14} color={palette.red} label={i===0?particles[1]:undefined} />)}
      <div style={{position:'absolute', left:262, top:210, width:34, height:34, background:palette.yellow, clipPath:'polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)'}} />
    </Card>
    <LegendList title="Faktor laju" items={factors} x={655} y={210} color={palette.teal} />
  </Stage>;
};

export const ChemRedoxElectrochemistryTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const halves = (spec.half_reactions as string[]) || [];
  const parts = (spec.cell_parts as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={45} y={170} w={850} h={410} title="Sel elektrokimia" color={palette.blue}>
      <SvgLayer>{arrowMarker}
        <rect x="120" y="250" width="130" height="160" rx="18" fill="rgba(96,165,250,0.12)" stroke="#60a5fa" strokeWidth="3"/>
        <rect x="410" y="250" width="130" height="160" rx="18" fill="rgba(52,211,153,0.12)" stroke="#34d399" strokeWidth="3"/>
        <rect x="165" y="190" width="14" height="130" fill="#cbd5e1"/>
        <rect x="455" y="190" width="14" height="130" fill="#cbd5e1"/>
        <path d="M 172 190 Q 320 115 462 190" stroke="#94a3b8" strokeWidth="4" fill="none"/>
        <line x1="252" y1="265" x2="402" y2="265" stroke="#a78bfa" strokeWidth="8"/>
      </SvgLayer>
      <Pill x={95} y={140} text={parts[0] || 'Anoda'} color={palette.blue} />
      <Pill x={383} y={140} text={parts[1] || 'Katoda'} color={palette.green} />
      <Pill x={275} y={282} text={parts[2] || 'Jembatan garam'} color={palette.purple} />
      <Pill x={80} y={430} text={halves[0] || 'Zn → Zn²⁺ + 2e⁻'} color={palette.blue} />
      <Pill x={400} y={430} text={halves[1] || 'Cu²⁺ + 2e⁻ → Cu'} color={palette.green} />
    </Card>
  </Stage>;
};

export const ChemOrganicStructureTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const examples = (spec.examples as any[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={45} y={180} w={845} h={390} title="Gugus fungsi" color={palette.teal}>
      {examples.slice(0,3).map((ex, i)=><Card key={i} x={75 + i*250} y={105} w={180} h={200} color={[palette.teal,palette.orange,palette.purple][i]} title={String(ex.name || 'Senyawa')}>
        <div style={{fontSize:34, fontWeight:800, textAlign:'center', marginTop:18}}>{String(ex.group || '-X')}</div>
        <div style={{fontSize:13, color:palette.subtext, textAlign:'center', marginTop:20}}>Kerangka karbon</div>
        <div style={{display:'flex', justifyContent:'center', gap:8, marginTop:14}}>{Array.from({length:4}).map((_,j)=><div key={j} style={{width:20,height:20,borderRadius:'50%', background:j===3? [palette.teal,palette.orange,palette.purple][i]: palette.subtext}} />)}</div>
      </Card>)}
    </Card>
  </Stage>;
};

export const SdBodySensesHealthTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const senses = (spec.senses as string[]) || [];
  const habits = (spec.habits as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={45} y={170} w={540} h={420} title="Pancaindra" color={palette.blue}>
      <div style={{position:'absolute', left:190, top:65, width:160, height:160, borderRadius:'50%', border:'3px solid rgba(248,250,252,0.65)'}} />
      {senses.slice(0,5).map((s,i)=><Pill key={i} x={[65,65,370,370,215][i]} y={[110,190,110,190,310][i]} text={s} color={[palette.blue,palette.green,palette.orange,palette.purple,palette.red][i]} />)}
    </Card>
    <LegendList title="Kebiasaan sehat" items={habits} x={650} y={245} color={palette.green} />
  </Stage>;
};

export const SdLifeCycleClassificationTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const groups = (spec.groups as string[]) || [];
  const cycle = (spec.life_cycle as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={175} w={360} h={390} title="Kelompok" color={palette.green}>
      {groups.slice(0,2).map((g,i)=><NodeBox key={i} x={75+i*155} y={125} label={g} w={130} h={90} color={[palette.green,palette.orange][i]} />)}
    </Card>
    <Card x={445} y={175} w={440} h={390} title="Siklus hidup" color={palette.purple}>
      {cycle.slice(0,4).map((c,i)=><NodeBox key={i} x={[80,250,250,80][i]} y={[85,85,245,245][i]} label={c} w={110} h={60} color={palette.purple} />)}
      <SvgLayer>{arrowMarker}<path d="M 565 265 Q 635 205 705 265" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 765 325 Q 700 385 635 325" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 575 385 Q 520 320 575 265" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
    </Card>
  </Stage>;
};

export const ChemAcidBaseSafetyTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const items = (spec.items as string[]) || [];
  const safety = (spec.safety as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={50} y={180} w={400} h={390} title="Contoh bahan" color={palette.orange}>
      {items.slice(0,4).map((it,i)=><NodeBox key={i} x={60 + (i%2)*170} y={85 + Math.floor(i/2)*120} label={it} w={130} h={70} color={[palette.red,palette.yellow,palette.blue,palette.green][i]} />)}
    </Card>
    <LegendList title="Aturan keselamatan" items={safety} x={560} y={220} color={palette.red} />
  </Stage>;
};

export const ChemLabSafetyTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const icons = (spec.icons as string[]) || [];
  const wf = (spec.workflow as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={170} w={840} h={410} title="Praktik laboratorium" color={palette.yellow}>
      {icons.slice(0,4).map((ic,i)=><NodeBox key={i} x={65+i*190} y={80} label={ic} w={150} h={68} color={[palette.blue,palette.orange,palette.green,palette.red][i]} />)}
      {wf.slice(0,3).map((s,i)=><NodeBox key={i} x={135+i*215} y={250} label={s} w={140} h={58} color={palette.teal} />)}
      <SvgLayer>{arrowMarker}<line x1="275" y1="452" x2="350" y2="452" {...lineStyle} markerEnd="url(#arrow)"/><line x1="490" y1="452" x2="565" y2="452" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
    </Card>
  </Stage>;
};

export const ChemParticleMatterTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const states = (spec.states as string[]) || [];
  const changes = (spec.changes as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={170} w={560} h={410} title="Model partikel" color={palette.blue}>
      {states.slice(0,3).map((s,i)=><Card key={i} x={25+i*175} y={90} w={160} h={200} color={[palette.green,palette.blue,palette.purple][i]} title={s}>
        <div style={{position:'relative', width:'100%', height:120}}>
          {Array.from({length: i===0?8:i===1?6:5}).map((_,j)=><div key={j} style={{position:'absolute', left:15 + (j%3)*40 + (i===2? j*6:0), top:20 + Math.floor(j/3)*35 + (i===1? (j%2)*10:0), width:18,height:18,borderRadius:'50%', background:[palette.green,palette.blue,palette.purple][i]}} />)}
        </div>
      </Card>)}
    </Card>
    <LegendList title="Perubahan" items={changes} x={690} y={235} color={palette.orange} />
  </Stage>;
};

export const SdInquiryObservationTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const skills = (spec.skills as string[]) || [];
  const objects = (spec.objects as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={175} w={840} h={395} title="Siklus inkuiri" color={palette.teal}>
      {skills.slice(0,4).map((s,i)=><NodeBox key={i} x={[95,320,545,320][i]} y={[95,60,95,250][i]} label={s} w={160} h={58} color={palette.teal} />)}
      <SvgLayer>{arrowMarker}<path d="M 255 285 Q 320 210 390 205" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 480 205 Q 555 210 620 285" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 560 350 Q 455 400 350 350" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 200 350 Q 130 255 175 180" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
      <LegendList title="Objek contoh" items={objects} x={640} y={220} color={palette.yellow} />
    </Card>
  </Stage>;
};

export const SdMatterStatesTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const states = (spec.states as string[]) || [];
  const examples = (spec.examples as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={46} y={170} w={840} h={405} title="Wujud zat" color={palette.blue}>
      {states.slice(0,3).map((s,i)=><Card key={i} x={45+i*260} y={90} w={210} h={210} color={[palette.teal,palette.blue,palette.purple][i]} title={s}>
        <div style={{display:'flex', justifyContent:'center', gap:18, flexWrap:'wrap', marginTop:12}}>{Array.from({length:6}).map((_,j)=><div key={j} style={{width:20,height:20,borderRadius:'50%', background:[palette.teal,palette.blue,palette.purple][i], opacity:i===2?0.7:1, transform:i===2?`translate(${j*6}px, ${j%2?8:-5}px)`:undefined}} />)}</div>
        <div style={{textAlign:'center', marginTop:25, color:palette.subtext}}>{examples[i] || ''}</div>
      </Card>)}
    </Card>
  </Stage>;
};

export const SdSolarSystemDayNightTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={46} y={170} w={840} h={405} title="Siang dan malam" color={palette.yellow}>
      <SvgLayer>
        <circle cx="180" cy="255" r="56" fill="#fbbf24" />
        <circle cx="500" cy="255" r="70" fill="#60a5fa" />
        <path d="M 500 185 A 70 70 0 0 1 500 325" fill="#0f172a" opacity="0.55"/>
        <circle cx="650" cy="195" r="22" fill="#e2e8f0" />
      </SvgLayer>
      <Pill x={110} y={155} text="Matahari" color={palette.yellow} />
      <Pill x={458} y={340} text="Bumi" color={palette.blue} />
      <Pill x={642} y={150} text="Bulan" color={palette.subtext} />
      <Pill x={405} y={185} text="Siang" color={palette.green} />
      <Pill x={535} y={185} text="Malam" color={palette.purple} />
    </Card>
  </Stage>;
};

export const SdEarthResourcesEnvironmentTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const res = (spec.resources as string[]) || [];
  const changes = (spec.changes as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={170} w={840} h={405} title="Permukaan Bumi" color={palette.green}>
      <div style={{position:'absolute', left:40, top:180, width:320, height:130, borderRadius:28, background:'linear-gradient(180deg, rgba(34,197,94,0.55), rgba(21,128,61,0.55))'}} />
      <div style={{position:'absolute', left:320, top:230, width:280, height:80, borderRadius:24, background:'linear-gradient(180deg, rgba(59,130,246,0.65), rgba(37,99,235,0.65))'}} />
      <LegendList title="Sumber daya" items={res} x={600} y={80} color={palette.yellow} />
      <LegendList title="Perubahan lingkungan" items={changes} x={600} y={280} color={palette.red} />
    </Card>
  </Stage>;
};

export const SdMixtureSeparationTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const mix = (spec.mixtures as string[]) || [];
  const methods = (spec.methods as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={50} y={175} w={390} h={400} title="Contoh campuran" color={palette.orange}>
      {mix.slice(0,3).map((m,i)=><NodeBox key={i} x={55} y={75 + i*95} label={m} w={270} h={60} color={palette.orange} />)}
    </Card>
    <Card x={470} y={175} w={420} h={400} title="Cara pemisahan" color={palette.teal}>
      {methods.slice(0,3).map((m,i)=><NodeBox key={i} x={70+i*110} y={130 + (i%2)*100} label={m} w={120} h={58} color={palette.teal} />)}
    </Card>
  </Stage>;
};

export const BioCellStructureTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const orgs = (spec.organelles as string[]) || [];
  const types = (spec.cell_types as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={45} y={170} w={840} h={405} title="Struktur sel" color={palette.green}>
      <SvgLayer>
        <ellipse cx="280" cy="320" rx="165" ry="105" fill="rgba(96,165,250,0.18)" stroke="#60a5fa" strokeWidth="3" />
        <circle cx="260" cy="305" r="38" fill="rgba(167,139,250,0.30)" stroke="#a78bfa" strokeWidth="3" />
        <ellipse cx="355" cy="280" rx="32" ry="22" fill="rgba(52,211,153,0.35)" />
        <ellipse cx="195" cy="355" rx="26" ry="16" fill="rgba(251,191,36,0.35)" />
      </SvgLayer>
      {orgs.slice(0,5).map((o,i)=><Pill key={i} x={[60,60,390,390,245][i]} y={[240,320,240,320,420][i]} text={o} color={[palette.blue,palette.purple,palette.green,palette.yellow,palette.teal][i]} />)}
      <LegendList title="Tipe sel" items={types} x={620} y={210} color={palette.orange} />
    </Card>
  </Stage>;
};

export const BioMembraneTransportTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const mechs = (spec.mechanisms as string[]) || [];
  const parts = (spec.particles as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={50} y={170} w={540} h={410} title="Transpor melintasi membran" color={palette.blue}>
      <div style={{position:'absolute', left:240, top:70, width:34, height:250, background:'repeating-linear-gradient(180deg, rgba(96,165,250,0.9) 0 10px, rgba(30,41,59,0.95) 10px 18px)', borderRadius:24}} />
      {Array.from({length:5}).map((_,i)=><Dot key={i} x={140 + (i%2)*45} y={120+i*40} r={10} color={palette.blue} label={i===0?parts[0]:undefined} />)}
      {Array.from({length:3}).map((_,i)=><Dot key={i} x={365 + (i%2)*40} y={170+i*55} r={10} color={palette.green} label={i===0?parts[1]:undefined} />)}
      <SvgLayer>{arrowMarker}<line x1="200" y1="220" x2="240" y2="220" {...lineStyle} markerEnd="url(#arrow)"/><line x1="275" y1="270" x2="335" y2="270" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
    </Card>
    <LegendList title="Mekanisme" items={mechs} x={655} y={230} color={palette.teal} />
  </Stage>;
};

export const BioCellDivisionTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const mit = (spec.mitosis as string[]) || [];
  const mei = (spec.meiosis as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={50} y={175} w={405} h={390} title="Mitosis" color={palette.blue}>
      {mit.slice(0,4).map((m,i)=><NodeBox key={i} x={55 + (i%2)*180} y={80 + Math.floor(i/2)*120} label={m} w={130} h={70} color={palette.blue} />)}
    </Card>
    <Card x={485} y={175} w={405} h={390} title="Meiosis" color={palette.purple}>
      {mei.slice(0,2).map((m,i)=><NodeBox key={i} x={120} y={120 + i*120} label={m} w={170} h={80} color={palette.purple} />)}
      <Pill x={560} y={410} text="hasil: 4 sel haploid" color={palette.yellow} />
    </Card>
  </Stage>;
};

export const BioEnzymeMetabolismTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const st = (spec.stages as string[]) || [];
  const fac = (spec.factors as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={50} y={175} w={540} h={390} title="Mekanisme enzim" color={palette.green}>
      {st.slice(0,3).map((s,i)=><NodeBox key={i} x={55 + i*160} y={150} label={s} w={130} h={70} color={[palette.yellow,palette.green,palette.blue][i]} />)}
      <SvgLayer>{arrowMarker}<line x1="250" y1="350" x2="265" y2="350" {...lineStyle} markerEnd="url(#arrow)"/><line x1="410" y1="350" x2="425" y2="350" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
    </Card>
    <LegendList title="Faktor pengaruh" items={fac} x={650} y={220} color={palette.orange} />
  </Stage>;
};

export const BioEnergyProcessTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const io = (spec.inputs_outputs as Record<string,string[]>) || {photosynthesis:[], respiration:[]};
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={40} y={170} w={400} h={400} title="Fotosintesis" color={palette.green}><LegendList title="Input-output" items={io.photosynthesis || []} x={70} y={230} color={palette.green} /></Card>
    <Card x={480} y={170} w={400} h={400} title="Respirasi" color={palette.orange}><LegendList title="Input-output" items={io.respiration || []} x={510} y={230} color={palette.orange} /></Card>
  </Stage>;
};

export const BioGeneticExpressionTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const stages = (spec.stages as string[]) || [];
  const keywords = (spec.keywords as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={175} w={840} h={395} title="Ekspresi gen" color={palette.purple}>
      {stages.slice(0,4).map((s,i)=><NodeBox key={i} x={60+i*185} y={155} label={s} w={140} h={70} color={[palette.blue,palette.green,palette.orange,palette.purple][i]} />)}
      <SvgLayer>{arrowMarker}<line x1="250" y1="350" x2="300" y2="350" {...lineStyle} markerEnd="url(#arrow)"/><line x1="435" y1="350" x2="485" y2="350" {...lineStyle} markerEnd="url(#arrow)"/><line x1="620" y1="350" x2="670" y2="350" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
      <LegendList title="Kata kunci" items={keywords} x={610} y={70} color={palette.yellow} />
    </Card>
  </Stage>;
};

export const BioGrowthTimelineTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const tl = (spec.timeline as string[]) || [];
  const factors = (spec.factors as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={180} w={840} h={390} title="Timeline pertumbuhan" color={palette.teal}>
      <SvgLayer>{arrowMarker}<line x1="120" y1="350" x2="760" y2="350" stroke="#94a3b8" strokeWidth="5" markerEnd="url(#arrow)"/></SvgLayer>
      {tl.slice(0,4).map((t,i)=><NodeBox key={i} x={90+i*180} y={180 - i*10} label={t} w={120} h={70} color={palette.teal} />)}
      <LegendList title="Faktor" items={factors} x={615} y={80} color={palette.yellow} />
    </Card>
  </Stage>;
};

export const ChemMaterialEnvironmentTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const materials = (spec.materials as string[]) || [];
  const apps = (spec.applications as string[]) || [];
  const impacts = (spec.impacts as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={45} y={175} w={255} h={390} title="Material" color={palette.blue}>{materials.map((m,i)=><Pill key={i} x={70} y={90+i*70} text={m} color={palette.blue} />)}</Card>
    <Card x={325} y={175} w={255} h={390} title="Aplikasi" color={palette.green}>{apps.map((m,i)=><Pill key={i} x={350} y={90+i*70} text={m} color={palette.green} />)}</Card>
    <Card x={605} y={175} w={255} h={390} title="Dampak" color={palette.red}>{impacts.map((m,i)=><Pill key={i} x={630} y={90+i*70} text={m} color={palette.red} />)}</Card>
  </Stage>;
};

export const SdWeatherWaterCycleTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const cycle = (spec.cycle as string[]) || [];
  const icons = (spec.weather_icons as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={170} w={840} h={405} title="Daur air" color={palette.blue}>
      {cycle.slice(0,4).map((c,i)=><NodeBox key={i} x={[110,360,620,360][i]} y={[310,120,310,450][i]-100} label={c} w={150} h={56} color={palette.blue} />)}
      <SvgLayer>{arrowMarker}<path d="M 260 360 Q 340 245 420 205" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 530 205 Q 620 250 690 345" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 630 410 Q 530 470 430 410" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 300 410 Q 210 390 180 355" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
      <LegendList title="Cuaca" items={icons} x={625} y={70} color={palette.yellow} />
    </Card>
  </Stage>;
};

export const ChemLabSeparationTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const methods = (spec.methods as string[]) || [];
  const mixtures = (spec.mixtures as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={45} y={175} w={520} h={390} title="Metode laboratorium" color={palette.orange}>
      {methods.slice(0,3).map((m,i)=><NodeBox key={i} x={60+i*150} y={110} label={m} w={125} h={72} color={palette.orange} />)}
      {mixtures.slice(0,3).map((m,i)=><Pill key={i} x={90+i*130} y={260} text={m} color={palette.blue} />)}
    </Card>
    <Card x={600} y={175} w={290} h={390} title="Prinsip" color={palette.teal}><div style={{fontSize:15, color:palette.subtext, lineHeight:1.55}}>Pemisahan didasarkan pada perbedaan sifat fisik seperti ukuran partikel, titik didih, dan afinitas terhadap fase diam/gerak.</div></Card>
  </Stage>;
};

export const BioImmuneResponseTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const actors = (spec.actors as string[]) || [];
  const stages = (spec.stages as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={175} w={540} h={390} title="Interaksi respons imun" color={palette.red}>
      {actors.slice(0,5).map((a,i)=><NodeBox key={i} x={[70,200,330,140,270][i]} y={[85,170,85,280,280][i]} label={a} w={120} h={52} color={[palette.red,palette.blue,palette.green,palette.purple,palette.yellow][i]} />)}
      <SvgLayer>{arrowMarker}<line x1="245" y1="286" x2="300" y2="244" {...lineStyle} markerEnd="url(#arrow)"/><line x1="390" y1="180" x2="300" y2="206" {...lineStyle} markerEnd="url(#arrow)"/><line x1="270" y1="338" x2="330" y2="338" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
    </Card>
    <LegendList title="Tahap" items={stages} x={655} y={230} color={palette.teal} />
  </Stage>;
};

export const BioHomeostasisFeedbackTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const loop = (spec.loop as string[]) || [];
  const ex = (spec.examples as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={170} w={540} h={400} title="Loop umpan balik" color={palette.purple}>
      {loop.slice(0,5).map((l,i)=><NodeBox key={i} x={[215,370,300,110,120][i]} y={[55,165,315,315,165][i]} label={l} w={120} h={54} color={palette.purple} />)}
      <SvgLayer>{arrowMarker}<path d="M 390 210 Q 390 300 360 340" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 240 340 Q 170 330 170 260" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 170 165 Q 195 105 250 82" {...lineStyle} markerEnd="url(#arrow)"/><path d="M 335 82 Q 390 90 405 160" {...lineStyle} markerEnd="url(#arrow)"/></SvgLayer>
    </Card>
    <LegendList title="Contoh" items={ex} x={660} y={235} color={palette.yellow} />
  </Stage>;
};

export const BioHealthDisorderTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const cases = (spec.cases as string[]) || [];
  const cols = (spec.columns as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={175} w={840} h={390} title="Kartu gangguan kesehatan" color={palette.red}>
      {cases.slice(0,3).map((c,i)=><Card key={i} x={50+i*250} y={80} w={210} h={240} color={[palette.red,palette.orange,palette.purple][i]} title={c}>
        {cols.slice(0,3).map((col,j)=><div key={j} style={{fontSize:14, color:j===0? [palette.red,palette.orange,palette.purple][i]: palette.subtext, marginTop: j===0? 12: 10}}>{j===0? 'Sistem': j===1? 'Gejala': 'Pencegahan'}: <span style={{color:palette.subtext}}>{col}</span></div>)}
      </Card>)}
    </Card>
  </Stage>;
};

export const SdStructureFunctionTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const plant = (spec.plant_parts as string[]) || [];
  const animal = (spec.animal_parts as string[]) || [];
  return <Stage spec={spec}><StepRail steps={spec.steps} />
    <Card x={48} y={175} w={390} h={390} title="Tumbuhan" color={palette.green}>{plant.slice(0,4).map((p,i)=><Pill key={i} x={75 + (i%2)*150} y={90 + Math.floor(i/2)*90} text={p} color={palette.green} />)}</Card>
    <Card x={490} y={175} w={390} h={390} title="Hewan" color={palette.orange}>{animal.slice(0,4).map((p,i)=><Pill key={i} x={515 + (i%2)*150} y={90 + Math.floor(i/2)*90} text={p} color={palette.orange} />)}</Card>
  </Stage>;
};

export const templateComponents = {
  'remotion.bio_ecosystem_network.v1': BioEcosystemNetworkTemplate,
  'remotion.bio_organ_system_flow.v1': BioOrganSystemFlowTemplate,
  'remotion.earth_space_system.v1': EarthSpaceSystemTemplate,
  'remotion.chem_bonding_molecule.v1': ChemBondingMoleculeTemplate,
  'remotion.bio_flow_system.v1': BioFlowSystemTemplate,
  'remotion.bio_taxonomy_biodiversity.v1': BioTaxonomyBiodiversityTemplate,
  'remotion.bio_biotech_process.v1': BioBiotechProcessTemplate,
  'remotion.chem_atomic_periodic.v1': ChemAtomicPeriodicTemplate,
  'remotion.chem_acid_base_titration.v1': ChemAcidBaseTitrationTemplate,
  'remotion.sd_ecosystem_food_chain.v1': SdEcosystemFoodChainTemplate,
  'remotion.sd_energy_forms.v1': SdEnergyFormsTemplate,
  'remotion.bio_structure_labeling.v1': BioStructureLabelingTemplate,
  'remotion.bio_virus_lifecycle.v1': BioVirusLifecycleTemplate,
  'remotion.bio_evolution_selection.v1': BioEvolutionSelectionTemplate,
  'remotion.chem_particle_reaction_rate.v1': ChemParticleReactionRateTemplate,
  'remotion.chem_redox_electrochemistry.v1': ChemRedoxElectrochemistryTemplate,
  'remotion.chem_organic_structure.v1': ChemOrganicStructureTemplate,
  'remotion.sd_body_senses_health.v1': SdBodySensesHealthTemplate,
  'remotion.sd_life_cycle_classification.v1': SdLifeCycleClassificationTemplate,
  'remotion.chem_acid_base_safety.v1': ChemAcidBaseSafetyTemplate,
  'remotion.chem_lab_safety.v1': ChemLabSafetyTemplate,
  'remotion.chem_particle_matter.v1': ChemParticleMatterTemplate,
  'remotion.sd_inquiry_observation.v1': SdInquiryObservationTemplate,
  'remotion.sd_matter_states.v1': SdMatterStatesTemplate,
  'remotion.sd_solar_system_day_night.v1': SdSolarSystemDayNightTemplate,
  'remotion.sd_earth_resources_environment.v1': SdEarthResourcesEnvironmentTemplate,
  'remotion.sd_mixture_separation.v1': SdMixtureSeparationTemplate,
  'remotion.bio_cell_structure.v1': BioCellStructureTemplate,
  'remotion.bio_membrane_transport.v1': BioMembraneTransportTemplate,
  'remotion.bio_cell_division.v1': BioCellDivisionTemplate,
  'remotion.bio_enzyme_metabolism.v1': BioEnzymeMetabolismTemplate,
  'remotion.bio_energy_process.v1': BioEnergyProcessTemplate,
  'remotion.bio_genetic_expression.v1': BioGeneticExpressionTemplate,
  'remotion.bio_growth_timeline.v1': BioGrowthTimelineTemplate,
  'remotion.chem_material_environment.v1': ChemMaterialEnvironmentTemplate,
  'remotion.sd_weather_water_cycle.v1': SdWeatherWaterCycleTemplate,
  'remotion.chem_lab_separation.v1': ChemLabSeparationTemplate,
  'remotion.bio_immune_response.v1': BioImmuneResponseTemplate,
  'remotion.bio_homeostasis_feedback.v1': BioHomeostasisFeedbackTemplate,
  'remotion.bio_health_disorder.v1': BioHealthDisorderTemplate,
  'remotion.sd_structure_function.v1': SdStructureFunctionTemplate,
} as const;

export type TemplateId = keyof typeof templateComponents;
export const RenderTemplate: React.FC<{spec: BaseTemplateSpec}> = ({spec}) => {
  const Comp = templateComponents[spec.template_id as TemplateId];
  if (!Comp) {
    return <Stage spec={spec}><Card x={60} y={180} w={1160} h={360} title="Template belum terdaftar" color={palette.red}><div style={{fontSize:22}}>{spec.template_id}</div></Card></Stage>;
  }
  return <Comp spec={spec} />;
};