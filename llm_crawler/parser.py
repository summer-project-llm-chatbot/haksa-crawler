# llm_crawler/parser.py
from typing import List, Dict, Any
from llm_crawler.dto import CourseRecord

def parse_dl_main(json_data: Dict[str, Any]) -> List[CourseRecord]:
    """
    json_data['dl_main'] 리스트에서
    - CDT
    - CURI_TYPE_CD_NM
    - CURI_NO
    - CURI_NM
    네 개 값만 추출해 CourseRecord 객체 리스트로 반환합니다.
    """
    records: List[CourseRecord] = []
    for item in json_data.get("dl_main", []):
        try:
            cdt = float(item.get("CDT", 0))
        except (TypeError, ValueError):
            cdt = 0.0

        record = CourseRecord(
            cdt=cdt,
            type_name=item.get("CURI_TYPE_CD_NM", ""),
            curi_no=item.get("CURI_NO", ""),
            curi_nm=item.get("CURI_NM", "")
        )
        records.append(record)
    return records
