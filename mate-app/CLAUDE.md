# 메이트(Mate) — 마스터 컨텍스트

## 프로젝트
- 앱: 메이트 (Mate) | 슬로건: 돈의 길, 아무도 안 알려줬잖아요
- 개념: 경제 길잡이 — 답이 아닌 "이런 길도 있다"를 보여주는 앱
- 타겟: 22~38세 | GitHub: github.com/minchul-der/mate-app
- 스택: HTML/CSS/JS, 모바일 375px 우선, #4F9EFF/#FFD166/#0D1B2A

## 에이전트 호출 기준
| 상황 | 호출할 에이전트 |
|------|--------------|
| 화면 기획·흐름 결정 | @.claude/agents/oracle.md |
| UI·색감·레이아웃 결정 | @.claude/agents/pixel.md |
| 문구·카피·안내 문구 결정 | @.claude/agents/stylist.md |

## 컨텍스트 파일 호출 기준
| 필요한 상황 | 호출할 파일 |
|------------|-----------|
| 철학·원칙이 필요할 때 | @.claude/context/philosophy.md |
| 레퍼런스 앱 분석이 필요할 때 | @.claude/context/references.md |
| 색상·폰트·컴포넌트 규격이 필요할 때 | @.claude/context/design-system.md |
| 면책 고지·법적 문구가 필요할 때 | @.claude/context/legal-templates.md |
| 온보딩 설계 규칙이 필요할 때 | @.claude/context/onboarding-design.md |

## 작업 흐름
```
에이전트 분석 + 제안 3가지 → 사장님 선택
→ Antigravity 기획 확정 → 사장님 승인
→ Claude Code(터미널) 코드 작성
→ Antigravity 미리보기 → GitHub commit
```

## 체크포인트
- 승인 없이 코드 작성·수정·삭제 금지
- 코드 수정 전 Git commit 먼저
- 보고 → 승인 → 실행 순서 항상 준수
- 코딩 명령은 영어로 처리, 응답은 한국어로
