# 更新日志

## 2.2.2

- 更新 RabbitQuest 至 1.0.2。商店目录上限提高到 1 MiB，修复导入建材预设后无法新增分类或保存商品的问题。

- 联机服务器需同步更新 RabbitQuest 至 1.0.2。

## 2.2.1

- 更新 RabbitCore 至 2.3.0，移除 FTB Quests 及旧任务覆盖配置。任务入口改由 RabbitQuest 提供。
- 更新 RabbitQuest 至 1.0.1，加入 197 项初始建材商品，移除旧测试预设入口。
- 新增随 RabbitQuest 正式发布独立提供的个人周常数据包。包含 8 项常驻任务和 3 份轮换工程订单，药剂交付与深暗清剿按配置校验。
- 联机服务器需同步更新 RabbitQuest。个人周常数据包由服务端安装到世界的 `datapacks/`。

## 2.2.0

- 集成 RabbitQuest 1.0.0，加入兔兔任务书、兑换商店、周常与工程订单、限时活动和任务兔子箱。
- 商店支持分类展开、商品搜索和三种兑换券；活动支持并行步骤、前置解锁、点击完成和待领奖励查看。
- 客户端组包从 RabbitQuest 的正式 GitHub Release 下载匹配 Minecraft 1.21.1 的 NeoForge JAR。多人联机需要服务端同时安装 RabbitQuest 并配置对应的任务数据包。

## 2.1.1

- 同步本地 Minecraft 1.21.1 CurseForge 实例中的 71 项依赖。
- 更新 Supplementaries 至 4.1.1、Entity Culling 至 1.12.1、Architectury API 至 13.0.12。
- 加入 Forgematica 0.4.3、MaFgLib 0.4.3 和 Simple Backups 4.0.30，移除 FTB Backups 2。
