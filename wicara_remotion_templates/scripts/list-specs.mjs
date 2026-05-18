import fs from 'fs';
import path from 'path';
const dir = path.join(process.cwd(), 'specs');
for (const f of fs.readdirSync(dir).filter((x)=>x.endsWith('.json')).sort()) {
  const s = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  console.log(`${String(s.row_index).padStart(3,'0')}	${s.template_id}	${s.component}	${s.title}`);
}