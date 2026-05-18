import argparse, json, shutil, subprocess, sys
from pprint import pformat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--template',required=True)
parser.add_argument('--spec',required=True)
parser.add_argument('--quality',default='-ql')
args=parser.parse_args()
tmp=ROOT/'tmp_render'; tmp.mkdir(exist_ok=True)
shutil.rmtree(tmp/'__pycache__', ignore_errors=True)
for stale in ['generated_template.py', 'render_scene.py']:
    (tmp/stale).unlink(missing_ok=True)
for name in ['core_templates.py','base_scene.py']:
    shutil.copyfile(ROOT/'templates'/'manim'/name, tmp/name)
shutil.copyfile(Path(args.template), tmp/'generated_template.py')
spec=json.loads(Path(args.spec).read_text(encoding='utf-8'))
spec_literal = pformat(spec, indent=4, width=120, sort_dicts=False)
(tmp/'render_scene.py').write_text(
    'from generated_template import GeneratedTemplate\n\nclass RenderScene(GeneratedTemplate):\n    SPEC = '
    + spec_literal
    + '\n',
    encoding='utf-8',
)
quality = args.quality.strip()
if not quality:
    quality = '-ql'
if not quality.startswith('-'):
    quality = f'-q{quality}'
cmd=[sys.executable, '-m', 'manim', quality, str(tmp/'render_scene.py'), 'RenderScene']
print('Running:', ' '.join(cmd))
subprocess.run(cmd,check=True)
