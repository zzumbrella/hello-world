# 读懂皇艺：英国皇家艺术学院（RCA）专业解读手册

写给零基础中国申请者的 RCA 专业解读书（2027/28 入学版）。当前是样书，成品在 `output/读懂皇艺-样书.pdf`。

## 样书包括什么

- 封面、使用说明、全书目录、前言
- 第一部分「零基础先补四课」全文：
  - RCA 是一所什么样的学校
  - 当代艺术和设计在关心什么问题
  - 他们怎么看问题
  - RCA 高频词速查
- 第二部分：
  - 三个学院总览
  - 两章样章：摄影 MA（以 Yang Zou 为主案例）、信息体验设计 MA
- 附录：来源总表

其余 27 个专业和第三部分「申请实操」只列在目录里，标「正式版收录」。

## 出处怎么保证

书里每一条事实都标了编号出处：

- 每章末尾有「本章出处」，书末有「来源总表」。
- 官网页面、课程规格书 PDF、毕业展页面和外部资料，都在 2026-10-18 读取，原始文件存在 `archive/`。
- 系主任的话出自官网开放日录像，引用时标出时间点，例如「4·31:08」表示第 4 条来源的第 31 分 08 秒。字幕原文存在 `archive/vimeo/`。

## 目录结构

| 路径 | 内容 |
|---|---|
| `content/` | 各章正文（HTML 加简单的简写标记，写法见 `scripts/build.py` 开头的说明） |
| `data/sources.json` | 全部来源：网址、标题、读取日期、存档位置 |
| `data/programmes.json` | 从 31 个专业页抓取的事实：学制、学费、截止日期、校区等 |
| `data/images.json`、`data/covers.json` | 官网图片和书封的来源与说明 |
| `archive/` | 被引用网页、PDF 和视频字幕的原始存档 |
| `assets/` | 书中用到的图片、书封和二维码 |
| `scripts/` | 抓取、存档和排版脚本 |
| `styles/book.css` | 排版样式（A4，正文加侧栏旁注） |

## 重新生成 PDF

```bash
python3 -m venv ~/.venvs/rca && ~/.venvs/rca/bin/pip install -r requirements.txt
scripts/setup_fonts.sh                      # 思源宋体/黑体（Noto CJK SC，转成 TrueType）和拉丁字体
~/.venvs/rca/bin/python -I scripts/build.py # 输出 output/读懂皇艺-样书.pdf
```

完整生成大约需要一分钟。中文字体要先转成 TrueType 格式（`setup_fonts.sh` 会自动处理）。否则在 MuPDF 内核的阅读器里（很多手机 App 都用它）中文会显示不出来。如果有旁注卡片被分在两页，`build.py` 会自动把它移到下一页，再重新排版。

## 更新官网信息

需要时按以下顺序重新抓取：

1. `fetch_programmes.py`
2. `fetch_sources.py`
3. `fetch_images.py`
4. `fetch_covers.py`
5. `fetch_external.py`
6. `gen_lesson4.py`（重新统计高频词）
7. 最后运行 `build.py`

官网是 JavaScript 渲染的，抓取脚本要用无头 Chromium。
