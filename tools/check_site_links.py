"""빌드된 위키 사이트(Quartz의 public 폴더)에서 깨진 내부 링크와 앵커를 찾는다.

사용법: python tools/check_site_links.py <public 폴더 경로>
깨진 링크가 있으면 목록을 출력하고 종료 코드 1을 반환한다.
"""
import glob
import os
import re
import sys
import urllib.parse

LINK_RE = re.compile(r'<a href="([^"#]*)(#[^"]*)?" class="internal')
ID_RE = re.compile(r'id="([^"]+)"')


def page_ids(path, cache={}):
    if path not in cache:
        with open(path, encoding='utf-8') as f:
            cache[path] = set(ID_RE.findall(f.read()))
    return cache[path]


def resolve(page, href):
    """링크가 가리키는 HTML 파일을 찾는다. 빈 href는 같은 페이지를 뜻한다."""
    if href == '':
        return page
    target = os.path.normpath(os.path.join(os.path.dirname(page), urllib.parse.unquote(href)))
    for candidate in (target + '.html', os.path.join(target, 'index.html'), target):
        if os.path.isfile(candidate):
            return candidate
    return None


def main():
    if len(sys.argv) != 2:
        print('사용법: python tools/check_site_links.py <public 폴더 경로>')
        return 2
    root = sys.argv[1]
    broken, checked = [], 0
    for page in glob.glob(os.path.join(root, '**', '*.html'), recursive=True):
        with open(page, encoding='utf-8') as f:
            html = f.read()
        for m in LINK_RE.finditer(html):
            href, anchor = m.group(1), m.group(2)
            checked += 1
            rel = os.path.relpath(page, root)
            dest = resolve(page, href)
            if dest is None:
                broken.append(f'페이지 없음: {rel} -> {href}')
            elif anchor and urllib.parse.unquote(anchor[1:]) not in page_ids(dest):
                broken.append(f'앵커 없음: {rel} -> {href}{urllib.parse.unquote(anchor)}')
    for line in broken:
        print(line)
    print(f'검사한 링크 {checked}개, 깨진 링크 {len(broken)}개')
    return 1 if broken else 0


if __name__ == '__main__':
    sys.exit(main())
