#!/usr/bin/env python3
"""检查中文 UI 文案的排版、标点与用词规则。

与具体项目无关：规则来自本 SKILL 的 references/rules.md，日期格式契约来自
assets/format-time.ts。项目专有的命名禁令从项目自己的 AGENTS.md / CLAUDE.md
中提取，不硬编码在本文件里。

多语言项目只检查简体中文语料；其他语言的排版惯例不同，自动跳过。

脚本只报告，不改文件。

用法：
    python3 check_copy.py <path> [<path> ...] [--json] [--rule ID] [--severity error]
    python3 check_copy.py <path> --list-bans        # 只列出从 AGENTS.md 提取到的禁用词
    python3 check_copy.py <path> --agents-md <file> # 指定命名禁令来源，可重复
    python3 check_copy.py <path> --no-agents-md     # 不扫描命名禁令
    python3 check_copy.py --list-rules              # 列出全部规则与级别
    python3 check_copy.py <path> --skip-rule ID     # 停用某条规则，可重复
    python3 check_copy.py <path> --ban TERM         # 追加禁用词，可重复
    python3 check_copy.py <path> --skip-ban TERM    # 排除某个禁用词，可重复
    python3 check_copy.py --self-check
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

CJK = r"一-鿿"

SCAN_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".json", ".vue", ".svelte"}
SKIP_DIR_NAMES = {"node_modules", "dist", "build", ".git", "coverage", "__pycache__"}

ERROR = "error"
WARN = "warn"

AGENTS_FILENAMES = ("AGENTS.md", "CLAUDE.md", "AGENTS.design.md")


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    severity: str
    message: str
    text: str
    excerpt: str


# ---------------------------------------------------------------------------
# 多语言项目：只检查简体中文语料
# ---------------------------------------------------------------------------

I18N_MARKERS = ("i18n", "locale", "locales", "lang", "langs", "translation", "translations", "messages")
SIMPLIFIED_ZH = {"zh", "zh-cn", "zh_cn", "zh-hans", "zh_hans", "zh-hans-cn", "cn", "chs", "zh-chs"}
KNOWN_LANGS = {
    "en", "ja", "ko", "fr", "de", "es", "ru", "pt", "it", "vi", "th", "ar", "id", "tr",
    "nl", "pl", "sv", "da", "fi", "nb", "no", "cs", "el", "he", "hi", "hu", "ro", "sk",
    "uk", "ms", "fa", "bn", "ta", "zh",
}
LOCALE_TOKEN = re.compile(r"^([a-z]{2})(?:[-_]([A-Za-z]{2,4}))?(?:[-_]([A-Za-z]{2,4}))?$")


def locale_of(token: str) -> str | None:
    """把路径片段解析成规范化 locale；不是 locale 时返回 None。"""
    match = LOCALE_TOKEN.match(token)
    if not match or match.group(1) not in KNOWN_LANGS:
        return None
    return token.lower().replace("_", "-")


def skip_for_locale(path: Path) -> bool:
    """多语言项目中，只保留简体中文语料。"""
    parts = list(path.parts[:-1]) + [path.stem]
    lowered = [p.lower() for p in parts]
    if not any(marker in lowered for marker in I18N_MARKERS):
        return False
    for part in parts:
        locale = locale_of(part)
        if locale is None:
            continue
        # 繁体与其他语言的标点、空格惯例不同，交给各自的规范。
        return locale not in SIMPLIFIED_ZH
    return False


# ---------------------------------------------------------------------------
# 语料提取：只取「像文案」的片段，即含中日韩字符的字符串字面量与标记文本
# ---------------------------------------------------------------------------

STRING_LITERAL = re.compile(
    r"'((?:[^'\\\n]|\\.)*)'"
    r"|\"((?:[^\"\\\n]|\\.)*)\""
    r"|`((?:[^`\\]|\\.)*)`",
    re.DOTALL,
)
MARKUP_TEXT = re.compile(r">([^<>{}]*[" + CJK + r"][^<>{}]*)<")
HAS_CJK = re.compile(r"[" + CJK + r"]")
LINE_COMMENT = re.compile(r"^\s*(//|\*|/\*|#)")
LOG_CALL = re.compile(r"(?:console|logger|log)\.\w+\(\s*$")
# 字符串前面的属性名决定它的角色，句末标点等规则按角色判定。
ROLE = re.compile(
    r"\b(label|name|title|message|confirmText|cancelText|actionLabel|placeholder"
    r"|aria-label|ariaLabel|description|tooltip|heading|caption)"
    r"\s*[:=]\s*\{?\s*$"
)

REFERENCES = Path(__file__).resolve().parent.parent / "references"


def load_csv_column(name: str, column: int = 0) -> list[str]:
    """读 references 下的对照表；文件缺失时返回空表，规则自动空转。"""
    path = REFERENCES / name
    if not path.exists():
        return []
    out = []
    for row in csv.reader(path.read_text(encoding="utf-8").splitlines()):
        if len(row) <= column or row[0].lstrip().startswith("#"):
            continue
        value = row[column].strip()
        if value:
            out.append(value)
    return out


# 官方写法本身就中英或中数连写的专有名词与单一记号，不受空格规则约束。
# 维护点是 references/proper-nouns.csv，不在本文件。
PROPER_NOUNS = tuple(load_csv_column("proper-nouns.csv"))

MASK_PATTERNS = [
    re.compile(r"\{\{[^}]*\}\}"),          # i18next {{name}}
    re.compile(r"\$\{[^}]*\}"),            # 模板插值
    re.compile(r"\{[A-Za-z_$][\w.$]*\}"),  # JSX / Vue 插值
    re.compile(r"\\[nrt]"),                # 转义
    re.compile(r"https?://\S+"),
    *([re.compile("|".join(re.escape(n) for n in PROPER_NOUNS))] if PROPER_NOUNS else []),
    # 文件名是业务内容而非文案，用户本来就会把中英数字连写：GMV看板.xlsx、会议录音.mp3
    re.compile(r"[^\s，。！？；：、「」（）]+\.(?=[A-Za-z])[A-Za-z0-9]{1,5}(?=$|[\s，。！？；：、「」（）])"),
]

# 内嵌的脚本片段（fixture 里的 PowerShell / JS）不是文案。
CODE_SNIPPET = re.compile(r"!==|===|=>|&&|\|\||\$\w|-eq |Where-Object|function\s*\(")
# 逗号分隔的数据行（CSV fixture）不是文案。
DATA_ROW = re.compile(r"^[^，。！？；：]*?(?:,[^，。！？；：]*){3,}$")


def mask(text: str) -> str:
    """把插值、URL、文件名与专有名词换成等长占位，保留下标以便定位。"""
    out = text
    for pattern in MASK_PATTERNS:
        out = pattern.sub(lambda m: "\x00" * len(m.group(0)), out)
    return out


def extract(path: Path) -> list[tuple[int, str, str]]:
    """返回 (行号, 文案片段, 属性角色) 列表；无角色时角色为空串。"""
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    # 整行注释里的反引号会被误读成模板字符串，先按行抹平（保留行数）。
    source = "\n".join("" if LINE_COMMENT.match(line) else line for line in source.split("\n"))

    results: list[tuple[int, str, str]] = []
    for match in STRING_LITERAL.finditer(source):
        raw = next(g for g in match.groups() if g is not None)
        if not HAS_CJK.search(raw):
            continue
        # 日志不是用户可见文案。
        if LOG_CALL.search(source[max(0, match.start() - 40) : match.start()]):
            continue
        line = source.count("\n", 0, match.start()) + 1
        role_match = ROLE.search(source[max(0, match.start() - 60) : match.start()])
        results.append((line, raw, role_match.group(1) if role_match else ""))

    for match in MARKUP_TEXT.finditer(source):
        raw = match.group(1)
        if not raw.strip():
            continue
        line = source.count("\n", 0, match.start()) + 1
        results.append((line, raw, ""))

    return results


# ---------------------------------------------------------------------------
# 项目命名禁令：从 AGENTS.md / CLAUDE.md 提取，不硬编码
# ---------------------------------------------------------------------------

BAN_SENTENCE = re.compile(
    r"(?:不允许|不得|禁止|不要|严禁|避免)"
    r"[^。；\n]{0,24}?"
    r"(?:出现|使用|使用到|写成|写作|引入|沿用|用)"
    r"\s*"
    r"(?:[「『\"“']\s*(?P<quoted>[^」』\"”'\n]{1,32}?)\s*[」』\"”']"
    r"|(?P<bare>[A-Za-z][A-Za-z0-9_.+-]{1,31}))"
)
# 这些词是规则本身的措辞，不是被禁的命名。
# 与 term.lower() 比较，故全部小写。这些是代码约束或规则措辞，不是文案命名禁令。
BAN_STOPWORDS = {
    "lorem", "ipsum", "console", "log", "any", "todo", "fixme", "http", "https",
    "usecontext", "useeffect", "usecallback", "usememo", "then", "catch", "var",
    "promise", "axios", "fetch", "important", "eslint", "git", "npm",
}


def find_agents_files(paths: list[Path]) -> list[Path]:
    """从被扫描路径向上找 AGENTS.md / CLAUDE.md，直到文件系统根。"""
    found: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        node = path.resolve()
        if node.is_file():
            node = node.parent
        while True:
            for filename in AGENTS_FILENAMES:
                candidate = node / filename
                if candidate.is_file() and candidate not in seen:
                    seen.add(candidate)
                    found.append(candidate)
            if node.parent == node:
                break
            node = node.parent
    return found


# 禁令的适用面：约束代码标识符，还是约束用户可见文案。
# 「工程代码里不允许出现 X」管的是变量与文件名，不该拿来判界面文案。
CODE_SCOPE = re.compile(
    r"工程代码|代码里|代码中|源码|标识符|变量名?|函数名?|类名|类型名|枚举"
    r"|接口名?|字段名|文件名|目录名|包名|模块名|命名空间|import|className|CSS"
)
COPY_SCOPE = re.compile(r"文案|界面|UI|用户可见|展示|提示语?|措辞|称呼|标题|按钮|文字|文本")


def ban_scope(line: str) -> str:
    """禁令作用于代码还是文案。两种信号都在或都不在时，按文案处理。"""
    if CODE_SCOPE.search(line) and not COPY_SCOPE.search(line):
        return "code"
    return "copy"


def extract_bans(files: list[Path]) -> tuple[dict[str, str], dict[str, str]]:
    """返回 ({文案禁用词: 出处}, {代码命名禁令: 出处})。后者默认不参与扫描。"""
    bans: dict[str, str] = {}
    code_only: dict[str, str] = {}
    for file in files:
        try:
            text = file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for match in BAN_SENTENCE.finditer(text):
            term = (match.group("quoted") or match.group("bare") or "").strip()
            if not term or term.lower() in BAN_STOPWORDS:
                continue
            # 纯中文的禁令往往是「禁止使用炒作话术」这类范畴描述，不是命名。
            if not re.search(r"[A-Za-z]", term) and len(term) > 6:
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            start = text.rfind("\n", 0, match.start()) + 1
            end = text.find("\n", match.end())
            line = text[start : end if end != -1 else len(text)]
            target = code_only if ban_scope(line) == "code" else bans
            target.setdefault(term, f"{file}:{line_no}")
    return bans, code_only


# ---------------------------------------------------------------------------
# 规则
# ---------------------------------------------------------------------------

# 不受「数字↔中文加空格」约束的结构：时间点日期、周期日期、时钟、版本号。
# 契约见 assets/format-time.ts。
DATE_LIKE = re.compile(
    r"\d{4}[/-]\d{2}[/-]\d{2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?"
    r"|\d{1,2}[/-]\d{1,2}(?: \d{1,2}:\d{2})?"
    r"|\d{1,2}:\d{2}(?::\d{2})?"
    r"|v?\d+(?:\.\d+)+"
)

RULES: list[dict] = []


def rule(rid: str, severity: str, message: str, fix: str = "", needs_role: bool = False):
    def decorate(fn):
        RULES.append(
            {"id": rid, "severity": severity, "message": message, "fix": fix,
             "fn": fn, "needs_role": needs_role}
        )
        return fn

    return decorate


# --- A 混排空格 ---


@rule(
    "space-cjk-latin",
    ERROR,
    "中文与拉丁字母之间保留一个半角空格",
    "Stream不可用 → Stream 不可用",
)
def _space_cjk_latin(text: str):
    for m in re.finditer(r"[" + CJK + r"][A-Za-z]|[A-Za-z][" + CJK + r"]", text):
        yield m.start(), m.group(0)


@rule(
    "space-cjk-digit",
    ERROR,
    "中文与阿拉伯数字之间保留一个半角空格（日期、时钟、版本号内部除外）",
    "最多选择50个文件 → 最多选择 50 个文件",
)
def _space_cjk_digit(text: str):
    masked = DATE_LIKE.sub(lambda m: "\x00" * len(m.group(0)), text)
    for m in re.finditer(r"[" + CJK + r"]\d|\d[" + CJK + r"]", masked):
        yield m.start(), text[m.start() : m.end()]


@rule("space-before-cjk-punct", ERROR, "全角标点前后不留空格", "由 Agent ，执行 → 由 Agent，执行")
def _space_before_cjk_punct(text: str):
    for m in re.finditer(r" [" + re.escape("，。！？；：、）」》】") + r"]", text):
        yield m.start(), m.group(0)


@rule(
    "file-size-unit-spacing",
    ERROR,
    "文件大小的数字与 B / KB / MB / GB / TB 之间保留一个半角空格",
    "1.44KB → 1.44 KB",
)
def _file_size_unit_spacing(text: str):
    for m in re.finditer(r"(?<![A-Za-z0-9])\d+(?:\.\d+)?(?:B|KB|MB|GB|TB)\b", text):
        yield m.start(), m.group(0)


# --- B 分隔符 ---


@rule(
    "middot-spacing",
    ERROR,
    "分隔符写作 ' · '，前后各一个半角空格",
    "正在执行「摘要」· 张三 → 正在执行「摘要」 · 张三",
)
def _middot_spacing(text: str):
    for m in re.finditer(r".?·.?", text):
        chunk = m.group(0)
        if chunk == "·":  # 整串只有一个点，通常是 CSS 控制间距的独立节点
            continue
        before = chunk[0] if not chunk.startswith("·") else ""
        after = chunk[-1] if not chunk.endswith("·") else ""
        if before == " " and after == " ":
            continue
        # 音译人名：两侧都是中文且都没有空格。
        if before and after and re.match(r"[" + CJK + r"]", before) and re.match(r"[" + CJK + r"]", after):
            continue
        yield m.start(), chunk


@rule(
    "middot-dangling",
    ERROR,
    "分隔符 · 只由拼接处写出，不进入单条文案的首尾，也不连续出现",
    "'个文档 ·' → '个文档'，分隔符移到 join(' · ')",
)
def _middot_dangling(text: str):
    stripped = text.strip()
    if stripped.startswith("·") or stripped.endswith("·"):
        yield 0, stripped[:24]
    for m in re.finditer(r"·\s*·", text):
        yield m.start(), m.group(0)


@rule(
    "list-separator",
    ERROR,
    "并列事实之间用 ' · ' 串联",
    "水平内边距 | 垂直内边距 → 水平内边距 · 垂直内边距",
)
def _list_separator(text: str):
    if not HAS_CJK.search(text):
        return
    for m in re.finditer(r" \| | — |・|•", text):
        yield m.start(), m.group(0)


# --- C 标点 ---


@rule(
    "fullwidth-punct",
    ERROR,
    "中文句子内使用全角标点",
    ", → ，　. → 。　; → ；　? → ？　: → ：　() → （）　并列 , → 、",
)
def _fullwidth_punct(text: str):
    masked = DATE_LIKE.sub(lambda m: "\x00" * len(m.group(0)), text)
    for m in re.finditer(r"[" + CJK + r"][,;?:]|[,;?][" + CJK + r"]", masked):
        yield m.start(), text[m.start() : m.end()]
    for m in re.finditer(r"[" + CJK + r"]\.(?!\.)|[" + CJK + r"]\(|\)[" + CJK + r"]", masked):
        yield m.start(), text[m.start() : m.end()]


@rule("fullwidth-colon-space", ERROR, "全角冒号后不加空格", "下次运行： 09:00 → 下次运行：09:00")
def _fullwidth_colon_space(text: str):
    for m in re.finditer(r"： ", text):
        yield m.start(), m.group(0)


@rule(
    "ellipsis-three-dots",
    ERROR,
    "省略号固定写作三个半角点 ...，标记会进入下一步交互的动作或进行中的状态；不使用半个省略号 …",
    "新增凭证… → 新增凭证...",
)
def _ellipsis_three_dots(text: str):
    for m in re.finditer(r"…+|。{2,}|\.{4,}", text):
        yield m.start(), m.group(0)


@rule("no-exclamation", ERROR, "界面文案不使用感叹号，用陈述句收尾", "创建成功！ → 已创建")
def _no_exclamation(text: str):
    for m in re.finditer(r"[！!]", text):
        yield m.start(), m.group(0)


@rule(
    "cjk-quote-style",
    ERROR,
    "引用界面对象、状态名或用户输入时用直角引号「」；协议与政策用《》",
    "可在“已归档”中查看 → 可在「已归档」中查看",
)
def _cjk_quote_style(text: str):
    # 只认「短语式引用」这一形态。叙事散文里的长引号对话不在此列；
    # 单引号一律不认——模板字符串里嵌套的 JS 定界符会与之混淆。
    for m in re.finditer(r"“[" + CJK + r"][^”]{0,7}”|\"[" + CJK + r"][^\"]{0,7}\"", text):
        yield m.start(), m.group(0)


# 名词性与动作性文案：标签、名称、标题、按钮。任何长度都不加句号。
NOMINAL_ROLES = {"label", "name", "title", "message", "confirmText", "cancelText",
                 "actionLabel", "heading", "caption"}
# 停顿数决定说明性文案是否成句。顿号是并列，不算停顿。
CLAUSE_PAUSE = re.compile(r"[，；,;]")
# 片段、疑问句与被插值截断的串不判「缺句号」。
FRAGMENT_TAIL = ("？", "！", "?", "!", ".", "…", "：", ":", "，", "、", "；",
                 ",", ";", "」", "』", "》", "）", ")", "]", "}", "\x00")


@rule(
    "trailing-period",
    ERROR,
    "短句结尾不加句号；含两处以上停顿的成句说明用 。 收尾；标签、标题与按钮任何长度都不加",
    'title="没有需要配置的连接器。" → 去掉句号；'
    'description="归档后只读，历史仍保留，可随时恢复" → 补 。',
    needs_role=True,
)
def _trailing_period(text: str, role: str):
    # 只判名词性与动作性文案。说明性文案的成句与否需要读语义，留给人工复核。
    if role not in NOMINAL_ROLES:
        return
    stripped = text.strip()
    if not HAS_CJK.search(stripped):
        return
    if stripped.endswith("。"):
        if len(CLAUSE_PAUSE.findall(stripped[:-1])) <= 1:
            yield len(stripped) - 1, stripped[-24:]
        return
    # 疑问式标题（取消这次运行？）是确认弹窗的既有句式，不判。
    if stripped.endswith(FRAGMENT_TAIL):
        return
    if len(CLAUSE_PAUSE.findall(stripped)) >= 2:
        yield len(stripped) - 1, stripped[-24:]


# --- D 日期与时间，契约见 assets/format-time.ts ---


@rule(
    "date-format",
    ERROR,
    "时间点日期写作 YYYY/MM/DD（同年省略为 MM/DD），时钟写作 24 小时制 HH:mm",
    "2026年7月31日 / 2026-07-31 → 2026/07/31",
)
def _date_format(text: str):
    for m in re.finditer(
        r"\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日|\d{4}[.-]\d{1,2}[.-]\d{1,2}", text
    ):
        yield m.start(), m.group(0)


@rule(
    "empty-value-em-dash",
    ERROR,
    "字段值缺失时显示全角破折号 —",
    "value={x ?? 'N/A'} → value={x ?? '—'}",
)
def _empty_value_em_dash(text: str):
    for m in re.finditer(r"^(?:N/A|--|-|无|空|null)$", text.strip()):
        yield 0, m.group(0)


# --- E 用词 ---


def load_name_cases(path: Path = REFERENCES / "name-casing.csv") -> dict[str, str]:
    """错误写法 → 官方写法。表的维护点是 references/name-casing.csv，不在本文件。"""
    cases: dict[str, str] = {}
    if not path.exists():
        return cases
    for row in csv.reader(path.read_text(encoding="utf-8").splitlines()):
        if len(row) < 2 or row[0].lstrip().startswith("#"):
            continue
        correct = row[0].strip()
        for wrong in row[1].split("|"):
            wrong = wrong.strip()
            if wrong and wrong != correct:
                cases[wrong] = correct
    return cases


NAME_CASE = load_name_cases()


@rule("name-casing", ERROR, "品牌与产品实体名使用官方写法（表见 references/name-casing.csv）", "Github → GitHub")
def _name_casing(text: str):
    for wrong, right in NAME_CASE.items():
        for m in re.finditer(r"\b" + re.escape(wrong) + r"\b", text):
            yield m.start(), f"{m.group(0)} → {right}"


@rule(
    "anthropomorphism",
    WARN,
    "用可验证的系统行为描述代替 AI 拟人化",
    "我帮你整理好了 → 已生成整理结果",
)
def _anthropomorphism(text: str):
    for m in re.finditer(r"我帮你|我来帮|我会帮|小助手|智能助手|我猜|我认为|我觉得|让我来|为您|助您", text):
        yield m.start(), m.group(0)


@rule(
    "personal-pronoun",
    ERROR,
    "第二人称用「你」，不用敬语与复数称谓（「我们」「它」由人工复核判定）",
    "请您先完成授权 → 先完成授权",
)
def _personal_pronoun(text: str):
    for m in re.finditer(r"您们|您|咱们|咱", text):
        yield m.start(), m.group(0)


@rule(
    "placeholder-qing-prefix",
    ERROR,
    "输入框 placeholder 用裸动词短语，「请输入 X」只用于校验错误提示",
    "请输入项目名称 → 输入项目名称",
    needs_role=True,
)
def _placeholder_qing(text: str, role: str):
    if role != "placeholder":
        return
    if text.strip().startswith("请"):
        yield 0, text.strip()[:24]


# 项目命名禁令由 --agents-md 动态注入，见 install_ban_rule()。
def resolve_bans(
    files: list[Path], extra: list[str] | None, skipped: list[str] | None
) -> tuple[dict[str, str], dict[str, str]]:
    """提取命名禁令，再应用用户的逐条增删。返回 (生效的, 按代码约束跳过的)。"""
    bans, code_only = extract_bans(files)
    for term in extra or []:
        # --ban 是用户的显式决定，可以把代码约束提回文案禁令。
        bans.setdefault(term, code_only.pop(term, "命令行 --ban"))
    for term in skipped or []:
        bans.pop(term, None)
    return bans, code_only


def install_ban_rule(bans: dict[str, str]) -> None:
    if not bans:
        return
    # 拉丁词大小写不敏感：AGENTS.md 写 SOIA，语料里可能写成 Soia / soia。
    latin = [t for t in bans if re.match(r"[A-Za-z]", t)]
    other = [t for t in bans if t not in latin]
    parts = [r"(?i:\b" + re.escape(t) + r"\b)" for t in latin] + [re.escape(t) for t in other]
    pattern = re.compile("|".join(parts))
    sources = "；".join(f"{t}（{src}）" for t, src in list(bans.items())[:6])

    @rule(
        "banned-term",
        ERROR,
        f"命中项目 AGENTS.md 的命名禁令：{sources}",
        "改用项目当前的正式命名",
    )
    def _banned_term(text: str):
        for m in pattern.finditer(text):
            yield m.start(), m.group(0)


# ---------------------------------------------------------------------------
# 执行
# ---------------------------------------------------------------------------


def check_text(text: str, role: str = "") -> list[tuple[str, str, str, str, int]]:
    """返回 (rule_id, severity, message, matched, offset)。"""
    masked = mask(text)
    if DATA_ROW.match(masked.strip()) or CODE_SNIPPET.search(masked):
        return []
    out = []
    for spec in RULES:
        args = (masked, role) if spec["needs_role"] else (masked,)
        for offset, matched in spec["fn"](*args):
            if "\x00" in str(matched):
                continue
            out.append((spec["id"], spec["severity"], spec["message"], matched, offset))
    # 首尾悬挂的 · 已由 middot-dangling 报出，不再重复报 spacing。
    if any(r == "middot-dangling" for r, *_ in out):
        out = [item for item in out if item[0] != "middot-spacing"]
    return out


def iter_files(paths: list[Path]):
    for path in paths:
        if path.is_file():
            if not skip_for_locale(path):
                yield path
            continue
        for child in path.rglob("*"):
            if not child.is_file() or child.suffix not in SCAN_SUFFIXES:
                continue
            if SKIP_DIR_NAMES & set(child.parts):
                continue
            if skip_for_locale(child):
                continue
            yield child


def excerpt(text: str, offset: int, width: int = 28) -> str:
    start = max(0, offset - width // 2)
    return text[start : start + width].replace("\n", " ")


def run(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(paths):
        for line, text, role in extract(path):
            for rid, severity, message, matched, offset in check_text(text, role):
                findings.append(
                    Finding(str(path), line, rid, severity, message, str(matched),
                            excerpt(text, offset))
                )
    findings.sort(key=lambda f: (f.severity != ERROR, f.rule, f.file, f.line))
    return findings


SELF_CHECK_CASES = [
    # (文案, 角色, 规则, 是否应命中)
    ("Stream不可用", "", "space-cjk-latin", True),
    ("Stream 不可用", "", "space-cjk-latin", False),
    ("GMV看板.xlsx", "", "space-cjk-latin", False),
    ("会议录音.mp3", "", "fullwidth-punct", False),
    ("数据备份.bin", "", "fullwidth-punct", False),
    ("已归档。归档后只读", "", "fullwidth-punct", False),
    ("BOSS直聘", "", "space-cjk-latin", False),
    ("最多选择50个文件", "", "space-cjk-digit", True),
    ("最多选择 50 个文件", "", "space-cjk-digit", False),
    ("30天内", "", "space-cjk-digit", True),
    ("更新于 2026/07/31 14:30", "", "space-cjk-digit", False),
    ("共 {{count}} 个文件", "", "space-cjk-digit", False),
    ("成功 · 8 分钟前 · 生成价格异常表", "", "middot-spacing", False),
    ("正在执行「摘要」· 张三", "", "middot-spacing", True),
    ("克里斯朵夫·李维", "", "middot-spacing", False),
    ("个文档 ·", "", "middot-dangling", True),
    ("成功 · 8 分钟前", "", "middot-dangling", False),
    ("水平内边距 | 垂直内边距", "", "list-separator", True),
    ("成功 · 8 分钟前", "", "list-separator", False),
    ("$page = $r | Where-Object { $_ -eq 'page' }", "", "list-separator", False),
    ("已归档,不再触发", "", "fullwidth-punct", True),
    ("已归档，不再触发", "", "fullwidth-punct", False),
    ("2026-07-15,搜索,12840,318,2864", "", "fullwidth-punct", False),
    ("下次运行： 明天 09:00", "", "fullwidth-colon-space", True),
    ("下次运行：明天 09:00", "", "fullwidth-colon-space", False),
    ("新增凭证...", "", "ellipsis-three-dots", False),
    ("加载中...", "", "ellipsis-three-dots", False),
    ("加载中…", "", "ellipsis-three-dots", True),
    ("新增凭证…", "", "ellipsis-three-dots", True),
    ("任务规划中。。。", "", "ellipsis-three-dots", True),
    ("创建成功！", "", "no-exclamation", True),
    ("已创建", "", "no-exclamation", False),
    ("self.__next_f!=='undefined'", "", "no-exclamation", False),
    ("可在“已归档”中查看", "", "cjk-quote-style", True),
    ("可在「已归档」中查看", "", "cjk-quote-style", False),
    ("依据《隐私政策》处理", "", "cjk-quote-style", False),
    ('当用户提到"约会议"时', "", "cjk-quote-style", True),
    ("没有需要重新配置的连接器。", "title", "trailing-period", True),
    ("取消这次运行？", "title", "trailing-period", False),
    ("归档后项目只读，历史记录与文件仍会保留，可随时恢复。", "message", "trailing-period", False),
    ("归档后项目只读，历史记录与文件仍会保留，可随时恢复", "message", "trailing-period", True),
    ("归档后项目只读，历史记录仍会保留", "message", "trailing-period", False),
    ("支持 PDF、Word、Excel 三种格式", "label", "trailing-period", False),
    ("已归档的知识库仅可浏览与下载。", "description", "trailing-period", False),
    ("共 {{count}} 个文件，", "", "trailing-period", False),
    ("请您先完成授权", "", "personal-pronoun", True),
    ("咱们再试一次", "", "personal-pronoun", True),
    ("由你确认", "", "personal-pronoun", False),
    ("我的文件", "", "personal-pronoun", False),
    ("2026年7月31日提交", "", "date-format", True),
    ("2026-07-31 提交", "", "date-format", True),
    ("2026/07/31 提交", "", "date-format", False),
    ("N/A", "", "empty-value-em-dash", True),
    ("—", "", "empty-value-em-dash", False),
    ("绑定 Github 账号", "", "name-casing", True),
    ("绑定 GitHub 账号", "", "name-casing", False),
    ("我来帮你收集资源", "", "anthropomorphism", True),
    ("正在收集资源", "", "anthropomorphism", False),
    ("请输入项目名称", "placeholder", "placeholder-qing-prefix", True),
    ("输入项目名称", "placeholder", "placeholder-qing-prefix", False),
    ("请先完成授权", "message", "placeholder-qing-prefix", False),
    ("由 Agent ，执行", "", "space-before-cjk-punct", True),
    ("文件大小：1.44KB", "", "file-size-unit-spacing", True),
    ("文件大小：1.44 KB", "", "file-size-unit-spacing", False),
    ("文件名 100MB", "", "file-size-unit-spacing", False),
]


def self_check() -> int:
    failures = []
    for text, role, rid, should_hit in SELF_CHECK_CASES:
        hits = {r for r, *_ in check_text(text, role)}
        if (rid in hits) is not should_hit:
            failures.append(
                f"{text!r} [{role or '-'}]: 期望 {rid} {'命中' if should_hit else '不命中'}，实际 {sorted(hits)}"
            )

    # locale 过滤
    locale_cases = [
        ("src/i18n/locales/zh-Hans/a.ts", False),
        ("src/i18n/locales/en/a.ts", True),
        ("src/i18n/locales/ja/a.ts", True),
        ("src/i18n/locales/zh-Hant/a.ts", True),
        ("src/locales/zh-CN.json", False),
        ("src/locales/en.json", True),
        ("src/pages/design/en-route/a.ts", False),  # 非 i18n 路径不做 locale 过滤
        ("src/components/Button.tsx", False),
    ]
    for raw, expected in locale_cases:
        actual = skip_for_locale(Path(raw))
        if actual is not expected:
            failures.append(f"locale 过滤 {raw}: 期望 skip={expected}，实际 {actual}")

    # 命名禁令提取
    sample = (
        "# AGENTS\n"
        "- **命名**：工程代码里除非明确指明不允许出现SOIA\n"
        "- 界面文案中不允许出现「小助手」\n"
        "- 禁止使用「智能助手」这类泛化称呼\n"
        "- 禁止擅自使用 useContext\n"
        "- 不要使用炒作话术\n"
    )
    tmp = Path("/tmp/_awr_agents_sample.md")
    tmp.write_text(sample, encoding="utf-8")
    bans, code_only = extract_bans([tmp])
    tmp.unlink(missing_ok=True)
    if "SOIA" in bans:
        failures.append("命名禁令提取：SOIA 只约束工程代码命名，不应作为文案禁用词")
    if "SOIA" not in code_only:
        failures.append(f"命名禁令提取：SOIA 应作为代码命名禁令单独列出，实际 {sorted(code_only)}")
    if "小助手" not in bans:
        failures.append(f"命名禁令提取：写明「界面文案」的禁令应生效，实际 {sorted(bans)}")
    if "智能助手" not in bans:
        failures.append(f"命名禁令提取：应捕获「智能助手」，实际 {sorted(bans)}")
    if "useContext" in bans:
        failures.append("命名禁令提取：useContext 是代码约束，不应作为文案禁用词")
    if any("炒作" in b for b in bans):
        failures.append(f"命名禁令提取：范畴描述不应被当成命名，实际 {sorted(bans)}")
    # --ban 能把代码约束显式提回文案禁令
    tmp.write_text(sample, encoding="utf-8")
    forced, _ = resolve_bans([tmp], ["SOIA"], None)
    tmp.unlink(missing_ok=True)
    if "SOIA" not in forced:
        failures.append("--ban SOIA 应能把代码命名禁令提回文案禁用词")

    total = len(SELF_CHECK_CASES) + len(locale_cases) + 7
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"self-check: {total - len(failures)}/{total} 通过")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查中文 UI 文案的排版、标点与用词规则")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--rule", action="append", help="只跑指定规则，可重复")
    parser.add_argument("--skip-rule", action="append", default=[],
                        help="停用指定规则，可重复；用于用户选择性执行")
    parser.add_argument("--list-rules", action="store_true", help="只列出全部规则与级别")
    parser.add_argument("--severity", choices=[ERROR, WARN], help="只报告该级别")
    parser.add_argument("--agents-md", action="append", type=Path,
                        help="命名禁令来源，可重复；默认从被扫描路径向上自动查找")
    parser.add_argument("--no-agents-md", action="store_true", help="不扫描命名禁令")
    parser.add_argument("--ban", action="append", default=[], help="追加禁用词，可重复")
    parser.add_argument("--skip-ban", action="append", default=[], help="排除某个禁用词，可重复")
    parser.add_argument("--list-bans", action="store_true", help="只列出提取到的命名禁令")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        return self_check()
    if args.list_rules:
        print(f"共 {len(RULES)} 条机械规则（banned-term 在有命名禁令时动态启用）：")
        for spec in RULES:
            print(f"  [{spec['severity']:5}] {spec['id']:24} {spec['message']}")
        return 0
    if not args.paths:
        parser.error("需要至少一个路径，或使用 --self-check")

    bans: dict[str, str] = {}
    if not args.no_agents_md:
        files = args.agents_md if args.agents_md else find_agents_files(args.paths)
        bans, code_only = resolve_bans(files, args.ban, args.skip_ban)
        install_ban_rule(bans)

    if args.list_bans:
        if bans:
            print(f"提取到 {len(bans)} 条文案禁用词：")
            for term, source in bans.items():
                print(f"  {term}    ← {source}")
        else:
            print("未从 AGENTS.md / CLAUDE.md 提取到文案禁用词。")
        if code_only:
            print(f"\n另有 {len(code_only)} 条只约束代码命名，已跳过（需要时用 --ban 加回）：")
            for term, source in code_only.items():
                print(f"  {term}    ← {source}")
        return 0

    if args.skip_rule:
        skipped = set(args.skip_rule)
        RULES[:] = [spec for spec in RULES if spec["id"] not in skipped]

    findings = run(args.paths)
    if args.rule:
        findings = [f for f in findings if f.rule in set(args.rule)]
    if args.severity:
        findings = [f for f in findings if f.severity == args.severity]

    if args.json:
        print(json.dumps([f.__dict__ for f in findings], ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f"{f.file}:{f.line}  [{f.severity}] {f.rule}")
            print(f"    {f.message}")
            print(f"    命中：{f.text}    上下文：…{f.excerpt}…")
        errors = sum(1 for f in findings if f.severity == ERROR)
        print(f"\n共 {len(findings)} 条（error {errors}，warn {len(findings) - errors}）")
        if bans:
            print(f"命名禁令已加载 {len(bans)} 条，用 --list-bans 查看")
        if args.skip_rule:
            print(f"已按用户选择停用规则：{'、'.join(args.skip_rule)}")

    return 1 if any(f.severity == ERROR for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
