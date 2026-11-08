#!/usr/bin/env python3
import hashlib, json, pathlib, shutil
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'output'
target=root/'openwrt/bin/targets/mediatek/filogic'
images=list(target.glob('*netcore_n60-pro*squashfs-sysupgrade.bin'))
assert len(images)==1, f'Expected exactly one N60 Pro image: {images}'
assert 0<images[0].stat().st_size<0x7280000, 'Unexpected image size'
for path in target.iterdir():
    if path.is_file() and (path in images or path.suffix in ['.manifest','.buildinfo','.json']): shutil.copy2(path,out/path.name)
names=[]
for p in sorted(out.iterdir()):
    if p.is_file() and p.name!='SHA256SUMS':
        with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest() if hasattr(hashlib,'file_digest') else hashlib.sha256(f.read()).hexdigest()
        names.append(f'{digest}  {p.name}')
(out/'SHA256SUMS').write_text('\n'.join(names)+'\n')
print('Collected firmware:',images[0].name)
