from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets" / "raw"
OUT = ROOT / "assets"

FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


BLUE = "#0969da"
ORANGE = "#f97316"
RED = "#cf222e"
GREEN = "#1a7f37"
PURPLE = "#8250df"
INK = "#1f2328"
MUTED = "#57606a"
PANEL = "#f6f8fa"


def arrow(draw, start, end, color=ORANGE, width=5):
    draw.line([start, end], fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 16
    p1 = (end[0] - length * math.cos(angle - 0.55), end[1] - length * math.sin(angle - 0.55))
    p2 = (end[0] - length * math.cos(angle + 0.55), end[1] - length * math.sin(angle + 0.55))
    draw.polygon([end, p1, p2], fill=color)


def badge(draw, xy, number, color=ORANGE):
    x, y = xy
    r = 22
    draw.ellipse((x-r, y-r, x+r, y+r), fill=color, outline="white", width=4)
    txt = str(number)
    box = draw.textbbox((0, 0), txt, font=font(22, True))
    draw.text((x-(box[2]-box[0])/2, y-(box[3]-box[1])/2-2), txt, fill="white", font=font(22, True))


def callout(draw, rect, number, badge_xy, color=ORANGE):
    draw.rounded_rectangle(rect, radius=10, outline=color, width=5)
    x1, y1, x2, y2 = rect
    target = ((x1+x2)//2, (y1+y2)//2)
    arrow(draw, badge_xy, target, color)
    badge(draw, badge_xy, number, color)


def annotate_repo():
    img = Image.open(RAW / "github-repo.png").convert("RGB")
    d = ImageDraw.Draw(img)
    callout(d, (48, 82, 442, 124), 1, (30, 128), BLUE)
    callout(d, (28, 137, 820, 180), 2, (845, 145), PURPLE)
    callout(d, (108, 202, 220, 244), 3, (70, 245), ORANGE)
    callout(d, (906, 201, 1020, 244), 4, (1050, 226), GREEN)
    img.save(OUT / "01-github-repository.png", quality=95)


def annotate_pr():
    img = Image.open(RAW / "github-pr-open.png").convert("RGB")
    d = ImageDraw.Draw(img)
    callout(d, (110, 204, 470, 250), 1, (80, 218), BLUE)
    callout(d, (106, 248, 680, 292), 2, (716, 260), GREEN)
    callout(d, (108, 302, 667, 346), 3, (705, 325), PURPLE)
    d.rounded_rectangle((1015, 380, 1320, 460), radius=12, fill="#fff8c5", outline="#d4a72c", width=3)
    d.text((1032, 392), "Reviewer、Assignee 等协作信息\n都集中在右栏", fill=INK, font=font(18))
    img.save(OUT / "04-github-pull-request.png", quality=95)


def annotate_conflict():
    img = Image.open(RAW / "github-pr-conflict.png").convert("RGB")
    img = img.crop((0, 0, img.width, min(900, img.height)))
    banner_h = 92
    canvas = Image.new("RGB", (img.width, img.height + banner_h), "white")
    canvas.paste(img, (0, banner_h))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((24, 16, img.width-24, 75), radius=14, fill="#ffebe9", outline=RED, width=3)
    d.text((48, 29), "真实状态：PR #2 的 mergeable=CONFLICTING，main 与练习分支修改了同一行", fill=RED, font=font(24, True))
    callout(d, (106, 285, 508, 335), 1, (72, 310), RED)
    callout(d, (104, 383, 640, 427), 2, (680, 405), PURPLE)
    canvas.save(OUT / "06-github-conflict.png", quality=95)


def base_vscode(title, branch="main"):
    img = Image.new("RGB", (1440, 900), "#1e1e1e")
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1440, 35), fill="#181818")
    d.text((16, 8), "文件   编辑   选择   查看   转到   运行   终端   帮助", fill="#cccccc", font=font(15))
    d.text((560, 7), title, fill="#dddddd", font=font(15))
    d.rectangle((0, 35, 48, 876), fill="#181818")
    icons = ["▣", "⑂", "⌕", "▷", "□"]
    for i, t in enumerate(icons):
        d.text((13, 58+i*54), t, fill="#bcbcbc", font=font(24, True))
    d.rectangle((0, 876, 1440, 900), fill="#007acc")
    d.text((18, 879), f"⎇  {branch}", fill="white", font=font(14, True))
    d.text((1250, 879), "UTF-8   LF   Markdown", fill="white", font=font(13))
    return img, d


def vscode_overview():
    img, d = base_vscode("github-collaboration-practice - Visual Studio Code")
    d.rectangle((48, 35, 300, 876), fill="#252526")
    d.text((66, 52), "资源管理器", fill="#cccccc", font=font(15, True))
    d.text((66, 88), "GITHUB-COLLABORATION-PRACTICE", fill="#cccccc", font=font(14, True))
    for y, t in [(128, "⌄ assets"), (164, "⌄ practice"), (200, "    生存指南素材.md"), (236, "  README.md"), (272, "  GitHub协作实操手册.md")]:
        d.text((72, y), t, fill="#d4d4d4", font=font(17))
    d.rectangle((300, 35, 1440, 80), fill="#252526")
    d.text((330, 50), "生存指南素材.md", fill="#ffffff", font=font(16))
    lines = ["# 生存指南素材", "", "## 导师选择", "", "- 选导师前应先了解研究方向、指导方式和课题组氛围。", "", "## 冲突练习句", "", "我计划每周整理一次学习记录。"]
    for i, t in enumerate(lines, 1):
        d.text((328, 95+i*34), str(i), fill="#858585", font=font(16))
        d.text((372, 95+i*34), t, fill="#d4d4d4", font=font(18))
    d.rectangle((0, 0, 1440, 48), outline=ORANGE, width=0)
    d.rounded_rectangle((840, 815, 1410, 860), radius=10, fill="#3a2f08", outline="#d4a72c", width=2)
    d.text((858, 826), "界面结构示意：位置与当前 VS Code 1.136 一致", fill="#ffd33d", font=font(17, True))
    callout(d, (4, 91, 44, 135), 1, (90, 110), PURPLE)
    callout(d, (3, 873, 180, 899), 2, (220, 850), ORANGE)
    img.save(OUT / "02-vscode-overview.png", quality=95)


def vscode_status():
    img, d = base_vscode("源代码管理 - Visual Studio Code", "practice/status-demo")
    d.rectangle((48, 35, 500, 876), fill="#252526")
    d.text((70, 52), "源代码管理", fill="#eeeeee", font=font(18, True))
    d.rounded_rectangle((68, 92, 477, 148), radius=5, fill="#3c3c3c")
    d.text((84, 108), "提交消息（按 Ctrl+Enter 提交）", fill="#aaaaaa", font=font(16))
    d.rounded_rectangle((68, 160, 477, 204), radius=4, fill="#0e639c")
    d.text((246, 170), "提交", fill="white", font=font(17, True))
    d.text((70, 232), "更改", fill="#eeeeee", font=font(17, True))
    rows = [(272, "README.md", "M", "#e2c08d"), (312, "新笔记.md", "U", "#73c991"), (352, "旧文件.md", "D", "#c74e39")]
    for y, name, status, color in rows:
        d.text((88, y), name, fill="#dddddd", font=font(17))
        d.text((446, y), status, fill=color, font=font(17, True))
        d.text((410, y), "+", fill="#dddddd", font=font(19, True))
    d.text((70, 414), "暂存的更改", fill="#eeeeee", font=font(17, True))
    for y, name, status in [(454, "新增条目.md", "A"), (494, "改名后.md", "R")]:
        d.text((88, y), name, fill="#dddddd", font=font(17))
        d.text((446, y), status, fill="#73c991", font=font(17, True))
        d.text((410, y), "−", fill="#dddddd", font=font(19, True))
    d.text((540, 70), "状态字母比颜色更可靠", fill="#ffffff", font=font(28, True))
    explanations = [
        ("U", "Untracked：新文件，Git 从未记录"),
        ("M", "Modified：已有文件被修改"),
        ("A", "Added：新文件已进入暂存区"),
        ("D", "Deleted：文件被删除"),
        ("R", "Renamed：Git 识别为改名"),
        ("UU", "双方都修改：合并冲突"),
    ]
    for i, (key, desc) in enumerate(explanations):
        y = 135 + i*72
        d.rounded_rectangle((550, y, 625, y+45), radius=8, fill="#333333", outline="#666666")
        d.text((570, y+9), key, fill="#4fc1ff", font=font(18, True))
        d.text((650, y+9), desc, fill="#d4d4d4", font=font(19))
    callout(d, (65, 88, 480, 207), 1, (520, 220), BLUE)
    callout(d, (65, 225, 480, 388), 2, (520, 370), ORANGE)
    callout(d, (65, 405, 480, 535), 3, (520, 545), GREEN)
    d.text((565, 826), "结构示意；颜色会随主题变化", fill="#ffd33d", font=font(17, True))
    img.save(OUT / "03-vscode-status.png", quality=95)


def graph_diagram():
    img, d = base_vscode("源代码管理图 - Visual Studio Code", "practice/conflict-demo")
    d.rectangle((48, 35, 420, 876), fill="#252526")
    d.text((70, 58), "源代码管理图", fill="#eeeeee", font=font(20, True))
    commits = [
        (130, 160, "2aa7435", "main / origin/main", "周一制定学习计划", BLUE),
        (260, 270, "7169ffe", "practice/conflict-demo", "周日晚整理学习记录", PURPLE),
        (130, 390, "2175447", "", "Squash merge PR #1", GREEN),
        (130, 510, "7e4f577", "", "初始化练习仓库", ORANGE),
    ]
    d.line([(130, 510), (130, 160)], fill="#4fc1ff", width=5)
    d.line([(130, 390), (260, 270)], fill="#c586c0", width=5)
    for x, y, sha, label, msg, color in commits:
        d.ellipse((x-13, y-13, x+13, y+13), fill=color, outline="white", width=3)
        d.text((x+30, y-24), msg, fill="#eeeeee", font=font(18, True))
        d.text((x+30, y+6), f"{sha}  {label}", fill="#aaaaaa", font=font(15))
    d.text((485, 100), "读图顺序", fill="white", font=font(30, True))
    items = ["① 圆点 = commit", "② 线 = 父子关系", "③ 分叉 = 从共同 commit 建立了分支", "④ 标签 = 分支当前指向的位置", "⑤ 颜色只用于区分线路，没有固定语义"]
    for i, item in enumerate(items):
        d.text((500, 175+i*78), item, fill="#d4d4d4", font=font(21))
    d.text((500, 620), "origin/main 是本地记录的远程 main 位置，\n不是第二个 GitHub 仓库。", fill="#ffd33d", font=font(22, True), spacing=10)
    d.text((500, 810), "结构示意：提交号来自本练习仓库的真实历史", fill="#aaaaaa", font=font(17))
    img.save(OUT / "05-source-control-graph.png", quality=95)


def merge_editor():
    img, d = base_vscode("合并编辑器 - 生存指南素材.md", "practice/conflict-demo")
    d.text((62, 52), "CURRENT（当前分支）", fill="#4fc1ff", font=font(19, True))
    d.text((520, 52), "INCOMING（main）", fill="#c586c0", font=font(19, True))
    d.text((980, 52), "RESULT（最终结果）", fill="#73c991", font=font(19, True))
    boxes = [(52, 92, 470, 360), (510, 92, 928, 360), (968, 92, 1388, 360)]
    for box in boxes:
        d.rounded_rectangle(box, radius=8, fill="#252526", outline="#555555", width=2)
    d.rectangle((70, 155, 450, 225), fill="#16364a")
    d.text((82, 168), "我计划每周日晚整理\n本周的学习记录。", fill="#eeeeee", font=font(19))
    d.rectangle((528, 155, 908, 225), fill="#40284a")
    d.text((540, 168), "我计划每周一早上制定\n本周的学习计划。", fill="#eeeeee", font=font(19))
    d.rectangle((986, 155, 1368, 250), fill="#1d3b28")
    d.text((998, 166), "我计划每周一早上制定计划，\n每周日晚整理本周记录。", fill="#eeeeee", font=font(19))
    d.text((75, 295), "接受当前更改", fill="#4fc1ff", font=font(16))
    d.text((533, 295), "接受传入更改", fill="#c586c0", font=font(16))
    d.text((1000, 295), "手工编辑语义正确的结果", fill="#73c991", font=font(16, True))
    d.rounded_rectangle((90, 430, 1340, 685), radius=12, fill="#252526", outline="#666666", width=2)
    d.text((120, 455), "原始冲突标记（不要把这些符号留进最终文件）", fill="#ffd33d", font=font(22, True))
    conflict = ["<<<<<<< HEAD", "我计划每周日晚整理本周的学习记录。", "=======", "我计划每周一早上制定本周的学习计划。", ">>>>>>> main"]
    colors = ["#4fc1ff", "#d4d4d4", "#ffd33d", "#d4d4d4", "#c586c0"]
    for i, (line, color) in enumerate(zip(conflict, colors)):
        d.text((135, 510+i*33), line, fill=color, font=font(18, i in [0, 2, 4]))
    d.text((100, 800), "结构示意：Current/Incoming 是相对概念；先读内容，再决定 Result。", fill="#ffd33d", font=font(20, True))
    img.save(OUT / "07-vscode-merge-editor.png", quality=95)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    annotate_repo()
    annotate_pr()
    annotate_conflict()
    vscode_overview()
    vscode_status()
    graph_diagram()
    merge_editor()
    print("assets generated")
