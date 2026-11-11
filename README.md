# 磊科 N60 Pro · 定制固件

[![云编译状态](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml/badge.svg)](https://github.com/w999w/n60pro-firmware/actions/workflows/build.yml)
[![系统版本](https://img.shields.io/badge/ImmortalWrt-25.12.2-1685D1?style=flat-square)](https://github.com/immortalwrt/immortalwrt/tree/v25.12.2)
[![内核版本](https://img.shields.io/badge/Linux-6.12.103-333333?style=flat-square)](https://github.com/immortalwrt/immortalwrt/blob/v25.12.2/target/linux/generic/kernel-6.12)
[![架构](https://img.shields.io/badge/arch-aarch64-6E4C13?style=flat-square)](https://github.com/w999w/n60pro-firmware/wiki/Requirements)

为 **磊科 N60 Pro 原厂 2GB 内存版**准备的通用固件：保留代理、DNS、外接硬盘、设备与带宽监控，以及兼容的网络加速能力。基于 ImmortalWrt 25.12.2 / Linux 6.12.103，由 GitHub Actions 每日自动构建。

> 详细文档已按专题拆分到 **[Wiki](https://github.com/w999w/n60pro-firmware/wiki)**，本 README 只保留概览与入口。

## 关键信息

| 项 | 值 |
| --- | --- |
| **管理地址** | **https://192.168.6.1** （HTTP 自动跳转；自签证书首次访问需手动信任） |
| 适配机型 | Netcore N60 Pro，2GB RAM ＋ 128MB NAND |
| 平台 / 架构 | MediaTek Filogic / ARM64 |
| 镜像格式 | `sysupgrade.itb`（FIT / UBI） |
| 无线 | 2.4G ＋ 5G，`sae-mixed`（SAE ＋ WPA2/WPA3 过渡）；5G 支持 160MHz |
| 代理 | OpenClash ＋ ARM64 Smart Mihomo 内核 |
| 监控 | Bandix 设备流量 ＋ collectd 系统统计 |
| 外置存储 | fstab 按 UUID 挂载，支持 ext4 / exFAT / NTFS3 / Btrfs / SMB |

## 不依赖外接硬盘

镜像**不要求**插着硬盘或存在 NAS：OpenClash 的核心、规则与 provider 放在内存盘，Bandix 的数据目录开机时自动判断——硬盘在线就用盘上的目录（历史可持久化），离线就退回内存盘，功能不中断，只是重启后历史清零。插拔硬盘由 hotplug 自动切换，无需手动改配置。

## 构建与下载

| 触发方式 | 执行内容 |
| --- | --- |
| **每天 01:00（北京时间）** | 自动完整编译 |
| 向 `main` 推送改动 | 只跑预检与源码下载，**不编译** |
| 手动 `workflow_dispatch` 勾选 `full_build` | 完整编译；输入未变化时可勾 `force_rebuild` 强制重建 |

产物在 Actions 附件中（`n60pro-25.12-2gb-编号`，含 `sysupgrade.itb` 与 `SHA256SUMS`），保留 14 天。源码与插件版本锁定在 `source-lock.json` 和 `feeds-lock.json`，包选择在 `config/extra.config`。

构建机制、指纹跳过、Actions 状态见 **[构建与发布](https://github.com/w999w/n60pro-firmware/wiki/Build-and-Release)**。

## 刷入

**25.12 使用官方 FIT/UBI 镜像体系，不能套用旧 237 版 24.10 的 `sysupgrade.bin` 方式。** 刷入前核对现有引导与分区布局；建议不勾"保留配置"，让首启脚本生效。

刷完后：

- LAN 变为 `192.168.6.1`，电脑需重新获取同网段地址
- 重启后 **5G 会晚约 60 秒出现**——160MHz 覆盖 DFS 信道，hostapd 要先做雷达检测，属正常现象

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

[ImmortalWrt](https://github.com/immortalwrt/immortalwrt/tree/v25.12.2) · [OpenClash](https://github.com/vernesong/OpenClash) · [MosDNS](https://github.com/sbwml/luci-app-mosdns) · [Bandix](https://github.com/timsaya/luci-app-bandix) · [Argon](https://github.com/jerrykuku/luci-theme-argon) · [iStore](https://github.com/istoreos/istore)

## 致谢

本项目在 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) 与 ChatGPT 的协助下完成。

[![](https://img.shields.io/badge/powered_by-dsh-4D6BFE?style=flat-square&logo=deepseek&logoColor=white)](https://github.com/deepseek-ai/deepseek-harness)
[![](https://img.shields.io/badge/assisted_by-ChatGPT-10A37F?style=flat-square&logo=openai&logoColor=white)](https://chatgpt.com)
