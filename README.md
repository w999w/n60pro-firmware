# 磊科 N60 Pro · ImmortalWrt 25.12 定制固件

[查看云编译](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml)

面向原厂 **2GB RAM＋128MB NAND**，基于官方 **ImmortalWrt v25.12.2 / Linux 6.12.103**。默认 LAN 管理地址 **192.168.100.1**，北京时间。此仓库为个人定制工程，不是官方发布镜像。

## 功能清单

| 类别 | 选择的功能 |
| --- | --- |
| 代理 | OpenClash＋已校验的 ARM64 Smart Mihomo 核心 |
| DNS | AdGuard Home＋核心、MosDNS |
| 管理 | 中文 LuCI、Argon、iStore、TaskPlan |
| 监控 | Bandix、LuCI Statistics、CPU/内存/负载/接口/磁盘统计、htop |
| 存储 | USB3、UAS、自动挂载、ext4/exFAT/NTFS3/VFAT/Btrfs、硬盘休眠、SMB |
| 网络 | 官方 mt76 Wi-Fi 驱动、网口/交换机驱动、IPv6、nft 流量卸载支持 |

不集成远程接入/VPN、DDNS、Lucky、上网时间控制、设备限速、下载器、Docker或媒体服务器。未移植第三方 TurboACC 的防火墙替换及内核补丁；采用官方驱动及卸载机制，实际加速效果及与 OpenClash 的兼容性需要上机验证。监控开启卸载流量时可能无法完整统计，需在精确统计与卸载之间实际取舍。

OpenClash、AdGuard Home、MosDNS 默认停用，后续配置统一 DNS 链路，避免抢占端口。内置插件不等于恢复私人订阅、AI规则或NAS设置。仓库不保存密码、订阅和备份。

## 编译与下载

提交构建配置会触发 Actions，也可在工作流页手动运行。使用全部 CPU 并行编译，失败时单线程输出详细日志；缓存源码下载及最多2GB的 CCache，加速后续构建。首轮缓存尚未形成，仍需完整编译。

成功后下载附件 `n60pro-25.12-2gb-编号`，其中应含 `*netcore_n60-pro*squashfs-sysupgrade.itb`、清单、配置及 SHA256SUMS。失败和取消的构建也会上传日志，日志附件不能刷机。附件保留14天。

准备阶段验证所有明确选择的包未被配置系统删除，收集阶段核对FIT文件头和软件清单。编译成功不代替设备启动、无线、USB及代理验证。

## 刷机兼容性

**25.12 为官方 FIT/UBI 镜像体系，不能直接按旧237版24.10的 sysupgrade.bin 刷入方法操作。** 需先核对现有引导与分区布局。本工程仅把设备树内存声明从512MiB改为2GiB，不自动修改分区，不写引导，不格式化硬盘。默认100.1地址在首次初始化应用，旧配置迁移可能覆盖它。

## 源码

- [ImmortalWrt](https://github.com/immortalwrt/immortalwrt/tree/v25.12.2)
- [OpenClash](https://github.com/vernesong/OpenClash)
- [AdGuard Home LuCI](https://github.com/rufengsuixing/luci-app-adguardhome)
- [MosDNS](https://github.com/sbwml/luci-app-mosdns)
- [Bandix 界面](https://github.com/timsaya/luci-app-bandix) / [核心打包](https://github.com/timsaya/openwrt-bandix)
- [TaskPlan](https://github.com/sirpdboy/luci-app-taskplan)
- [Argon](https://github.com/jerrykuku/luci-theme-argon) / [iStore](https://github.com/istoreos/istore)

准确提交、核心校验值见 source-lock.json，feeds采用官方v25.12.2配套固定提交。docs/upstream-build-review.md是旧24.10构建的历史审阅，不代表25.12适配结论。
