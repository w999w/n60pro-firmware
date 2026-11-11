#!/usr/bin/env python3
"""Prepare a pinned N60 Pro 2 GiB build; never reads router backups."""
import gzip, hashlib, json, os, pathlib, re, shutil, subprocess, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / 'openwrt'
LOCK = json.loads((ROOT/'source-lock.json').read_text(encoding='utf-8-sig'))
MODERN = LOCK.get('series') == '25.12'
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

for key, dest in [('openclash','openclash-src'),('argon','luci-theme-argon')] + [(k,k+'-src') for k in LOCK.get('extra_packages',[])]:
    checkout(LOCK[key], SRC/'package/custom'/dest)
# Feed copies of the legacy Argon packages must not shadow the pinned v3 theme.
# The v3 theme itself owns the argon-config translation package; leaving the
# legacy config app installed makes opkg resolve that translation to a missing
# luci-app-argon-config dependency during image assembly.
for name in ('luci-theme-argon', 'luci-app-argon-config', 'luci-app-mosdns', 'mosdns', 'geo2txt'):
    for p in (SRC/'package/feeds').rglob(name):
        if p.is_symlink(): p.unlink()

# Start with upstream's MTK radio settings, discarding its multi-device targets.
base='' if MODERN else (SRC/'defconfig/mt7975-ipailna-high-power.config').read_text()
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
assert ('sysupgrade.itb' if MODERN else 'sysupgrade.bin') in block and 'kmod-mt7915e' in block
patched=block.replace('kmod-mt7915e kmod-mt7986-firmware mt7986-wo-firmware','kmod-mt_wifi kmod-warp')
if not MODERN:
    mk.write_text(text[:match.start()]+patched+text[match.end():])

# Ship the two verified arm64 cores, with no subscriptions or personal settings.
def resolve_core_asset(key, spec):
    """解析内核下载地址。

    滚动发布（如 vernesong/mihomo 的 Prerelease-Alpha）会不断替换资产文件名，
    写死 URL 必然 404。这里允许用 repo/release/asset_pattern 在构建时解析当前文件；
    仍兼容原来的 url + sha256 固定写法。
    """
    if 'url' in spec:
        return spec['url'], spec.get('sha256')
    repo, tag, pattern = spec['repo'], spec['release'], spec['asset_pattern']
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'n60-build'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    rx = re.compile(pattern)
    names = []
    # 首选 API；拿不到（无 token 限流、权限不足等）就退回 release 页面解析
    try:
        url = f'https://api.github.com/repos/{repo}/releases/tags/{tag}'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            rel = json.load(resp)
        matches = [a for a in rel.get('assets', []) if rx.match(a['name'])]
        matches.sort(key=lambda a: a.get('created_at', ''), reverse=True)
        names = [a['name'] for a in matches]
        print(f'{key}: 通过 API 解析（{len(names)} 个匹配）', flush=True)
    except Exception as exc:
        print(f'{key}: API 解析失败（{exc}），改用 release 页面解析', flush=True)
        page = f'https://github.com/{repo}/releases/expanded_assets/{tag}'
        req = urllib.request.Request(page, headers={'User-Agent': 'n60-build'})
        with urllib.request.urlopen(req, timeout=60) as resp:
            html = resp.read().decode('utf-8', 'replace')
        found = re.findall(rf'/{re.escape(repo)}/releases/download/{re.escape(tag)}/([^"?#\\]+)', html)
        names = sorted({n for n in found if rx.match(n)})

    assert names, f'{key}: {repo}@{tag} 中没有匹配 {pattern} 的资产'
    chosen = names[0]
    dl = f'https://github.com/{repo}/releases/download/{tag}/{chosen}'
    print(f'{key}: 解析到 {chosen}', flush=True)
    return dl, spec.get('sha256')

for key in (['smart_core'] if MODERN else ['smart_core']):
    spec=LOCK[key]
    dl_url,dl_sha=resolve_core_asset(key,spec)
    archive=ROOT/(key+'.download')
    run('curl','--fail','--location','--retry','4','--max-time','180','--output',str(archive),dl_url)
    actual=hashlib.sha256(archive.read_bytes()).hexdigest()
    if dl_sha:
        assert actual==dl_sha, f'{key} checksum mismatch'
    else:
        print(f'{key}: SHA256={actual}（未固定，仅记录用于追溯）', flush=True)
    dest=SRC/'files/etc/openclash/core/clash_meta'
    dest.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(archive,'rb') as src, dest.open('wb') as dst: shutil.copyfileobj(src,dst)
    dest.chmod(0o755)
    archive.unlink()

defaults=SRC/'files/etc/uci-defaults/99-n60-generic'
defaults.parent.mkdir(parents=True,exist_ok=True)
defaults.write_text('''#!/bin/sh
uci set system.@system[0].hostname=N60Pro
uci set system.@system[0].timezone=CST-8
uci set system.@system[0].zonename=Asia/Shanghai
uci commit system
uci -q set dropbear.@dropbear[0].DirectInterface=lan
uci -q delete dropbear.@dropbear[0].Interface
uci -q commit dropbear
uci set network.lan.proto=static
uci set network.lan.ipaddr=192.168.6.1
uci set network.lan.netmask=255.255.255.0
uci commit network
uci -q set openclash.config.enable=0
uci -q set openclash.config.core_type=Smart
uci -q commit openclash
uci -q set bandix.traffic.enabled=1
uci -q set bandix.traffic.traffic_enable_storage=0
uci -q set bandix.general.data_dir=/tmp/bandix
uci -q set bandix.general.tc_backend=netlink
uci -q commit bandix
# Spin the external disk down after 10 idle minutes (handled by hd-idle).
uci -q set hd-idle.@hd-idle[0].disk=sda
uci -q set hd-idle.@hd-idle[0].enabled=1
uci -q set hd-idle.@hd-idle[0].idle_time_interval=10
uci -q set hd-idle.@hd-idle[0].idle_time_unit=minutes
uci -q commit hd-idle
# HTTPS on by default: generate a self-signed cert first, then decide whether
# to force the redirect. uhttpd appends -q whenever listen_https is non-empty,
# without checking that the cert is usable; redirecting to a dead 443 would
# lock the web UI out, so only enable it once both files really exist.
if [ ! -s /etc/uhttpd.crt ] || [ ! -s /etc/uhttpd.key ]; then
    px5g selfsigned -der -days 397 -newkey ec -pkeyopt ec_paramgen_curve:P-256 \\
        -keyout /etc/uhttpd.key -out /etc/uhttpd.crt \\
        -subj /C=ZZ/ST=Somewhere/L=Unknown/CN=N60Pro \\
        -addext extendedKeyUsage=serverAuth \\
        -addext subjectAltName=DNS:N60Pro \\
        -addext subjectAltName=IP:192.168.6.1 >/dev/null 2>&1
    chmod 600 /etc/uhttpd.key 2>/dev/null
    chmod 644 /etc/uhttpd.crt 2>/dev/null
fi
uci -q delete uhttpd.main.listen_https
if [ -s /etc/uhttpd.crt ] && [ -s /etc/uhttpd.key ]; then
    uci -q add_list uhttpd.main.listen_https=0.0.0.0:443
    uci -q add_list uhttpd.main.listen_https='[::]:443'
    uci -q set uhttpd.main.redirect_https=1
else
    # No usable cert: keep plain HTTP reachable instead of redirecting nowhere.
    uci -q set uhttpd.main.redirect_https=0
fi
uci -q commit uhttpd
for svc in openclash mosdns ksmbd watchcat taskplan; do
    [ ! -x /etc/init.d/$svc ] || /etc/init.d/$svc disable
done
for svc in bandix collectd hd-idle; do
    [ ! -x /etc/init.d/$svc ] || /etc/init.d/$svc enable
done
# Pick data dirs by disk presence, then stage OpenClash onto tmpfs.
[ -x /usr/sbin/bandix-datadir.sh ] && /usr/sbin/bandix-datadir.sh
[ -x /usr/sbin/openclash-datadir.sh ] && /usr/sbin/openclash-datadir.sh
exit 0
''')
defaults.chmod(0o755)

# 数据目录选择脚本：镜像不假定一定有外接硬盘，两处都做在线检测。
datadir_helpers=SRC/'files/usr/sbin'
datadir_helpers.mkdir(parents=True,exist_ok=True)
(datadir_helpers/'bandix-datadir.sh').write_text('''#!/bin/sh
# Prefer the disk when it is mounted so history persists; fall back to tmpfs.
DISK_DIR="/mnt/sda1/bandix"
TMP_DIR="/tmp/bandix"
want="$TMP_DIR"
if mountpoint -q /mnt/sda1 2>/dev/null; then
	mkdir -p "$DISK_DIR" 2>/dev/null && want="$DISK_DIR"
fi
mkdir -p "$want" 2>/dev/null
current=$(uci -q get bandix.general.data_dir)
if [ "$current" != "$want" ]; then
	uci -q set bandix.general.data_dir="$want"
	if [ "$want" = "$DISK_DIR" ]; then
		uci -q set bandix.traffic.traffic_enable_storage=1
	else
		uci -q set bandix.traffic.traffic_enable_storage=0
	fi
	uci -q commit bandix
fi
exit 0
''')
(datadir_helpers/'openclash-datadir.sh').write_text('''#!/bin/sh
# Stage OpenClash core/providers/rules on tmpfs and point the symlinks at it.
# Source: the disk copy when mounted, otherwise the flash seed copy.
TMP_ROOT="/tmp/openclash"
DISK_ROOT="/mnt/sda1/openclash"
SEED_ROOT="/etc/openclash/_seed"
for d in core providers rules data; do mkdir -p "$TMP_ROOT/$d" 2>/dev/null; done
copy_missing() {
	[ -d "$1" ] || return 0
	for f in "$1"/*; do
		[ -e "$f" ] || continue
		b=$(basename "$f")
		[ -e "$2/$b" ] || cp -a "$f" "$2/" 2>/dev/null
	done
}
if mountpoint -q /mnt/sda1 2>/dev/null && [ -d "$DISK_ROOT" ]; then
	copy_missing "$DISK_ROOT/core" "$TMP_ROOT/core"
	copy_missing "$DISK_ROOT/providers" "$TMP_ROOT/providers"
	copy_missing "$DISK_ROOT/rules" "$TMP_ROOT/rules"
else
	copy_missing "$SEED_ROOT/core" "$TMP_ROOT/core"
	copy_missing "$SEED_ROOT/providers" "$TMP_ROOT/providers"
	copy_missing "$SEED_ROOT/rules" "$TMP_ROOT/rules"
fi
cd /etc/openclash 2>/dev/null || exit 0
for pair in "core:core" "proxy_provider:providers" "rule_provider:rules"; do
	link="${pair%%:*}"; target="${pair##*:}"
	if [ -h "$link" ] || [ -e "$link" ]; then rm -rf "$link" 2>/dev/null || continue; fi
	ln -sf "$TMP_ROOT/$target" "$link"
done
exit 0
''')
for f in datadir_helpers.iterdir(): f.chmod(0o755)

# 插拔硬盘时重新判定数据目录，只有真的变了才重启 bandix。
hotplug=SRC/'files/etc/hotplug.d/block/90-bandix-datadir'
hotplug.parent.mkdir(parents=True,exist_ok=True)
hotplug.write_text('''#!/bin/sh
[ -x /usr/sbin/bandix-datadir.sh ] || exit 0
case "$DEVNAME" in sda*) ;; *) exit 0 ;; esac
before=$(uci -q get bandix.general.data_dir)
/usr/sbin/bandix-datadir.sh
[ "$before" = "$(uci -q get bandix.general.data_dir)" ] && exit 0
[ -x /etc/init.d/bandix ] && /etc/init.d/bandix restart >/dev/null 2>&1
exit 0
''')
hotplug.chmod(0o755)
run('make','defconfig',cwd=SRC)
config=(SRC/'.config').read_text()

for name in ['.config','tmp/.packageinfo','tmp/.config-package.in']:
    path=SRC/name
    if path.exists(): shutil.copy2(path,OUT/('diagnostic-'+path.name.lstrip('.')))
meta=(SRC/'tmp/.packageinfo').read_text()
for name in ['luci-app-store','luci-lib-taskd','taskd','luci-lib-xterm']:
    match=re.search(r'^Package: '+re.escape(name)+r'\n.*?(?=\nPackage: |\Z)',meta,re.M|re.S)
    print('DEPENDENCY DIAGNOSTIC',name,match.group(0)[:3000] if match else 'NOT IN PACKAGE METADATA',flush=True)
print('ALL DROPPED REQUESTED PACKAGES:',[sym for sym in re.findall(r'^CONFIG_PACKAGE_(.+)=y$',(ROOT/'config/extra.config').read_text(),re.M) if f'CONFIG_PACKAGE_{sym}=y' not in config],flush=True)

required=['TARGET_mediatek_filogic_DEVICE_netcore_n60-pro','PACKAGE_luci-app-store','PACKAGE_luci-app-openclash','PACKAGE_kmod-mt_wifi','PACKAGE_luci-app-mtwifi-cfg','PACKAGE_luci-app-timewol','PACKAGE_luci-theme-argon','PACKAGE_luci-i18n-argon-config-zh-cn']
if MODERN:
    required=[s for s in required if s not in ('PACKAGE_kmod-mt_wifi','PACKAGE_luci-app-mtwifi-cfg','PACKAGE_luci-app-timewol')]
    required += ['PACKAGE_kmod-mt7915e']
    required += [l.strip().split('=')[0].removeprefix('CONFIG_') for l in (ROOT/'config/extra.config').read_text().splitlines() if l.startswith('CONFIG_PACKAGE_') and l.endswith('=y')]
for sym in required:
    assert f'CONFIG_{sym}=y' in config, f'Mandatory symbol lost: {sym}'
assert 'CONFIG_CCACHE=y' in config, 'Compiler cache was not enabled'
# Check selected package definitions before any expensive compilation starts.
selected=set(re.findall(r'^CONFIG_PACKAGE_(.+)=y$',config,re.M))
metadata=(SRC/'tmp/.packageinfo').read_text()
definitions={}
for stanza in metadata.split('\n\n'):
    name=re.search(r'^Package: (.+)$',stanza,re.M)
    if name:
        definitions.setdefault(name.group(1),[]).append(stanza)
duplicates={name:len(definitions[name]) for name in selected if len(definitions.get(name,[]))>1}
assert not duplicates, f'Duplicate selected package definitions: {duplicates}'
provided=set(selected)
for name in selected:
    for stanza in definitions.get(name,[]):
        for aliases in re.findall(r'^Provides: (.+)$',stanza,re.M):
            provided.update(alias.split('=')[0].lstrip('@') for alias in aliases.replace(',',' ').split())
missing=[]
for name in selected:
    for stanza in definitions.get(name,[]):
        for deps in re.findall(r'^Depends: (.+)$',stanza,re.M):
            for dep in deps.split():
                # Conditional/virtual dependencies are resolved by Kconfig;
                # check only unconditional, direct package dependencies here.
                if dep.startswith('+') and not any(c in dep for c in ':@|()'):
                    dep=dep[1:]
                    if dep not in provided:
                        missing.append((name,dep))
assert not missing, f'Selected packages have unselected direct dependencies: {missing}'
(OUT/'preflight.json').write_text(json.dumps({'series':LOCK.get('series'),'firmware_commit':LOCK['firmware']['commit'],'selected_package_count':len(selected),'duplicate_definitions':duplicates,'missing_direct_dependencies':missing,'lan':'192.168.6.1','full_compile_completed':False},indent=2))
shutil.copy2(SRC/'.config',OUT/'build.config')
with (OUT/'diffconfig').open('w') as f: subprocess.run(['./scripts/diffconfig.sh'],cwd=SRC,stdout=f,check=True)
for name in ['source-lock.json','feeds-lock.json']: shutil.copy2(ROOT/name,OUT/name)
with (OUT/'device-changes.patch').open('w') as f: subprocess.run(['git','diff','--','target'],cwd=SRC,stdout=f,check=True)
print('Pinned source, packages, 2 GiB RAM and unchanged partition layout prepared.')
