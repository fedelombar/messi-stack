import re,sys
from pathlib import Path
st=Path(sys.argv[1]); mm=st/'skills/messi-mode'
skills={p.name for p in (st/'skills').iterdir()}
princ={p.stem for p in (mm/'principles').glob('*.md')}
plays={p.stem for p in (mm/'playbooks').glob('*.md')}
ok=skills|princ|{'principle-'+p for p in princ}|plays|{'blocked','bug','changed','clean','updated'}
bad=[]
for f in [*(st/'skills').rglob('*.md'), *(st/'agents').rglob('*.md')]:
    if f.name in('UPSTREAM.md',): continue
    t=f.read_text()
    for n in set(re.findall(r'\*\*([a-z][a-z-]+)\*\*',t)):
        if n not in ok: bad.append((str(f.relative_to(st)),'bold',n))
    for n in set(re.findall(r'(?<![\w/.~])/([a-z][a-z-]+)`',t)):
        if n not in skills|{'loop','simplify'}: bad.append((str(f.relative_to(st)),'slash',n))
    for n in set(re.findall(r'playbooks/([a-z-]+)\.md',t)):
        if n not in plays: bad.append((str(f.relative_to(st)),'playbook',n))
    for n in set(re.findall(r'~/\.claude/skills/([a-z-]+)/([\w./-]+)',t)):
        if n!=('messi-mode','SOURCE') and not (st/'skills'/n[0]/n[1].rstrip('.')).exists(): bad.append((str(f.relative_to(st)),'path','/'.join(n)))
    if f.name=='SKILL.md' and not re.match(r'---\nname: .+\ndescription: .+\n',t): bad.append((str(f.relative_to(st)),'frontmatter',''))
# playbook titles listed in messi-mode
titles=re.search(r'\n(Investigation,.*)\n',(mm/'SKILL.md').read_text()).group(1).rstrip('.').split(', ')
for t in titles:
    if t.lower().replace(' ','-') not in plays: bad.append(('SKILL.md','title',t))
if len(titles)!=len(plays): bad.append(('SKILL.md','title-count',f'{len(titles)} vs {len(plays)}'))
print('\n'.join(map(str,bad)) or 'all references resolve'); print(len(skills),'skills',len(princ),'principles',len(plays),'playbooks')
