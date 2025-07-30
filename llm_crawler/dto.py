from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class LoginInfo:
    user_id: str
    password: str

@dataclass(frozen=True)
class CourseRecord:
    cdt: float
    type_name: str
    curi_no: str
    curi_nm: str