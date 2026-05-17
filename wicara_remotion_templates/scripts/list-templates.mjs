import fs from 'fs';
import path from 'path';
const specsDir = path.join(process.cwd(), 'specs');
const files = fs.readdirSync(specsDir).filter((f) => f.endsWith('.json'));
for (const file of files) {
  const data = JSON.parse(fs.readFileSync(path.join(specsDir, file), 'utf-8'));
  console.log(`${data.row_index}	${data.template_id}	${data.title}`);
}