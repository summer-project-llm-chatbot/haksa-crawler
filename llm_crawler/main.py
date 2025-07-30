# llm_crawler/main.py
import argparse
import json
from llm_crawler.crawler import perform_login_and_fetch
from llm_crawler.dto import LoginInfo
from llm_crawler.enums import CrawlStatus
from llm_crawler.parser import parse_dl_main

def main():
    parser = argparse.ArgumentParser(description="LLM 대학 성적 크롤러 및 파서")
    parser.add_argument(
        "--user-id", "-u",
        help="학번 또는 사용자 ID"
    )
    parser.add_argument(
        "--password", "-p",
        help="비밀번호"
    )
    parser.add_argument(
        "--out", "-o",
        default="records.json",
        help="파싱 결과를 저장할 JSON 파일 경로 (기본: records.json)"
    )
    args = parser.parse_args()

    login = LoginInfo(user_id=args.user_id, password=args.password)
    status, raw_data = perform_login_and_fetch(login)

    if status is not CrawlStatus.SUCCESS or not isinstance(raw_data, dict):
        print("크롤링에 실패했습니다.")
        return

    # 파싱
    records = parse_dl_main(raw_data)
    # 결과 저장
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump([r.__dict__ for r in records], f, ensure_ascii=False, indent=2)

    print(f"요약 {len(records)}건을 '{args.out}'에 저장했습니다.")

if __name__ == "__main__":
    main()
