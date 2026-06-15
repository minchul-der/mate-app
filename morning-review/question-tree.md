# 온보딩 질문 트리 알고리즘 (2026-06-16)

목표: 5개 이하 질문으로 사용자 성향 3가지 도출
- 투자 성향 (안전 / 균형 / 적극)
- 소비 습관 (안정형 / 유동형)
- 재무 목표 (단기 / 중기 / 장기)

---

## 핵심 설계 원칙

1. **첫 질문이 가장 중요한 분기점**
   - 직업 → 소득 범위·소비 패턴 예측
   - 목표 → 이후 질문 순서 결정

2. **중복 추론 (Implicit Inference)**
   - 직접 묻지 않아도 조합으로 파악
   - 예: 학생 + 1인가구 → 비상금 필요성 매우 높음 → 안전형 확률 60%+

3. **최대 5개 슬라이드 유지**
   - 슬라이드 수 변경 없이 내부 질문만 적응형으로 변경

---

## 분기 트리 구조

```
[슬라이드 1] 생년월일 + 직업
    │
    ├─ 학생·취준생
    │   └─ [슬라이드 3] 소득 범위: 0~50만원 / 50~100만원 / 100만원+ (학생 기준)
    │   └─ [성향 추정] 목표=비상금·자기계발 확률↑ / 스타일=안전형 확률↑
    │
    ├─ 프리랜서·계약직
    │   └─ [슬라이드 3] 소득: 불규칙 여부 추가 질문
    │   └─ [성향 추정] 비상금 니즈 특히 높음
    │
    ├─ 직장인·회사원
    │   └─ [슬라이드 3] 기존 소득 칩 (100만원 단위)
    │   └─ [성향 추정] 내집마련·노후준비 관심 높음
    │
    └─ 자영업·기타
        └─ [슬라이드 3] 기존 소득 칩 (가장 다양)
```

---

## 3가지 성향 도출 공식

### A. 투자 성향 스코어 (0~10)

| 입력값 | 포인트 |
|--------|--------|
| goal = 비상금/부채상환 | +3 안전형 |
| goal = 노후준비/내집마련 | +1 균형형 |
| goal = 여행/취미/기타 | +1 적극형 |
| style 직접 선택 (슬라이드 5) | 직접 반영 |
| income < 200만원 | +2 안전형 |
| income >= 400만원 | +1 적극형 |
| age < 28 | +1 적극형 (시간 여유) |
| housing = 월세/공공임대 | +2 안전형 |

**최종 판정:**
- 안전형 포인트 >= 5 → 안전형 추천
- 적극형 포인트 >= 5 → 적극형 추천
- 그 외 → 균형형

### B. 소비 습관 분류

| 조건 | 분류 |
|------|------|
| housing = 월세 + income < 300 | 유동형 (고정비 부담 높음) |
| housing = 자가 | 안정형 (고정비 낮음) |
| family = 1인가구 + 학생 | 유동형 |
| family = 신혼/자녀 | 안정형 (필수 지출 계획적) |

### C. 재무 목표 기간

| goal | 기간 |
|------|------|
| 비상금 | 단기 (6개월~1년) |
| 내집마련 | 중기 (3~7년) |
| 부채상환 | 단기~중기 |
| 노후준비 | 장기 (10년+) |
| 여행·취미 | 단기 |

---

## onboarding.html 적용 로직

```javascript
/* ══ 적응형 질문 엔진 ══ */
function deriveProfile(ans) {
  const now = new Date();
  const age  = now.getFullYear() - ans.birthYear;
  
  let safeScore = 0, aggressiveScore = 0;
  
  // 목표 기반
  if (['비상금','부채상환'].includes(ans.goal)) safeScore += 3;
  if (ans.goal === '여행취미') aggressiveScore += 2;
  
  // 소득 기반
  const incomeMap = {
    '100만원 미만': -2, '100~200만원': -1,
    '200~300만원': 0,   '300~400만원': 1,
    '400~500만원': 2,   '500만원 이상': 3,
  };
  const incScore = incomeMap[ans.income] || 0;
  if (incScore < 0) safeScore += Math.abs(incScore);
  else aggressiveScore += incScore;
  
  // 나이 기반 (젊을수록 위험 여유)
  if (age < 27) aggressiveScore += 2;
  else if (age > 33) safeScore += 1;
  
  // 주거 기반
  if (['월세','공공임대','비주택'].includes(ans.housing)) safeScore += 2;
  if (ans.housing === '자가') aggressiveScore += 1;
  
  // 직업 기반
  if (['프리랜서','학생'].includes(ans.job)) safeScore += 2;
  
  // 최종 성향
  let derivedStyle;
  if (!ans.style) {
    // 사용자가 직접 선택 안 했을 때만 추론 적용
    if (safeScore >= 5) derivedStyle = '안전';
    else if (aggressiveScore >= 5) derivedStyle = '적극';
    else derivedStyle = '균형';
  } else {
    derivedStyle = ans.style; // 직접 선택 우선
  }
  
  // 소비 습관
  let spendingType;
  if (ans.housing === '월세' && ['100만원 미만','100~200만원','200~300만원'].includes(ans.income)) {
    spendingType = '유동형';
  } else if (ans.housing === '자가' || ans.family === '신혼부부') {
    spendingType = '안정형';
  } else {
    spendingType = '균형형';
  }
  
  // 목표 기간
  const goalPeriod = {
    '비상금': '단기', '부채상환': '단기',
    '내집마련': '중기', '여행취미': '단기',
    '노후준비': '장기', '기타': '중기',
  }[ans.goal] || '중기';
  
  return { derivedStyle, spendingType, goalPeriod, age };
}

/* 학생 선택 시 소득 칩 범위 변경 */
function adaptSlide3ForStudent() {
  const chips = document.querySelectorAll('#slide3 .chip-btn');
  const studentRanges = ['없음·장학금', '50만원 미만', '50~100만원', '100~200만원', '아르바이트 병행', '기타'];
  chips.forEach((chip, i) => {
    if (studentRanges[i]) {
      chip.setAttribute('data-val', studentRanges[i]);
      chip.innerHTML = studentRanges[i].replace('·', '<br/>');
      chip.onclick = () => pickChip(chip, 'income', studentRanges[i]);
    }
  });
}
```

**슬라이드 1 직업 선택 이벤트에 연결:**
```javascript
// pick() 함수 안에 직업별 분기 추가
function pick(btn, key, val) {
  btn.closest('.radio-list').querySelectorAll('.radio-item').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  ans[key] = val;
  
  // 학생 선택 시 슬라이드 3 적응
  if (key === 'job' && val === '학생') {
    adaptSlide3ForStudent();
    ans.income = null; // 기존 소득 선택 초기화
  } else if (key === 'job') {
    // 다른 직업으로 바꾸면 원래 소득 칩으로 복원
    restoreDefaultIncome();
  }
  
  checkSlide();
}
```

---

## 구현 현황

- [x] 알고리즘 설계 완료 (this file)
- [x] `deriveProfile()` 로직 `onboarding.html`에 적용
- [x] 학생 선택 시 소득 칩 어댑티브 변경 구현
- [x] result.html에서 `deriveProfile()` 활용하여 카드 선택

---

## 향후 개선 포인트

1. **학생 소득 범위** — 현재 수동 매핑, 향후 JSON 데이터로 분리
2. **A/B 테스트** — 성향 추론 정확도 검증 (사용자 설문 피드백 수집)
3. **더 많은 변수** — 자산 규모를 성향 판단에 반영 (현재 소득만 사용)
