# Rabbit World

基于 Minecraft Java 1.21.1 和 NeoForge 21.1.265 的整合包，包含 Minecraft Transit Railway、FTB Quests 和 Rabbit 系列模组。服务端需要 Java 21。

## 项目文件

- `manifest.json` 固定 Minecraft、NeoForge 和 CurseForge 下载项的版本。
- `overrides/config/` 包含整合包配置和 FTB 任务。
- `overrides/kubejs/` 包含 KubeJS 脚本及资源。
- `overrides/mods/` 包含整合包自带的三个 Rabbit JAR。
- `server-excludes.txt` 用 CurseForge 项目 slug 维护服务端应跳过的客户端项目。

仓库只保留整合包所需文件。本地地图缓存、旧任务备份、Numen MCP 连接配置和 BlueMap SQL 连接配置由使用者自行管理。服务端构建会跳过指向客户端存档的 BlueMap 地图定义。

## 安装客户端

从 GitHub Actions 的 **Build Rabbit World** 下载 **Rabbit-World-Client** 构建产物。解开 Actions 外层压缩包，将里面的 `Rabbit-World-Client-1.21.zip` 导入 CurseForge。

也可以用 Python 3.9 或更新版本在本地运行 `python3 scripts/build.py client`，输出到 `dist/`。

## 构建和安装服务端

准备 Python 3.9 或更新版本、Java 21 和 CurseForge API Key。把 Key 设置为当前终端的环境变量 `CURSEFORGE_API_KEY`，然后运行：

```sh
java -version
python3 scripts/build.py server
```

脚本按清单下载服务端模组、合并配置、安装 NeoForge，输出 `dist/Rabbit-World-Server-1.21.zip`。如果 CurseForge 不向 API 提供某个文件，脚本会报告其项目 ID 和文件 ID 并终止。可以通过 CurseForge 客户端安装整合包，然后按同样的排除清单整理模组并手动上传到 NeoForge 服务端。

解压到空服务端目录。Linux 用 `bash run.sh nogui` 启动，Windows 用 `run.bat nogui`。首次启动会生成 `eula.txt`，阅读并接受 EULA 后再次启动。等控制台出现 `Done` 后，用同版客户端进服，检查 FTB 任务和 MTR。

## GitHub Actions

推送到 `main` 或推送 `v*` 标签会构建客户端包。服务端构建可在配置仓库 Secret `CURSEFORGE_API_KEY` 后，从 **Run workflow** 勾选 **Build the dedicated server pack**。公开仓库中的服务端任务用于验证构建，完整 ZIP 可在本地生成。私有仓库的任务会上传服务端构建产物。
