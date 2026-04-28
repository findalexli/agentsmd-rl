#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prism-insight

# Idempotency guard
if grep -qF "| 2.5.0 | 2026-02-22 | **Telegram /report \uc77c\uc77c \ud69f\uc218 \ud658\uae09 + \ud55c\uad6d\uc5b4 \uba54\uc2dc\uc9c0 \ubcf5\uc6d0** - \uc11c\ubc84 \uc624\ub958(\uc11c\ube0c\ud504\ub85c\uc138\uc2a4" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,6 +1,6 @@
 # CLAUDE.md - AI Assistant Guide for PRISM-INSIGHT
 
-> **Version**: 2.4.9 | **Updated**: 2026-02-21
+> **Version**: 2.5.0 | **Updated**: 2026-02-22
 
 ## Quick Overview
 
@@ -153,6 +153,7 @@ result = await trading.async_sell_stock(ticker=ticker, limit_price=current_price
 | prism-us import error | Use `_import_from_main_cores()` helper |
 | Telegram message in English | v2.2.0 restored Korean templates - pull latest |
 | Broadcast translation empty | gpt-5-mini fallback added in v2.2.0 |
+| `/report` 오류 후 재사용 불가 | v2.5.0 수정 - 서버 오류 시 자동 환급됨, 재시도 가능 |
 
 ## i18n Strategy (v2.2.0)
 
@@ -182,6 +183,7 @@ test: Tests
 
 | Ver | Date | Changes |
 |-----|------|---------|
+| 2.5.0 | 2026-02-22 | **Telegram /report 일일 횟수 환급 + 한국어 메시지 복원** - 서버 오류(서브프로세스 타임아웃, 내부 AI 에이전트 오류) 시 `/report`·`/us_report` 일일 사용 횟수 자동 환급 (`refund_daily_limit`, `_is_server_error` 추가, `send_report_result` 내 환급 처리), `AnalysisRequest`에 `user_id` 필드 추가, Telegram 봇 사용자 대면 메시지 한국어 템플릿 복원 |
 | 2.4.9 | 2026-02-21 | **US 분석 버그 5종 수정** - `data_prefetch._df_to_markdown` tabulate 의존성 제거 (직접 마크다운 테이블 생성), `us_telegram_summary_agent` evaluator 프롬프트에 `needs_improvement` JSON 형식 명세 추가 + 평가 등급 0-3으로 정정 (Pydantic validation 오류 해결), `create_us_sell_decision_agent` US holding 매도 판단에 연결 (규칙 기반→AI 기반, fallback 유지), `redis_signal_publisher` 로그 KRW 하드코딩→`market` 필드 기반 USD/KRW 동적 출력, GCP Pub/Sub credentials 경로 로그 추가 + `GCP_CREDENTIALS_PATH` 미설정 경고 (401 진단 개선) |
 | 2.4.8 | 2026-02-19 | **US 매수 가격 수정 + GCP 인증 + Firebase Bridge 타입 감지 버그 3종 수정** - `get_current_price()` KIS `last` 빈 문자열 시 `base`(전일종가) fallback 추가, `async_buy_stock()` KIS 가격 조회 실패 시 `limit_price` fallback (예약주문 보장), GCP Pub/Sub 401 → 명시적 `service_account.Credentials` 인증으로 전환, `detect_type()` 포트폴리오 키워드 구체화 (`포트폴리오 관점` 오탐 방지), `detect_type()` 트리거 키워드(`트리거/급등/급락/surge`) analysis 이전에 체크 (매수신호 포함 트리거 알림 정상 분류), `extract_title()` 파일경로 체크를 markdown 정리 이전으로 이동 (PDF 파일명 언더바 보존) |
 | 2.4.7 | 2026-02-16 | **주간 리포트 확장 + 압축 후행평가** - 주간 매매 요약, 매도 후 평가, AI 장기 학습 인사이트, L1→L2 압축 후행 교훈, 다국어 broadcast 지원 |
PATCH

echo "Gold patch applied."
