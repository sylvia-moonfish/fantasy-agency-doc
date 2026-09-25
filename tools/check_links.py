"""프로젝트 안의 모든 Markdown 문서에서 깨진 상대 링크와 제목 앵커를 찾는다.

사용법: python tools/check_links.py
깨진 링크가 있으면 목록을 출력하고 종료 코드 1을 반환한다.
"""
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', 'node_modules', 'public', '.quartz-cache'}
LINK_RE = re.compile(r'\]\(([^)\s]+)\)')
HEADING_RE = re.compile(r'^#+\s+(.*)')


def slug(title):
    """GitHub 방식과 같은 제목 앵커를 만든다."""
    title = title.strip().lower()
    title = ''.join(c for c in title if c.isalnum() or c in '-_ ')
    return title.replace(' ', '-')


def title_anchor(path):
    """문서 첫 줄의 "# 제목" 앵커. 위키 사이트에서는 이 제목이 앵커 없이 페이지 제목으로 바뀐다."""
    with open(path, encoding='utf-8') as f:
        m = re.match(r'# (.+)', f.readline())
    return slug(m.group(1)) if m else None


def anchors(path, cache={}):
    if path not in cache:
        with open(path, encoding='utf-8') as f:
            cache[path] = {slug(m.group(1)) for line in f for m in [HEADING_RE.match(line)] if m}
    return cache[path]


def markdown_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith('.md'):
                yield os.path.join(dirpath, name)


def main():
    broken = []
    files = list(markdown_files())
    for path in files:
        with open(path, encoding='utf-8') as f:
            text = f.read()
        for m in LINK_RE.finditer(text):
            target = urllib.parse.unquote(m.group(1))
            if re.match(r'^[a-z]+:', target):
                continue
            file_part, _, anchor = target.partition('#')
            dest = os.path.normpath(os.path.join(os.path.dirname(path), file_part)) if file_part else path
            rel = os.path.relpath(path, ROOT)
            if not os.path.exists(dest):
                broken.append(f'파일 없음: {rel} -> {target}')
            elif anchor and os.path.isfile(dest) and anchor not in anchors(dest):
                broken.append(f'앵커 없음: {rel} -> {target}')
            elif anchor and os.path.isfile(dest) and anchor == title_anchor(dest):
                broken.append(f'문서 제목 앵커(위키에서 깨짐, 앵커 없이 문서만 링크할 것): {rel} -> {target}')
    for line in broken:
        print(line)
    print(f'검사한 문서 {len(files)}개, 깨진 링크 {len(broken)}개')
    return 1 if broken else 0


if __name__ == '__main__':
    sys.exit(main())
