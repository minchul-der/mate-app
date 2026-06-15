# Pixel Report — UI 컴포넌트 감사

분석 대상: `index.html`, `onboarding.html`, `css/style.css` (2026-06-16 기준)

---

## 핵심 문제: 두 화면의 그린 컬러가 다름

| 파일 | 그린 값 | 비고 |
|------|--------|------|
| `index.html` (style.css 로드) | `#00C47A` | `--color-primary` |
| `onboarding.html` (인라인 CSS) | `#00A86B` | `--green` |

사용자가 인트로 → 온보딩으로 이동할 때 브랜드 그린이 눈에 띄게 달라짐. 통일 필요.

**수정:** `onboarding.html`의 `--green: #00A86B` → `#00C47A`로 변경, 또는 `css/style.css`를 온보딩에서도 `<link>`로 로드.

---

## 폰트 로드 중복

`index.html`은 `css/style.css`로 Noto Sans KR 로드.
`onboarding.html`은 `<head>`에 별도로 같은 Google Fonts URL 재호출.

**수정:** 공통 CSS에서 한 번만 로드하거나, 온보딩에서도 `style.css` 링크 추가.

---

## 모바일 375px 터치 타깃 미달

| 요소 | 실제 크기 | 권장 |
|------|---------|------|
| 뒤로 버튼 `.back-btn` | 38×38px | 44×44px |
| 건너뛰기 `.skip-btn` | ~30×30px (padding 8px) | 44×44px |
| 소득 칩 `.chip-btn` | ~100×38px | OK |
| 주거 그리드 `.grid-item` | ~160×55px | OK |

**수정:** `.back-btn { width:44px; height:44px; }`, `.skip-btn { padding: 12px 14px; }`

---

## 슬라이드 4 주거 그리드: 일부 카드 sub-text 없음

"전세", "월세" 카드에는 `.grid-sub`가 없어 다른 카드들(자가/공공임대/고시원/가족)과 시각적 높이가 달라짐 → 그리드 불균형.

```html
<!-- 현재 -->
<button class="grid-item" onclick="pickGrid(this,'housing','전세')">
  <span class="grid-icon">🔑</span>전세
</button>

<!-- 수정 -->
<button class="grid-item" onclick="pickGrid(this,'housing','전세')">
  <span class="grid-icon">🔑</span>전세
  <span class="grid-sub">보증금 계약</span>
</button>
```

---

## 배경색 불일치

- `index.html` 배경: `#F7F8FA` (style.css `--color-bg`)
- `onboarding.html` 배경: `#F0F4F8` (`--bg`)

두 화면의 배경이 미세하게 달라 전환 시 깜빡임처럼 보일 수 있음.
