# N60 Pro 2GB 上游构建审阅

审阅日期：2026-11-08。范围为本仓库锁文件、prepare.py、extra.config、build.yml，并直接读取锁定提交的一手源码；未刷写设备，未把正在进行的 Actions 当作编译成功。结论：未发现上述代码中可据现有证据认定的必然编译阻断或分区不匹配；仍需区分“生成固件”与“实机验证通过”。

## 设备与镜像

- 锁定的上游 N60 Pro DTS 原为 512MiB（`0x20000000`）；本地只将长度改为 `0x80000000`，即从 `0x40000000` 开始的 2GiB 内存。五个分区的偏移/长度完全吻合用户当前布局：BL2 `0/0x100000`、env `0x100000/0x80000`、factory `0x180000/0x200000`、fip `0x380000/0x200000`、ubi `0x580000/0x7280000`。prepare.py 没有修改这些分区。[锁定 DTS](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/target/linux/mediatek/dts/mt7986a-netcore-n60-pro.dts)
- 上游该设备只定义 `sysupgrade-tar | append-metadata`；升级脚本把 `netcore,n60-pro` 交给 `nand_do_upgrade`。因此收集到的是现有兼容 OpenWrt/ImmortalWrt 系统的 NAND sysupgrade 包，不能据 `.bin` 后缀称为可直接写入整个闪存或任意引导器的 factory 镜像。[设备镜像定义](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/target/linux/mediatek/image/filogic.mk)、[平台升级脚本](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/target/linux/mediatek/filogic/base-files/lib/upgrade/platform.sh)
- **明确的验证边界**：DTS 改动只声明 Linux 可见内存；该 sysupgrade 配方不替换 BL2/fip，因而不能修复或证明当前引导链的 DDR 初始化。现有设备是否能稳定使用 2GiB，仍须已有启动日志及运行结果佐证。collect.py 的包大小检查也只是粗筛，不能独立证明 UBI 可用空间或启动兼容性。

## MTK 无线驱动

- N60 Pro 原始 profile 默认 `kmod-mt7915e` 等 mt76 包；prepare.py 将其替换为 `kmod-mt_wifi kmod-warp`，与用户要求的 MTK 驱动相符。仅勾选 LuCI 无线界面不能代替这一步。[设备 profile](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/target/linux/mediatek/image/filogic.mk)
- 继承的 `mt7975-ipailna-high-power.config` 实际包含 MT7986、AX6000、conninfra、MTK 无线/硬件加速及 mtwifi-cfg 配置；驱动 Makefile 自动依赖 wifi-dats、conninfra、hnat、warp。SoC DTS 也已含 MTK `wbsys` 节点，因此不能把“本地未再手写这些依赖/节点”列为缺陷。[上游 defconfig](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/defconfig/mt7975-ipailna-high-power.config)、[驱动 Makefile](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/package/mtk/drivers/mt_wifi/Makefile)、[SoC DTS](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/target/linux/mediatek/files-6.6/arch/arm64/boot/dts/mediatek/mt7986a.dtsi)
- MT7986 的 l1profile 明确指定 EEPROM offset `0x0`、大小 `0x5000`；不能仅凭 defconfig 中 `RT_FIRST_IF_RF_OFFSET=0xc0000` 就断言本构建读错校准区。源码审阅不代替实际双频启动、MAC/校准读取和无线稳定性验证。[l1profile](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/package/mtk/drivers/wifi-profile/files/mt7986/l1profile.dat)

## 插件、默认值与工作流

- OpenClash 锁定版本明确识别 `core_type=Smart`，使用 `/etc/openclash/core/clash_meta`；AdGuardHome 锁定版本默认核心路径为 `/usr/bin/AdGuardHome/AdGuardHome`。本地两个内置核心的路径与之吻合；下载同时校验锁定 SHA256。当前准备脚本也已兼容 AdGuard 压缩包中 `./AdGuardHome/AdGuardHome` 的路径前缀。[OpenClash init](https://github.com/vernesong/OpenClash/blob/e553e82e01c697aefbe1555261a503f425e00ccd/luci-app-openclash/root/etc/init.d/openclash)、[AdGuardHome init](https://github.com/rufengsuixing/luci-app-adguardhome/blob/37fdf502b99328b37c9ef4c4387f069f67253f85/root/etc/init.d/AdGuardHome)
- 本地首次启动脚本明确写入 LAN `192.168.100.1/24`；OpenClash 和 AdGuardHome 默认关闭，未内置订阅/个人配置。extra.config 选择 iStore、两款插件、常用 USB/文件系统、SMB、定时唤醒、WireGuard、终端及 MTK 加速。prepare.py 会在 `make defconfig` 后校验关键符号，但“之前常用功能”的完整一致性仍应以最终 `build.config`/manifest 与用户旧清单比较，不能由这些选择行全部推定。
- 固件、feeds、插件均锁定提交；feeds 来源与上游 feeds.conf.default 的四个项目一致。README 的快速开始仍写另一个仓库名，实际构建应以 source-lock.json 的指定仓库和提交为准。[上游 feeds](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/feeds.conf.default)、[上游 README](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/README.md)
- 工作流显式 `shell: bash`，GitHub 使用 `bash --noprofile --norc -eo pipefail`，故 `make ... | tee ...` 的 make 失败不会被 tee 成功掩盖；并行编译失败后的单线程重试也会正确传播最终失败。`if: always()` 可在失败后保留诊断资料。[GitHub 工作流 shell 定义](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsshell)
- 上游 README 列出的宿主依赖比本工作流更多，但那是通用环境清单；仅凭缺少若干 APT 名称，不能认定 GitHub runner 上实际缺依赖。应由本次准备/下载/编译日志中的明确错误及最终构建状态判断，当前源码审阅未证实具体依赖阻断。[上游构建要求](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/README.md)

本审阅只新增此说明，没有修改构建代码、配置或设备。

## 下载阶段补充核对

当前任务提供的现象是 download 阶段在 tools/tar、zstd、flock、sed 等输出后数分钟无新增可见日志；这仅证明等待，尚不证明下载失败，也不足以定位某一个 URL。尤其 flock 直接编译仓内 C 文件，没有外部 PKG_SOURCE_URL，不能据 `tools/flock/download` 一行认定下载卡在 flock。[flock Makefile](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/tools/flock/Makefile)

锁定 downloader 的镜像顺序为：scripts/localmirrors → CONFIG_LOCALMIRROR → DOWNLOAD_MIRROR → 包自身 URL（含 @GNU 展开）→ ImmortalWrt 官方缓存 → OpenWrt 官方缓存。tar/sed 的 @GNU 展开顺序先腾讯、阿里、清华、中科大，GNU 自有域名位于其后；zstd 自身 URL 是 Facebook GitHub release。这里能确认的是顺序，不能据此推定 GitHub runner 上某镜像不可用。[download.pl](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/scripts/download.pl)、[镜像表](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8/scripts/projectsmirrors.json)

如果确需给下一次执行设置无进展退出条件，建议使用 downloader 已支持的环境变量，保留原始源及 SHA256：

```yaml
env:
  CURL_OPTIONS: --speed-limit 1 --speed-time 60 --max-time 600 --retry 0
  DOWNLOAD_MIRROR: https://sources.cdn.openwrt.org;https://sources.openwrt.org
```

`CURL_OPTIONS` 在默认 `--retry 5` 后追加，覆盖重试数；连接仍沿用默认 20 秒限制，传输低于 1 字节/秒持续 60 秒会退出，单次请求最多 600 秒。关闭 curl 内部重试的理由是 downloader 将 stdout 流直接写入文件及哈希：curl 官方明确说明，管道输出无法在重试时撤销已输出的部分，故“部分下载后超时再重试”可能拼接残片。现有哈希会拒绝这种结果；用 `--retry 0` 则由 downloader 清理失败文件后切换下一镜像，避免该浪费。上述时间是每次请求上限，镜像列表完整遍历的总耗时仍可能更长。官方缓存优先只调整候选顺序，不绕过哈希；缺失文件会继续原始 URL/其余缓存。[curl retry](https://curl.se/docs/manpage.html#--retry)、[max-time](https://curl.se/docs/manpage.html#--max-time)、[speed-time](https://curl.se/docs/manpage.html#--speed-time)

此处仅记录建议，没有修改工作流或干预当前运行。

## GitHub 运行器下载实测补充（2026-11-08）

独立诊断任务42461532610在GitHub Ubuntu22.04运行器下载锁定的sed-4.9.tar.gz：ImmortalWrt源约2.98秒、腾讯约2.63秒、阿里约0.77秒完成，三者SHA256均与工具Makefile一致；OpenWrt两个源在本轮25秒测试时限内只收到部分内容，不能据此称其文件错误或长期不可用。不同任务的运行器实例/区域可能不同，本测试不定位主任务具体等待的URL。

主构建42460778880随后自然完成Download阶段并进入Compile，故本轮没有应用上述建议环境变量，也没有为下载策略重新取消构建。来源：[下载诊断日志](https://github.com/w999w/n60pro-firmware/actions/runs/42461532610)、[主构建](https://github.com/w999w/n60pro-firmware/actions/runs/42460778880)。

配置产物复核：58项要求启用的配置在make defconfig后全部保留，标准mt7915e/mt7986固件包和wpad-openssl未混入；feeds安装完成后的配置合成无依赖警告。首启脚本中LAN192.168.100.1/24、Asia/Shanghai及时区提交均存在，未包含格式化/刷写命令。这些检查不代替最终manifest和实际设备验证。
