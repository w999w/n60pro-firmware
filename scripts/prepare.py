#!/usr/bin/env python3
"""Prepare a pinned N60 Pro 2 GiB build; never reads router backups."""
import gzip, hashlib, json, pathlib, re, shutil, subprocess, tarfile, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / 'openwrt'
LOCK = json.loads((ROOT/'source-lock.json').read_text(encoding='utf-8-sig'))
OUT = ROOT/'output'
OUT.mkdir(exist_ok=True)

def run(*args, cwd=ROOT):
    subprocess.run(args, cwd=cwd, check=True)

def checkout(spec, path):
    path.mkdir(parents=True, exist_ok=True)
    run('git','init',str(path))
    run('git','-C',str(path),'remote','add','origin',spec['url'])
    run('git','-C',str(path),'fetch','--depth=1','origin',spec['commit'])
    run('git','-C',str(path),'checkout','--detach','FETCH_HEAD')

checkout(LOCK['firmware'], SRC)
feeds=json.loads((ROOT/'feeds-lock.json').read_text(encoding='utf-8-sig'))
feeds['istore']=LOCK['istore']
(SRC/'feeds.conf.default').write_text(''.join(f"src-git {k} {v['url']}^{v['commit']}\n" for k,v in feeds.items()))
run('./scripts/feeds','update','-a',cwd=SRC)
run('./scripts/feeds','install','-a',cwd=SRC)

for key, dest in [('openclash','openclash-src'),('adguard_luci','luci-app-adguardhome'),('argon','luci-theme-argon')]:
    checkout(LOCK[key], SRC/'package/custom'/dest)
# A same-named feed symlink must not shadow our pinned theme.
for p in (SRC/'package/feeds').rglob('luci-theme-argon'):
    if p.is_symlink(): p.unlink()

# Start with upstream's MTK radio settings, discarding its multi-device targets.
base=(SRC/'defconfig/mt7975-ipailna-high-power.config').read_text()
base='\n'.join(l for l in base.splitlines() if not l.startswith(('CONFIG_TARGET_', 'CONFIG_HAS_SUBTARGETS=')))
(SRC/'.config').write_text(base+'\n'+(ROOT/'config/extra.config').read_text())

dts=SRC/'target/linux/mediatek/dts/mt7986a-netcore-n60-pro.dts'
text=dts.read_text()
old='reg = <0 0x40000000 0 0x20000000>;'
assert text.count(old)==1, 'Unexpected memory declaration; review instead of guessing'
dts.write_text(text.replace(old,'reg = <0 0x40000000 0 0x80000000>;'))

mk=SRC/'target/linux/mediatek/image/filogic.mk'
text=mk.read_text()
match=re.search(r'define Device/netcore_n60-pro\n.*?\nendef',text,re.S)
assert match, 'N60 profile missing'
block=match.group()
assert 'sysupgrade.bin' in block and 'kmod-mt7915e' in block
patched=block.replace('kmod-mt7915e kmod-mt7986-firmware mt7986-wo-firmware','kmod-mt_wifi kmod-warp')
mk.write_text(text[:match.start()]+patched+text[match.end():])

# Ship the two verified arm64 cores, with no subscriptions or personal settings.
for key in ['smart_core','adguard_core']:
    spec=LOCK[key]
    archive=ROOT/(key+'.download')
    run('curl','--fail','--location','--retry','4','--max-time','180','--output',str(archive),spec['url'])
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==spec['sha256'], f'{key} checksum mismatch'
    if key=='smart_core':
        dest=SRC/'files/etc/openclash/core/clash_meta'
        dest.parent.mkdir(parents=True,exist_ok=True)
        with gzip.open(archive,'rb') as src, dest.open('wb') as dst: shutil.copyfileobj(src,dst)
    else:
        dest=SRC/'files/usr/bin/AdGuardHome/AdGuardHome'
        dest.parent.mkdir(parents=True,exist_ok=True)
        with tarfile.open(archive,'r:gz') as tar:
            members=[m for m in tar.getmembers() if m.isfile() and m.name.removeprefix('./')=='AdGuardHome/AdGuardHome']
            assert len(members)==1, 'Unexpected AdGuard archive layout'
            with tar.extractfile(members[0]) as src, dest.open('wb') as dst: shutil.copyfileobj(src,dst)
    dest.chmod(0o755)
    archive.unlink()

defaults=SRC/'files/etc/uci-defaults/99-n60-generic'
defaults.parent.mkdir(parents=True,exist_ok=True)
defaults.write_text('''#!/bin/sh
uci set system.@system[0].hostname=N60Pro
uci set system.@system[0].timezone=CST-8
uci set system.@system[0].zonename=Asia/Shanghai
uci commit system
uci set network.lan.proto=static
uci set network.lan.ipaddr=192.168.100.1
uci set network.lan.netmask=255.255.255.0
uci commit network
uci -q set openclash.config.enable=0
uci -q set openclash.config.core_type=Smart
uci -q commit openclash
uci -q set AdGuardHome.AdGuardHome.enabled=0
uci -q set AdGuardHome.AdGuardHome.redirect=none
uci -q commit AdGuardHome
for svc in openclash AdGuardHome cloudflared ipsec ipsec-vpnd ksmbd watchcat timewol ttyd; do
    [ ! -x /etc/init.d/$svc ] || /etc/init.d/$svc disable
done
exit 0
''')
defaults.chmod(0o755)
run('make','defconfig',cwd=SRC)
config=(SRC/'.config').read_text()
required=['TARGET_mediatek_filogic_DEVICE_netcore_n60-pro','PACKAGE_luci-app-store','PACKAGE_luci-app-openclash','PACKAGE_luci-app-adguardhome','PACKAGE_kmod-mt_wifi','PACKAGE_luci-app-mtwifi-cfg','PACKAGE_luci-app-timewol','PACKAGE_luci-app-ksmbd','PACKAGE_luci-theme-argon']
for sym in required:
    assert f'CONFIG_{sym}=y' in config, f'Mandatory symbol lost: {sym}'
shutil.copy2(SRC/'.config',OUT/'build.config')
with (OUT/'diffconfig').open('w') as f: subprocess.run(['./scripts/diffconfig.sh'],cwd=SRC,stdout=f,check=True)
for name in ['source-lock.json','feeds-lock.json']: shutil.copy2(ROOT/name,OUT/name)
with (OUT/'device-changes.patch').open('w') as f: subprocess.run(['git','diff','--','target'],cwd=SRC,stdout=f,check=True)
print('Pinned source, packages, 2 GiB RAM and unchanged partition layout prepared.')
