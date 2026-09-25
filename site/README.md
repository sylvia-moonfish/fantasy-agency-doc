# 위키 사이트 설정

이 폴더는 [Quartz](https://quartz.jzhao.xyz/) v4로 기획 문서를 위키 사이트로 만드는 설정이다. 이 폴더 자체는 사이트에 올라가지 않는다.

| 파일 | 역할 |
| --- | --- |
| `quartz.config.ts` | 사이트 제목, 주소, 언어, 글꼴, 플러그인 설정 |
| `quartz.layout.ts` | 페이지 구성 요소(탐색기, 검색, 그래프, 역링크 등) 배치 |
| `prepare.mjs` | 문서를 Quartz의 `content/`로 복사하고, 제목을 앞머리로 옮기고, 폴더별 태그를 단다 |

## 자동 배포

`main` 브랜치에 올리면 `.github/workflows/deploy-site.yml`이 사이트를 빌드해 GitHub Pages에 배포한다. 저장소 설정의 **Pages → Source**가 **GitHub Actions**로 되어 있어야 한다.

## 로컬에서 미리 보기

Node.js 22 이상이 필요하다. 저장소 바깥의 빈 폴더에서 다음 순서로 실행한다.

```bash
git clone --depth 1 --branch v4.5.2 https://github.com/jackyzha0/quartz.git quartz
```

```bash
cd quartz && npm ci
```

```bash
node ../fantasy-agency-doc/site/prepare.mjs .
```

```bash
npx quartz build --serve
```

브라우저에서 `http://localhost:8080`을 연다. 문서를 고친 뒤에는 `prepare.mjs`를 다시 실행하면 반영된다.

## 문서를 쓸 때 주의할 점

- 문서 첫 줄의 `# 제목`은 사이트에서 페이지 제목이 되며 앵커가 사라진다. 다른 문서에서 문서 전체를 가리킬 때는 `문서.md#제목` 대신 `문서.md`로 링크한다. `python tools/check_links.py`가 이를 검사한다.
- 최상위 폴더를 새로 만들면 `prepare.mjs`의 `TAGS`에도 추가한다.
- 사이트에 올리지 않을 항목은 `prepare.mjs`의 `EXCLUDE`에 추가한다.
