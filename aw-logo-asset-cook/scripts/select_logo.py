#!/usr/bin/env python3
"""Choose one composition per usage scenario. Standard library only."""
import math
import shutil
import sys
from pathlib import Path

# cook.py replaces this value with the project's explicit scenario configuration.
CONFIG = {}
ROOT = Path(__file__).resolve().parent


def ask_choice(prompt, choices):
    print(prompt)
    for key, (label, _) in choices.items():
        print(f'  {key}. {label}')
    while True:
        answer = input('选择：').strip()
        if answer in choices:
            return choices[answer][1]
        print('请输入列出的编号。')


def ask_size():
    while True:
        try:
            value = float(input('场景典型显示尺寸（逻辑 px，如 24 CSS px）：').strip())
            if math.isfinite(value) and value > 0:
                return value
        except ValueError:
            pass
        print('请输入大于 0 的有限数字。')


def choose_layout(size, scenario='', existing=None):
    if existing:
        return existing
    setting = CONFIG.get('scenarios', {}).get(scenario, {})
    if setting.get('layout'):
        return setting['layout']
    size = setting.get('size', size)
    return 'compact' if size <= CONFIG.get('compact_max_size', 32) else 'spacious'


def select_logo(size, kind, theme, scenario='', existing=None):
    layout = choose_layout(size, scenario, existing)
    available = sorted({p.name.split('-')[1] for p in (ROOT / 'base').glob('logo-*-*-*.svg')})
    if layout not in available and len(available) == 1 and not existing and not CONFIG.get('scenarios', {}).get(scenario, {}).get('layout'):
        layout = available[0]
        print(f'推荐构图未提供，沿用现有 {layout}；不会自动补留白。')
    if theme == 'adaptive':
        return (ROOT / 'base' / 'adaptive' / f'logo-{layout}-{kind}.svg').resolve()
    return (ROOT / 'base' / f'logo-{layout}-{kind}-{theme}.svg').resolve()


def ask_theme():
    surface = ask_choice('Logo 所在区域背景：', {
        '1': ('一直浅色', 'light'), '2': ('一直深色', 'dark'), '3': ('随界面明暗变化', 'changing')})
    if surface != 'changing':
        return surface
    usage = ask_choice('这份 Logo 的实际用途：', {
        '1': ('网页中随界面变化', 'web'), '2': ('设计稿、文档或图片导出', 'static'), '3': ('其他或不确定', 'unknown')})
    if usage == 'web':
        print('推荐 adaptive；接入后必须在目标浏览器验证浅色、深色及手动主题。')
        return 'adaptive'
    return ask_choice('本次实际展示区域的背景：', {'1': ('浅色', 'light'), '2': ('深色', 'dark')})


def offer_copy(source):
    while True:
        value = input('可选复制到文件夹或 .svg 路径（回车结束）：').strip()
        if not value:
            return
        destination = Path(value).expanduser()
        if destination.is_dir():
            destination /= source.name
        if destination.suffix.lower() != '.svg' or not destination.parent.is_dir():
            print('请输入已存在文件夹或父目录已存在的 .svg 路径。')
            continue
        try:
            with source.open('rb') as src, destination.open('xb') as dst:
                shutil.copyfileobj(src, dst)
        except OSError as error:
            print(f'未复制（不会覆盖已有文件）：{error}')
            continue
        print(f'已复制：{destination.resolve()}')
        return


def main():
    print('为一个场景选一次构图；全部尺寸、资源档位和 1×/2× 沿用。')
    scenario = input('已有场景名称（app/favicon/status 或项目名称，未知可回车）：').strip()
    existing = input('该场景已有构图（compact/spacious/original，未确定可回车）：').strip()
    if existing and existing not in ('compact', 'spacious', 'original'):
        print('未知构图；请先核对已有场景。', file=sys.stderr)
        return 1
    size = ask_size()
    kind = ask_choice('图标是否自带底板？', {'1': ('带底板', 'background'), '2': ('透明底', 'transparent')})
    theme = ask_theme()
    path = select_logo(size, kind, theme, scenario, existing or None)
    if not path.is_file():
        print(f'资源缺失：{path}\n请先确认角色或取得相应生成授权，不自动替代配色或留白。', file=sys.stderr)
        return 1
    print(f'文件绝对路径：{path}')
    if kind == 'background':
        print('基础 SVG 为直角；普通界面请由容器设置圆角并裁切，见 base/README.md。')
    offer_copy(path)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (EOFError, KeyboardInterrupt):
        print('\n已结束选择。')
