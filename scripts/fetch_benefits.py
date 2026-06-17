#!/usr/bin/env python3
"""
메이트 앱 — 정부 혜택 데이터 자동 수집 스크립트
GitHub Actions에서 매일 KST 01:00에 자동 실행됩니다.

GitHub Secrets에 등록할 환경변수:
  DATA_GO_KR_API_KEY  — 공공데이터포털 API 키 (https://www.data.go.kr)
  BOKJIRO_API_KEY     — 복지로 오픈API 키 (https://www.bokjiro.go.kr)
  FSS_API_KEY         — 금융감독원 오픈API 키 (https://finlife.fss.or.kr)
  LH_API_KEY          — LH공사 오픈API 키 (https://www.data.go.kr)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("[ERROR] requests 모듈 없음. pip install requests 실행 필요.")
    sys.exit(1)

KST = timezone(timedelta(hours=9))
ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "benefits.json"

# ── 대상 연령 (메이트 앱 타겟) ──────────────────────────────
TARGET_AGE_MIN = 15
TARGET_AGE_MAX = 40

# ── 수집 대상 카테고리 키워드 ──────────────────────────────
YOUTH_KEYWORDS = [
    "청년", "대학생", "취업준비", "구직", "신혼부부",
    "전세", "월세", "청약", "임대", "금융지원", "창업"
]


def load_current() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"meta": {}, "benefits": []}


def save(benefits: list, note: str = ""):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(KST)
    data = {
        "meta": {
            "updated_at": now.isoformat(),
            "total_count": len(benefits),
            "version": "1.1.0",
            "note": note or f"자동 업데이트 — {now.strftime('%Y-%m-%d %H:%M KST')}",
            "sources": [
                "공공데이터포털", "복지로", "금융감독원",
                "LH공사", "주택도시기금", "고용노동부"
            ]
        },
        "benefits": benefits
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[SAVE] {DATA_FILE.name} — {len(benefits)}건 저장 완료")


# ────────────────────────────────────────────────────────────
# 복지로 오픈API
# 문서: https://www.bokjiro.go.kr/ssis-tbu/twatga/openApi/openApiInfo.do
# ────────────────────────────────────────────────────────────
def fetch_bokjiro(api_key: str) -> list:
    if not api_key:
        print("[SKIP] 복지로 API 키 없음 → 기존 데이터 유지")
        return []

    url = "http://www.bokjiro.go.kr/openapi/rest/wlfareInfo"
    results = []

    try:
        for page in range(1, 11):  # 최대 1,000건
            resp = requests.get(url, params={
                "serviceKey": api_key,
                "pageNo": page,
                "numOfRows": 100,
                "srvTarget": "003",   # 청년 (srvTarget 코드: 003)
                "lifeArray": "003",
            }, timeout=30)

            if resp.status_code != 200:
                print(f"  [WARN] 복지로 HTTP {resp.status_code}")
                break

            try:
                data = resp.json()
            except Exception:
                break

            items = (
                data.get("wlfareInfo", {})
                    .get("list", [])
            )
            if not items:
                break

            results.extend(items)
            print(f"  복지로 {len(results)}건 수집 중...")
            time.sleep(0.3)

    except Exception as e:
        print(f"[ERROR] 복지로 API: {e}")

    print(f"  복지로 최종 {len(results)}건")
    return results


# ────────────────────────────────────────────────────────────
# 금융감독원 금융상품 비교공시 API
# 문서: https://finlife.fss.or.kr/finlife/api/fncCoApi/list.do
# ────────────────────────────────────────────────────────────
def fetch_fss(api_key: str) -> list:
    if not api_key:
        print("[SKIP] 금융감독원 API 키 없음 → 기존 데이터 유지")
        return []

    results = []

    endpoints = [
        # 정기예금
        "https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json",
        # 적금
        "https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json",
        # 연금저축
        "https://finlife.fss.or.kr/finlifeapi/annuitySavingProductsSearch.json",
    ]

    for ep in endpoints:
        try:
            resp = requests.get(ep, params={
                "auth": api_key,
                "topFinGrpNo": "020000",
                "pageNo": 1,
            }, timeout=30)

            if resp.status_code != 200:
                continue

            data = resp.json().get("result", {})
            base = data.get("baseList", [])
            results.extend(base)
            print(f"  금감원 {ep.split('/')[-1]}: {len(base)}건")
            time.sleep(0.3)

        except Exception as e:
            print(f"  [WARN] 금감원 {ep}: {e}")

    return results


# ────────────────────────────────────────────────────────────
# LH 청약정보 API (공공데이터포털)
# 데이터셋: LH 임대주택 정보 서비스
# ────────────────────────────────────────────────────────────
def fetch_lh(api_key: str) -> list:
    if not api_key:
        print("[SKIP] LH API 키 없음 → 기존 데이터 유지")
        return []

    url = "https://apis.data.go.kr/B552555/lhLeaseNoticeInfo1/lhLeaseNoticeInfo1"
    results = []

    try:
        resp = requests.get(url, params={
            "serviceKey": api_key,
            "PG_SZ": 100,
            "PAGE": 1,
            "SPL_TP_CD": "07",   # 청년 매입임대
        }, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            items = data.get("dsList", [])
            results.extend(items)
            print(f"  LH {len(results)}건 수집")

    except Exception as e:
        print(f"[ERROR] LH API: {e}")

    return results


# ────────────────────────────────────────────────────────────
# 수집 데이터 → 메이트 스키마 변환
# API 응답이 연동되면 이 함수에 변환 로직을 추가하세요.
# ────────────────────────────────────────────────────────────
def transform_bokjiro(raw_items: list, existing_ids: set) -> list:
    """복지로 API 응답 → benefits 스키마 변환 (TODO: 실제 연동 시 구현)"""
    converted = []
    for item in raw_items:
        try:
            benefit_id = f"bokjiro_{item.get('servId', '')}"
            if benefit_id in existing_ids:
                continue  # 이미 수동 등록된 항목은 건너뜀

            # 키워드 필터링 — 청년 관련 항목만
            name = item.get("servNm", "")
            target = item.get("tgtrDtlCn", "")
            combined = name + target
            if not any(kw in combined for kw in YOUTH_KEYWORDS):
                continue

            # TODO: 실제 필드 매핑은 API 응답 확인 후 구현
            # converted.append({
            #     "id": benefit_id,
            #     "name": name,
            #     "category": "복지",
            #     "source": "복지로",
            #     "apply_url": item.get("servDtlLink", "https://www.bokjiro.go.kr"),
            #     ...
            # })

        except Exception as e:
            print(f"  [WARN] 변환 실패: {e}")

    return converted


def transform_fss(raw_items: list) -> list:
    """금감원 API 응답 → benefits 스키마 변환 (TODO: 실제 연동 시 구현)"""
    # TODO: 청년 우대 상품 필터링 및 스키마 변환 구현
    return []


def transform_lh(raw_items: list) -> list:
    """LH API 응답 → benefits 스키마 변환 (TODO: 실제 연동 시 구현)"""
    # TODO: 청년 임대주택 항목 필터링 및 스키마 변환 구현
    return []


# ────────────────────────────────────────────────────────────
# 메인
# ────────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  메이트 혜택 데이터 수집 시작")
    print(f"  {datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')}")
    print("=" * 50)

    # 환경변수에서 API 키 로드
    data_go_kr_key = os.environ.get("DATA_GO_KR_API_KEY", "")
    bokjiro_key    = os.environ.get("BOKJIRO_API_KEY", "") or data_go_kr_key
    fss_key        = os.environ.get("FSS_API_KEY", "")
    lh_key         = os.environ.get("LH_API_KEY", "") or data_go_kr_key

    # 현재 JSON 로드
    current = load_current()
    base_benefits = current.get("benefits", [])
    existing_ids = {b["id"] for b in base_benefits}
    print(f"\n현재 등록된 혜택: {len(base_benefits)}건")

    # API 수집
    print("\n[STEP 1] 복지로 API 수집")
    bokjiro_raw = fetch_bokjiro(bokjiro_key)

    print("\n[STEP 2] 금융감독원 API 수집")
    fss_raw = fetch_fss(fss_key)

    print("\n[STEP 3] LH공사 API 수집")
    lh_raw = fetch_lh(lh_key)

    # 변환 및 병합
    print("\n[STEP 4] 데이터 변환 및 병합")
    new_benefits = []
    new_benefits.extend(transform_bokjiro(bokjiro_raw, existing_ids))
    new_benefits.extend(transform_fss(fss_raw))
    new_benefits.extend(transform_lh(lh_raw))

    if new_benefits:
        merged = base_benefits + new_benefits
        print(f"  신규 {len(new_benefits)}건 추가 → 총 {len(merged)}건")
        save(merged)
    else:
        # API 연동 없음 → 기존 수동 데이터 유지, updated_at만 갱신
        print("  신규 API 데이터 없음 — 기존 데이터 유지, 타임스탬프 갱신")
        save(base_benefits, "수동 데이터 유지 — API 키 연동 대기 중")

    print("\n[완료]")


if __name__ == "__main__":
    main()
