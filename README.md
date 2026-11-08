# N60 Pro 2GB firmware build

Generic firmware built with GitHub Actions from 237/padavanonly's Linux 6.6 tree, pinned to ec9ef10efc65da1e6d1de4e2c043c0e13d08eed8. It is a custom build, not an official ImmortalWrt release.

Includes iStore, OpenClash with a checksum-verified Smart Mihomo core, AdGuard Home with its verified arm64 core, Argon, MTK Wi-Fi/HNAT/QoS management, ext4/exFAT/NTFS3/Btrfs USB storage, SMB, WOL, Watchcat, web terminal, Cloudflare Tunnel, IPsec and WireGuard support. Unconfigured proxy/VPN/file sharing/remote terminal services are disabled initially; configure before use. daed and application filtering are not included in this first build because they were disabled/unreliable in the previous deployment.

The upstream N60 Pro DT memory declaration is explicitly changed from 512 MiB to 2 GiB. The NAND partition map is not changed. The selected device remains netcore_n60-pro, not a 512 MB flash modification. MTK driver settings come from the pinned upstream radio configuration; standard mt76 packages are removed from this device profile to avoid mixing driver stacks.

Start the **Build N60 Pro 2GB** workflow from Actions (or push a build configuration change to main). Artifacts contain the sysupgrade.bin image, checksums, full config/diffconfig, exact source/feed commits, device patch, manifests and diagnostic logs. Only a green workflow with a firmware image is a successful build. A successful build does not replace device boot/Wi-Fi/IPv6 validation.

This repository contains no subscriptions, passwords, router backups, private domain overrides, fixed MACs or disk UUIDs. Existing private settings must be migrated separately. No script flashes a router, changes its bootloader or formats a disk. Never feed a raw MTD backup to the upgrade UI. Confirm bootloader/partition compatibility before installing any image.

Base source: https://github.com/padavanonly/immortalwrt-mt798x-6.6
OpenClash: https://github.com/vernesong/OpenClash
iStore: https://github.com/istoreos/istore
AdGuard LuCI: https://github.com/rufengsuixing/luci-app-adguardhome
AdGuard core: https://github.com/AdguardTeam/AdGuardHome

Source files retain their upstream licenses. Build scripts/configuration in this repository are provided under the MIT license; firmware components retain their respective licenses.
