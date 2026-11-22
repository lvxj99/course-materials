"""Create a portable UTF-8-named ZIP and verify every local handout link."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

root = Path(__file__).resolve().parent.parent
archive = root.parent / '强化学习拓展_讲义与配图.zip'
document = '强化学习_从序贯决策到大模型后训练.md'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
    for file in sorted(root.rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts:
            bundle.write(file, Path(root.name) / file.relative_to(root))
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    names = set(bundle.namelist())
    md_name = root.name + '/' + document
    content = bundle.read(md_name).decode('utf-8')
    for ref in re.findall(r'\]\(([^)]+)\)', content):
        if not ref.startswith(('http://', 'https://')):
            assert root.name + '/' + ref in names, ref
    svgs = [name for name in names if name.endswith('.svg')]
    assert len(svgs) == 15
    assert bundle.read(md_name) == (root / document).read_bytes()
print(json.dumps({'archive': str(archive), 'files': len(names), 'svg': len(svgs),
                  'bytes': archive.stat().st_size, 'local_links': 'all present',
                  'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()},
                 ensure_ascii=False, indent=2))
