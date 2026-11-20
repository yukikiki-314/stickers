# 小猫表情包 GitHub 批量导入包

本包根据你提供的《南南の小猫表情包》PDF整理，包含 76 条图片记录。**这里暂时没有包含图片二进制文件**：当前执行环境无法访问原始图片域名 `serein3cc.cn`，因此没有把无法验证的空文件放进压缩包。

## 文件说明

- `sticker_manifest.csv`：76 张表情包的编号、类别、中文名称、原始地址、预期 jsDelivr 地址。
- `sticker_manifest.json`：同一份索引的 JSON 版本。
- `download_stickers.py`：批量下载器，会检查文件签名，失败项目记录到 `download-report.csv`。
- `.github/workflows/import-stickers.yml`：GitHub Actions 手动工作流，下载成功后自动提交图片到 `emoji/`。

## 放进仓库

目标仓库：`yukikiki-314/stickers`。默认分支按 `main` 配置。请把本包解压后，将 `sticker_manifest.csv`、`download_stickers.py` 放在仓库根目录，并将工作流文件放在：

` .github/workflows/import-stickers.yml `

上传并提交后，打开仓库的 **Actions**，选择 **Import cat stickers**，点击 **Run workflow**。运行完成后：

- 成功的图片会保存到 `emoji/`；
- `emoji/index.csv` 会列出 CDN 地址和下载状态；
- `download-report.csv` 会逐张记录成功或失败原因。

jsDelivr 地址格式为：

`https://cdn.jsdelivr.net/gh/yukikiki-314/stickers@main/emoji/文件名`

如果仓库默认分支不是 `main`，需要同步修改 CSV 中的 CDN 地址。

## 注意

1. 原始图片站目前无法从本次执行环境访问；GitHub Actions 的运行结果才会最终确认每张图片是否仍可下载。
2. 公开仓库会公开图片及其索引。请确认你有权重新托管这些图片，并遵守原作者的使用条件。
3. 工作流只会提交实际下载且通过图片格式签名检查的文件，不会用错误页面冒充图片。
