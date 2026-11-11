# Rabbit World

基于 Minecraft Java 1.21.1 和 NeoForge 21.1.265 的整合包，包含 Minecraft Transit Railway、FTB Quests 和 Rabbit 系列模组。

## 项目文件

- `manifest.json` 固定 Minecraft、NeoForge 和 CurseForge 下载项的版本。
- `overrides/config/` 包含整合包配置和 FTB 任务。
- `overrides/kubejs/` 包含 KubeJS 脚本及资源。
- Rabbit 系列 JAR 由构建脚本从各模组仓库的最新正式 GitHub Release 下载。

仓库只保留整合包所需文件。本地地图缓存、旧任务备份、Numen MCP 连接配置和 BlueMap SQL 连接配置由使用者自行管理。

## 安装客户端

从 Rabbit World 的 GitHub Releases 下载 `Rabbit-World-Client-*.zip`，直接导入 CurseForge。

也可以用 Python 3.9 或更新版本在本地运行 `python3 scripts/build.py client`，输出到 `dist/`。

## GitHub Actions

推送 `v*` 标签后，**Build Rabbit World** 会构建客户端 ZIP 并上传到对应的 GitHub Release。也可对版本标签手动运行工作流。

客户端包包含 RabbitCore、RabbitTools 和 RabbitMine。构建脚本从各模组的最新正式发布中选取与整合包 Minecraft 版本匹配的 NeoForge JAR。
