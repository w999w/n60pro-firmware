# 磊科 N60 Pro · 2GB 定制固件

[![云编译状态](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml/badge.svg)](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml)
[![源码基础](https://img.shields.io/badge/源码-237%20%2F%20padavanonly-blue)](https://github.com/padavanonly/immortalwrt-mt798x-6.6)
[![管理地址](https://img.shields.io/badge/管理地址-192.168.100.1-00897b)](#默认配置)

基于 **237 / padavanonly 的 ImmortalWrt Linux 6.6 源码线**，为磊科 N60 Pro 原厂 **2GB 内存版**准备的 GitHub Actions 云编译工程，集成常用代理、广告过滤、存储和网络管理功能。

> **当前处于构建与验证阶段。** 有附件不代表已有固件：失败或取消的任务也可能上传诊断日志。请确认构建成功，且附件内包含镜像及 SHA256SUMS。构建成功后仍需验证实际设备启动、无线和 IPv6。

**快速入口：** [查看编译进度](https://github.com/w999w/n60pro-firmware/actions) · [功能配置](config/extra.config) · [版本锁定](source-lock.json)

## 默认配置

| 项目 | 配置 |
|---|---|
| 设备 | 磊科 Netcore N60 Pro，原厂 2GB RAM 版本 |
| 管理地址 / LAN 网关 | **192.168.100.1** |
| LAN 网段 | `192.168.100.0/24`，DHCP 分配 `192.168.100.x` |
| 平台 | MediaTek / Filogic · ARM64 |
| 源码线 | ImmortalWrt 24.10 / Linux 6.6，237 分支 |
| 无线方案 | 上游 MTK 驱动与配套管理组件 |
| 内存适配 | N60 Pro 设备树从 512MiB 声明调整为 2GiB |
| 时间 | 北京时间 · `Asia/Shanghai` |

**2GB 是运行内存，不是闪存容量。** 本工程未选择 512MB 硬改闪存版本，保留固定源码中的 N60 Pro 分区布局。内存声明不替代引导程序的 DDR 初始化，上机后需确认识别和稳定性。

## 功能清单

下表为构建配置中的选择，最终以成功构建的软件清单和设备验证结果为准。

| 分类 | 组件 | 用途 |
|---|---|---|
| 应用商店 | **iStore** | 常用插件安装管理 |
| 代理分流 | **OpenClash + Smart Mihomo 核心** | 订阅、策略组、透明代理和规则分流 |
| DNS 广告过滤 | **AdGuard Home 管理插件 + ARM64 核心** | 查询管理和广告域名过滤 |
| 无线与加速 | MTK Wi-Fi 管理、HNAT/WARP、TurboACC、MTK QoS | 配套无线和加速管理 |
| USB 存储 | USB 3.0、自动挂载、ext4 / exFAT / NTFS3 / VFAT / Btrfs | 外接硬盘和常见文件系统 |
| 文件共享 | ksmbd / SMB | 局域网文件共享 |
| VPN / 隧道 | WireGuard、IPsec、Cloudflare Tunnel | 按需设置加密连接 |
| 日常管理 | 中文 LuCI、Argon、网页终端、WOL、Watchcat、内存管理 | 管理、唤醒与维护 |
| 运维工具 | SFTP 服务端、nano、htop、tcpdump 等 | 文件传输、编辑和诊断 |

OpenClash、AdGuard Home 初始不启用，配置完成后再启动。VPN、文件共享及远程管理功能也需按需配置。首版未加入此前停用的 daed 和存在配置缺失问题的应用过滤后端。

## 如何编译和下载

1. 打开 [Actions → Build N60 Pro 2GB](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml)。
2. 点击 **Run workflow** 启动云编译。
3. 等待源码准备、下载、编译、产物收集完成。
4. 打开成功的记录，在 **Artifacts / 附件**下载 `n60pro-2gb-编号`。
5. 解压，确认镜像存在，并核对 `SHA256SUMS`。

修改 main 分支的工作流、构建脚本、配置或版本锁定文件也会触发编译。**只修改 README 不触发重编译。** 附件保留 14 天，重要镜像请保存到本地。

### 附件内容

| 文件 | 说明 |
|---|---|
| `*netcore_n60-pro*squashfs-sysupgrade.bin` | 成功构建的 N60 Pro 升级镜像 |
| `SHA256SUMS` | 产物校验值 |
| `build.config` / `diffconfig` | 完整及精简构建配置 |
| `source-lock.json` / `feeds-lock.json` | 固定的源码、插件和软件源提交 |
| `device-changes.patch` | 内存与驱动选择改动 |
| `*.manifest` / `*.buildinfo` / `*.json` | 构建实际输出的软件清单与元数据 |
| `prepare.log` / `download.log` / `build*.log` | 准备、下载和编译日志 |

## 刷入与配置迁移

- 先确认设备型号、现有 U-Boot 与分区布局兼容，保留离线备份。
- 跨固件版本按功能选择性恢复配置，不整体覆盖新系统的 `/etc`、可写层、驱动或内核模块。
- 本工程没有自动刷机、刷写 U-Boot、修改分区或格式化硬盘的脚本。
- 不要将原始 MTD 备份、诊断日志附件或恢复镜像当作升级镜像。

仓库不包含个人密码、机场订阅、控制器密钥、备份、设备 MAC 或磁盘 UUID。

AI 美区优先规则、多订阅更新、流媒体选点、NAS 内网解析、AdGuard/OpenClash DNS 链路和维护计划属于后续私有配置迁移。**安装插件不会自动恢复这些设置。**

<details>
<summary><strong>源码来源与版本说明</strong></summary>

| 项目 | 上游来源 |
|---|---|
| 固件基础 | [padavanonly/immortalwrt-mt798x-6.6](https://github.com/padavanonly/immortalwrt-mt798x-6.6) |
| OpenClash | [vernesong/OpenClash](https://github.com/vernesong/OpenClash) |
| Smart 核心 | [vernesong/mihomo](https://github.com/vernesong/mihomo) |
| iStore | [istoreos/istore](https://github.com/istoreos/istore) |
| AdGuard 管理插件 | [rufengsuixing/luci-app-adguardhome](https://github.com/rufengsuixing/luci-app-adguardhome) |
| AdGuard 核心 | [AdguardTeam/AdGuardHome](https://github.com/AdguardTeam/AdGuardHome) |
| Argon | [jerrykuku/luci-theme-argon](https://github.com/jerrykuku/luci-theme-argon) |

当前固件源码固定为 `ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8`，其他提交见锁定文件；两个预置核心的下载均校验 SHA256。固定版本不代表永远是最新版本，更新时需重新核对兼容性和构建结果。

</details>

## 项目说明

本项目是个人定制构建工程，**不是 ImmortalWrt 官方发布固件**，也不代表上游作者为定制配置背书。各固件组件保留上游许可证；本工程脚本与配置按 MIT 条款提供。
