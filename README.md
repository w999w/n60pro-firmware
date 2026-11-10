# 磊科 N60 Pro · 定制固件

[![云编译状态](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml/badge.svg)](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml)
[![系统版本](https://img.shields.io/badge/ImmortalWrt-25.12.2-1685D1?style=flat-square)](https://github.com/immortalwrt/immortalwrt/tree/v25.12.2)
[![内核版本](https://img.shields.io/badge/Linux-6.12.103-333333?style=flat-square)](https://github.com/immortalwrt/immortalwrt/blob/v25.12.2/target/linux/generic/kernel-6.12)

为 **磊科 N60 Pro 原厂 2GB 内存版**准备的通用固件：保留代理、DNS、外接硬盘、设备与带宽监控，以及兼容的网络加速能力。

> **版本标签表示当前构建目标，不表示镜像已经完成编译或通过上机验证。** 构建状态与接手事项见 [Actions](https://github.com/w999w/n60pro-firmware/actions) 和 [项目 Wiki](https://github.com/w999w/n60pro-firmware/wiki)。

## 系统与硬件

| 项目 | 当前配置 |
| --- | --- |
| **系统版本** | **ImmortalWrt 25.12.2**，官方稳定标签 |
| **Linux 内核** | **6.12.103**，采用该系统版本配套内核 |
| 适配机型 | Netcore N60 Pro，2GB RAM＋128MB NAND |
| 平台 / 架构 | MediaTek Filogic / ARM64 |
| **管理地址** | **http://192.168.6.1** |
| LAN 网段 | 192.168.6.0/24 |
| WAN 上网 | DHCP，接上级中兴路由器，由中兴拨号 |
| 时区 | Asia/Shanghai，北京时间 |
| 无线方案 | 官方 mt76 驱动及设备配套无线固件 |
| 镜像格式 | 官方 FIT / UBI：`sysupgrade.itb` |

2GB 是运行内存；128MB 是板载闪存。外接硬盘另计。源码与插件采用固定提交，详见 [版本锁定](source-lock.json) 和 [配套 feeds](feeds-lock.json)。

## 保留的功能

| 分类 | 配置 | 用途 |
| --- | --- | --- |
| **代理分流** | **OpenClash＋ARM64 Smart Mihomo 核心** | 订阅管理、规则分流、AI与流媒体策略 |
| **DNS 与广告过滤** | **AdGuard Home＋核心、MosDNS** | 广告域名过滤、DNS分流和缓存 |
| 管理界面 | 中文 LuCI、Argon、iStore | 中文后台、主题、插件商店 |
| **设备与带宽监控** | **Bandix** | 设备流量与带宽使用情况 |
| 系统统计 | LuCI Statistics / collectd、htop | CPU、内存、负载、网络接口和磁盘统计 |
| 硬件状态 | 系统状态页及设备驱动 | 查看联网设备、接口及硬件支持的温度信息 |
| **外接硬盘** | USB 3.0、UAS、自动挂载、e2fsprogs | 识别、挂载和维护USB存储 |
| 文件系统 | ext4、exFAT、NTFS3、VFAT、Btrfs | 支持常见磁盘格式 |
| 局域网共享 | SMB / ksmbd | 电脑访问路由器外接硬盘 |
| 磁盘维护 | 硬盘休眠管理 | 按需配置硬盘休眠 |
| **网络性能** | 官方网口、交换机、Wi-Fi驱动，nft流量卸载支持 | 保留适配的转发与加速能力 |
| 日常维护 | TaskPlan、Watchcat、nano、tcpdump | 定时任务、维护和网络诊断 |

以上为构建配置中的选择，最终以成功构建的 manifest 和设备验证结果为准。没有同时集成旧 wrtbwmon，以 Bandix 和系统统计覆盖监控需求。

**加速说明：** 本版采用官方驱动及卸载机制，未加入需要替换防火墙的第三方 TurboACC 补丁。流量卸载可能影响监控统计完整性，也需核对与 OpenClash 的兼容性；组件存在不等于已启用或已完成性能调优。

## 默认启停状态

| 状态 | 功能 |
| --- | --- |
| **默认启用** | 基础联网、路由器后台、iStore、Bandix流量监控、collectd系统统计 |
| **默认停用，按需开启** | OpenClash、AdGuard Home、MosDNS、SMB、Watchcat、硬盘休眠服务、TaskPlan |

Bandix默认使用内存目录，不持久化流量数据，重启后历史清空，减少闪存写入。代理和DNS服务需统一配置后再启动，避免端口冲突。

## 精简范围

按需求不集成：DDNS、Lucky、VPN/远程接入、异地组网、内网穿透、上网时间控制、设备限速、带宽整形、各类下载器、Docker及媒体服务器。必要的本地SSH管理保留。

私人订阅、AI美区选点、流媒体策略及NAS设置不写入公开镜像工程；仓库和Wiki不保存密码、密钥或私人备份。

## 云编译与下载

全部构建文件保存在本仓库，云端执行，不依赖个人电脑路径。换电脑或AI后，读取 [Wiki交接说明](https://github.com/w999w/n60pro-firmware/wiki) 即可继续。

1. 提交构建配置，或手动运行工作流且保持 `full_build` 未勾选：执行**预检与源码下载**。
2. 预检通过后，手动运行并勾选 `full_build`：执行**完整编译**。
3. 完整编译成功后，下载 `n60pro-25.12-2gb-编号` 附件，核对镜像及 `SHA256SUMS`。

编译使用运行器全部CPU，并缓存下载源码与最多2GB的CCache；缓存丢失可重新构建。准备阶段检查包选择及依赖，产物收集阶段检查FIT文件头与软件清单。首次完整编译仍需较长时间。

> 预检成功不等于固件编译成功。失败或取消的任务也可能上传日志附件；只有包含真实镜像的成功完整构建才有可交付固件。Actions附件保留14天。

## 刷入条件

**25.12使用官方FIT/UBI镜像体系，不能直接沿用旧237版24.10的刷入方法。** 刷入前需核对现有引导与分区布局。工程仅修改2GiB内存声明，不自动改分区、刷引导或格式化硬盘。

默认192.168.6.1地址在首次初始化时应用，迁移旧配置可能覆盖它。编译成功后仍需验证实际启动、无线、USB、IPv6及代理功能。

## 源码与文档

[ImmortalWrt](https://github.com/immortalwrt/immortalwrt/tree/v25.12.2) · [OpenClash](https://github.com/vernesong/OpenClash) · [AdGuard LuCI](https://github.com/rufengsuixing/luci-app-adguardhome) · [MosDNS](https://github.com/sbwml/luci-app-mosdns) · [Bandix界面](https://github.com/timsaya/luci-app-bandix) / [核心打包](https://github.com/timsaya/openwrt-bandix) · [TaskPlan](https://github.com/sirpdboy/luci-app-taskplan) · [Argon](https://github.com/jerrykuku/luci-theme-argon) · [iStore](https://github.com/istoreos/istore)

本项目为个人定制构建工程，不是ImmortalWrt官方发布固件。旧版审阅文档 [upstream-build-review.md](docs/upstream-build-review.md) 仅记录24.10历史情况，不代表25.12已经验证。
