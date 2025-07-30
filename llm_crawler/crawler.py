import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Page
from llm_crawler.config import LOGIN_URL, RECORDS_URL, TIMEOUT_SECONDS, EXPECTED_POST_LOGIN_URL
from llm_crawler.dto    import LoginInfo
from llm_crawler.enums  import CrawlStatus
from typing import Tuple

def perform_login_and_fetch(login: LoginInfo) -> Tuple[CrawlStatus, str]:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(TIMEOUT_SECONDS * 1_000)

        try:
            # 1) 로그인 페이지로 이동
            print("[로그인 시작] → login page 진입")
            page.goto(LOGIN_URL)

            # 2) 아이디/비밀번호 입력
            print("[로그인 입력]")
            page.locator("#id").click()
            page.locator("#id").fill(login.user_id)
            page.locator("input[type='password']").click()
            page.locator("input[type='password']").fill(login.password)

            # 3) 로그인 버튼 클릭 & 대시보드 진입 대기
            print("[로그인 클릭]")
            page.locator("#loginBtn").click()
            print("[로그인 성공 대기 중]")

            try:
                # 성공 URL 도달 대기
                page.wait_for_url(f"{EXPECTED_POST_LOGIN_URL}*", timeout=TIMEOUT_SECONDS * 1_000)
            except PlaywrightTimeoutError:
                current_url = page.url
                if "login" in current_url:
                    print("[경고] 로그인 실패: 로그인 페이지로 되돌아옴")
                    return CrawlStatus.FAILURE, "잘못된 아이디 또는 비밀번호입니다."
                else:
                    print("[오류] 알 수 없는 URL에서 타임아웃:", current_url)
                    dump_debug_state(page, "unexpected_url_timeout")
                    return CrawlStatus.FAILURE, "알 수 없는 오류로 로그인에 실패했습니다."

            print(f"[현재 페이지]: {page.url}")

            # 4) 로그인 성공 체크
            if EXPECTED_POST_LOGIN_URL not in page.url:
                return CrawlStatus.FAILURE, ""

            # 5) 정보시스템 → 학사정보시스템(팝업)
            page.get_by_role("link", name="정보시스템", exact=True).click()
            with page.expect_popup() as pop_info:
                page.get_by_role("link", name="학사정보시스템").click()
            page1 = pop_info.value
            page1.set_default_timeout(TIMEOUT_SECONDS * 1_000)

            # 6) doList.do 요청 URL 및 Cookie 캡처
            captured = {"url": None}
            def _capture_request(req):
                if req.resource_type == "xhr" and "SugRecordQ/doList.do" in req.url:
                    captured["url"] = req.url
            page1.on("request", _capture_request)

            # 7) 팝업 내 메뉴 탐색
            page1.wait_for_selector("div.w2popup_window", timeout=TIMEOUT_SECONDS * 1_000)
            page1.get_by_role("link", name="확인").click(force=True)
            page1.wait_for_load_state("networkidle")

            page1.get_by_text("수업/성적").click()
            page1.wait_for_timeout(300)
            page1.get_by_text("성적 및 강의평가").click()
            page1.wait_for_timeout(300)

            # 8) 기이수성적조회 클릭과 동시에 doList.do 응답 캡처
            with page1.expect_response(
                    lambda res: res.request.resource_type == "xhr"
                                and captured["url"] is not None
                                and res.url == captured["url"],
                    timeout=TIMEOUT_SECONDS * 1_000
            ) as resp_info:
                page1.get_by_text("기이수성적조회").click()
            response: Response = resp_info.value

            # 9) JSON 텍스트 또는 dict로 파싱
            #json_text = response.text()
            json_data = response.json()

            # 10) 결과 반환
            return CrawlStatus.SUCCESS, json_data

        except PlaywrightTimeoutError as e:
            print("실패: 타임아웃 발생 →", e)
            dump_debug_state(page, "timeout_error")
            return CrawlStatus.FAILURE, ""
        finally:
            browser.close()


if __name__ == "__main__":
    # 실제 로그인 정보 주입
    login_info = LoginInfo(user_id, password)
    status, data = perform_login_and_fetch(login_info)
    print(f"크롤링 결과: {status}")
