// 기획 문서를 Quartz 폴더로 옮겨 위키 사이트를 빌드할 준비를 한다.
//
// 사용법: node site/prepare.mjs <Quartz 폴더 경로>
//
// 1. 저장소의 Quartz 설정(site/quartz.config.ts, site/quartz.layout.ts)을 Quartz 폴더에 복사한다.
// 2. Quartz 폴더의 content/를 비우고 공개할 Markdown 문서를 복사한다.
// 3. 각 문서의 첫 줄 제목(# 제목)을 앞머리의 title로 옮긴다. 사이트에서 제목이 두 번 보이지 않게 하기 위함이다.
//    이때 폴더에 따라 분류 태그(확정·미확정 등)를 단다.
// 4. 사이트 첫 페이지(index.md)를 목차.md로 만든다.
// 문서 안의 <!-- site:exclude:start --> ~ <!-- site:exclude:end --> 구간은 사이트에서 뺀다.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const quartzDir = process.argv[2]
if (!quartzDir) {
  console.error("사용법: node site/prepare.mjs <Quartz 폴더 경로>")
  process.exit(1)
}

// 사이트에 올리지 않는 항목
const EXCLUDE = new Set([
  ".git",
  ".github",
  "node_modules",
  "site",
  "tools",
  "README.md",
  "AGENTS.md",
  "기록",
])

for (const name of ["quartz.config.ts", "quartz.layout.ts"]) {
  fs.copyFileSync(path.join(repoRoot, "site", name), path.join(quartzDir, name))
}

const contentDir = path.join(quartzDir, "content")
fs.rmSync(contentDir, { recursive: true, force: true })
fs.mkdirSync(contentDir, { recursive: true })

// 최상위 폴더(또는 파일)별 태그. 새 폴더를 만들면 여기에도 추가한다.
const TAGS = {
  "세계관": ["세계관", "확정"],
  "캐릭터": ["캐릭터", "확정"],
  "게임 기획": ["게임기획", "확정"],
  "임시 검토안": ["임시검토안", "미확정"],
}

// <!-- site:exclude:start --> 와 <!-- site:exclude:end --> 사이는 사이트에서 뺀다.
function stripExcluded(text) {
  return text.replace(/<!-- site:exclude:start -->[\s\S]*?<!-- site:exclude:end -->\r?\n?/g, "")
}

// 앞머리가 없는 문서의 첫 줄 "# 제목"을 앞머리 title로 바꾸고 태그를 단다.
function toSitePage(text, relPath) {
  text = stripExcluded(text)
  if (text.startsWith("---")) return text
  const match = text.match(/^# (.+)\r?\n/)
  if (!match) return text
  const title = match[1].replaceAll('"', '\\"')
  const tags = TAGS[relPath.split(path.sep)[0]] ?? []
  return `---\ntitle: "${title}"\ntags: [${tags.join(", ")}]\n---\n` + text.slice(match[0].length)
}

function copyMarkdown(srcDir, destDir) {
  for (const entry of fs.readdirSync(srcDir, { withFileTypes: true })) {
    if (EXCLUDE.has(entry.name) || entry.name.startsWith(".")) continue
    const src = path.join(srcDir, entry.name)
    const dest = path.join(destDir, entry.name)
    if (entry.isDirectory()) {
      fs.mkdirSync(dest, { recursive: true })
      copyMarkdown(src, dest)
    } else if (entry.name.endsWith(".md")) {
      const relPath = path.relative(repoRoot, src)
      fs.writeFileSync(dest, toSitePage(fs.readFileSync(src, "utf8"), relPath))
    }
  }
}
copyMarkdown(repoRoot, contentDir)

// 첫 페이지: 목차 내용을 쓰되 제목을 사이트 이름으로 두고, 사이트 제외 구간은 뺀다.
const toc = stripExcluded(fs.readFileSync(path.join(repoRoot, "목차.md"), "utf8")).replace(
  /^# .*\r?\n/,
  "",
)
fs.writeFileSync(
  path.join(contentDir, "index.md"),
  `---\ntitle: 노에라 인력 사무소 기획 위키\n---\n` + toc,
)

console.log(`문서를 ${contentDir}에 준비했습니다.`)
