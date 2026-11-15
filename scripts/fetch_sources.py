"""Download only pinned, licensed narrative data; verify exact file hashes."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'data/source_manifest.json').read_text())
for f in m['files']:
    u='https://raw.githubusercontent.com/inkle/ink-library/'+m['commit']+'/'+quote(f['upstream_path'])
    body=urlopen(Request(u,headers={'User-Agent':'NarrativeNoveltyResearch/1.0'}),timeout=60).read()
    if hashlib.sha256(body).hexdigest()!=f['sha256']:raise ValueError('Source checksum mismatch: '+f['id'])
    (ROOT/f['local_path']).write_bytes(body)
    print(f['id'],len(body),'verified')
