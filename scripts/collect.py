#!/usr/bin/env python3
import hashlib, json, pathlib, shutil
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'output'
target=root/'openwrt/bin/targets/mediatek/filogic'
images=list(target.glob('*netcore_n60-pro*squashfs-sysupgrade.*'))
assert len(images)==1, f'Expected exactly one N60 Pro image: {images}'
assert 0<images[0].stat().st_size<0x7280000, 'Unexpected image size'
lock=json.loads((root/'source-lock.json').read_text(encoding='utf-8-sig'))
if lock.get('series')=='25.12':
    assert images[0].suffix=='.itb', '25.12 must produce the upstream FIT image'
    with images[0].open('rb') as f:
        assert f.read(4)==bytes.fromhex('d00dfeed'), 'Invalid FIT header'
manifest=next(target.glob('*netcore_n60-pro*.manifest'),None)
assert manifest, 'N60 Pro package manifest missing'
packages={line.split(' - ')[0] for line in manifest.read_text().splitlines()}
required={line.split('=')[0].removeprefix('CONFIG_PACKAGE_') for line in (root/'config/extra.config').read_text().splitlines() if line.startswith('CONFIG_PACKAGE_') and line.endswith('=y')}
assert not required-packages, f'Mandatory packages absent from image: {sorted(required-packages)}'
assert (root/'openwrt/files/etc/openclash/core/clash_meta').stat().st_size>1000000, 'Clash core missing'
for path in target.iterdir():
    if path.is_file() and (path in images or path.suffix in ['.manifest','.buildinfo','.json']): shutil.copy2(path,out/path.name)
names=[]
for p in sorted(out.iterdir()):
    if p.is_file() and p.name!='SHA256SUMS':
        with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest() if hasattr(hashlib,'file_digest') else hashlib.sha256(f.read()).hexdigest()
        names.append(f'{digest}  {p.name}')
(out/'SHA256SUMS').write_text('\n'.join(names)+'\n')
print('Collected firmware:',images[0].name)
