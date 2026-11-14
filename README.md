# 磊科 N60 Pro · 定制固件

[![云编译状态](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml/badge.svg)](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml)
[![系统版本](https://img.shields.io/badge/ImmortalWrt-25.12.2-1685D1?style=flat-square)](https://github.com/immortalwrt/immortalwrt/tree/v25.12.2)
[![内核版本](https://img.shields.io/badge/Linux-6.12.103-333333?style=flat-square)](https://github.com/immortalwrt/immortalwrt/blob/v25.12.2/target/linux/generic/kernel-6.12)
[![架构](https://img.shields.io/badge/arch-aarch64-6E4C13?style=flat-square)](https://github.com/w999w/n60pro-firmware/wiki/Requirements)

[![下载固件](https://img.shields.io/badge/下载固件-Releases-2ea44f?style=for-the-badge)](https://github.com/w999w/n60pro-firmware/releases/tag/nightly)
[![云编译](https://img.shields.io/badge/云编译-Actions-2088ff?style=for-the-badge)](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml)
[![使用文档](https://img.shields.io/badge/使用文档-Wiki-8b5cf6?style=for-the-badge)](https://github.com/w999w/n60pro-firmware/wiki)

为 **磊科 N60 Pro 原厂 2GB 内存版**准备的通用固件：保留代理、DNS、外接硬盘、设备与带宽监控，以及兼容的网络加速能力。基于 ImmortalWrt 25.12.2 / Linux 6.12.103，GitHub Actions 每天北京时间 01:00 触发，输入指纹命中时跳过编译。

> 详细文档已按专题拆分到 **[Wiki](https://github.com/w999w/n60pro-firmware/wiki)**，本 README 只保留概览与入口。

## 关键信息

| 项 | 值 |
| --- | --- |
| **管理地址** | **https://192.168.6.1** （HTTP 自动跳转；自签证书首次访问需手动信任） |
| 适配机型 | Netcore N60 Pro，2GB RAM ＋ 128MB NAND |
| 平台 / 架构 | MediaTek Filogic / ARM64 |
| 镜像格式 | `sysupgrade.itb`（FIT / UBI） |
| 无线 | 官方 mt76 驱动，2.4G＋5G；SSID、加密与频宽按设备实际配置 |
| 代理 | OpenClash ＋ ARM64 Smart Mihomo 内核 |
| 监控 | Bandix 设备流量 ＋ collectd 系统统计 |
| 外置存储 | fstab 按 UUID 挂载，支持 ext4 / exFAT / VFAT / NTFS3 / Btrfs；不集成 SMB |

## 镜像默认与设备现状

| 项目 | 镜像默认 | 当前设备（2026-11-14） |
| --- | --- | --- |
| 系统 / 内核 | **25.12.2 / 6.12.103** | 同系列 |
| OpenClash | 安装 Smart 构建核心，**默认关闭** | 普通 Meta alpha-gbc76c13，redir-host，已启用 |
| 监控 / 休眠 | Bandix、collectd、hd-idle 自启 | 已启用 |
| 私人配置 | 不包含订阅、设备命名或 NAS 租约 | 仅在路由器私下配置 |

保留 iStore、Argon、OpenClash、存储驱动、设备与带宽监控。**不集成** AdGuard Home、MosDNS、SMB/ksmbd、Watchcat、远程组网、DDNS、下载器、限速和上网时间控制。

设备侧：AI 按“DMIT 美区 AI/家宽 → DMIT 其他美区 → 组合订阅美区”回退；游戏、Apple、DeepSeek 直连；linux.do 走日常代理。用户确认当前配置改善 LOL 延迟，保持现有设置。上述个人分流不预置进通用镜像。

## 外接硬盘与目录

OpenClash 核心位于**闪存真实目录**，规则与 provider 缓存放内存盘；不再把整个 OpenClash 目录链接到硬盘。Bandix 数据目录助手优先使用已挂载的硬盘，否则回退内存盘。

当前设备已有启动重建钩子；构建脚本与设备钩子尚不完全一致，新刷镜像仍需验证重启与无盘场景，不能把设备实测直接当作镜像保证。详见 [刷机与首启](https://github.com/w999w/n60pro-firmware/wiki/Flash-and-First-Boot)。

## 构建与下载

| 触发方式 | 执行内容 |
| --- | --- |
| **每天 01:00（北京时间）** | 自动运行；成功指纹命中则跳过编译 |
| 向 `main` 推送改动 | 只跑预检与源码下载，**不编译** |
| 手动 `workflow_dispatch` 勾选 `full_build` | 完整编译；输入未变化时可勾 `force_rebuild` 强制重建 |

产物在 Actions 附件中（`n60pro-25.12-2gb-编号`，含 `sysupgrade.itb` 与 `SHA256SUMS`），保留 14 天。固件与插件提交记录在 `source-lock.json` 和 `feeds-lock.json`，包选择在 `config/extra.config`。Smart 核心当前跟随滚动发布，未固定资产哈希，也未纳入构建指纹；详见 Wiki 已知缺口。

构建机制、指纹跳过、Actions 状态见 **[构建与发布](https://github.com/w999w/n60pro-firmware/wiki/Build-and-Release)**。

## 刷入

**25.12 使用官方 FIT/UBI 镜像体系，不能套用旧 237 版 24.10 的 `sysupgrade.bin` 方式。** 刷入前核对现有引导与分区布局；建议不勾"保留配置"，让首启脚本生效。

刷完后：

- LAN 变为 `192.168.6.1`，电脑需重新获取同网段地址
- 若设备选择覆盖 DFS 的 160MHz 信道，5G 启动可能等待 CAC；具体时长依地区与信道而定

步骤、首启默认值与验证清单见 **[刷机与首启](https://github.com/w999w/n60pro-firmware/wiki/Flash-and-First-Boot)**。

## 文档导航

| 页面 | 内容 |
| --- | --- |
| [需求与范围](https://github.com/w999w/n60pro-firmware/wiki/Requirements) | 目标硬件、功能清单、明确不做的、订阅结构与分流意图 |
| [构建与发布](https://github.com/w999w/n60pro-firmware/wiki/Build-and-Release) | 关键文件、触发规则、指纹跳过、Actions 快照、兼容边界 |
| [刷机与首启](https://github.com/w999w/n60pro-firmware/wiki/Flash-and-First-Boot) | 刷写命令、首启默认值、验证清单、软链拓扑 |
| [OpenClash](https://github.com/w999w/n60pro-firmware/wiki/OpenClash) | 代理组、AI 链路、规则与 DNS、更新机制、优化记录 |
| [网络与无线](https://github.com/w999w/n60pro-firmware/wiki/Network-and-Wireless) | 接口地址、IPv6 relay、无线与 160MHz/DFS、转发性能参数 |
| [运维手册](https://github.com/w999w/n60pro-firmware/wiki/Operations) | 定时任务、日志归档、备份与回滚点、常用命令 |
| [故障与排查](https://github.com/w999w/n60pro-firmware/wiki/Troubleshooting) | 排障决策树、构建故障记录、已知无害日志 |
| [变更记录](https://github.com/w999w/n60pro-firmware/wiki/Changelog) | 按日期倒序的完整时间线 |

## 边界

公开仓库与 Wiki **不保存**账号密码、机场订阅、控制器密钥、MAC、UUID、私人配置或备份。私人订阅与 NAS 设置另行私下迁移。

本项目为个人定制构建工程，**不是 ImmortalWrt 官方发布镜像**。

## 源码

[ImmortalWrt](https://github.com/immortalwrt/immortalwrt/tree/v25.12.2) · [OpenClash](https://github.com/vernesong/OpenClash) · [Bandix](https://github.com/timsaya/luci-app-bandix) · [Argon](https://github.com/jerrykuku/luci-theme-argon) · [iStore](https://github.com/istoreos/istore)

## 致谢

本项目在 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) 与 ChatGPT 的协助下完成。

[![](https://img.shields.io/badge/powered_by-dsh-4D6BFE?style=flat-square&logo=deepseek&logoColor=white)](https://github.com/deepseek-ai/deepseek-harness)
[![](https://img.shields.io/badge/assisted_by-ChatGPT-10A37F?style=flat-square&logo=openai&logoColor=white)](https://chatgpt.com)
