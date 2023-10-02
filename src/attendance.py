from audioop import mul
import numpy as np
import requests
import json
import argparse
from typing import Any
import pandas as pd


class LessonData:

    def __init__(self, group_name: str = "", instance_id: int = -1, group_id: int = -1):
        self.group_name = group_name
        self.instance_id = instance_id
        self.group_id = group_id
        self.students_ids: dict[str, set] = {}
        self.students_ids_marked = set()

    def check_attendance(self, students_names: set):
        for name, st_ids in self.students_ids.items():
            if name in students_names:
                self.students_ids_marked.update(st_ids)

    def get_post_data(self) -> dict:
        users = []
        for st_ids in self.students_ids.values():
            for st_id in st_ids:
                users.append({
                    "user": {"id": st_id},
                    "teacherReported": st_id in self.students_ids_marked
                })
        data = {"users": users, "lessonInstanceIds": [self.instance_id]}
        return data


LESSON_TITLE = "Программирование"
LESSON_TYPE = "Лек"
BASE_URL = "https://digital.etu.ru/attendance/api/schedule/check-in/teacher"
CHECKS_COUNT = 2
MIN_TIME = 30 * 60  # min


def parse_args() -> dict[str, Any]:
    argp = argparse.ArgumentParser()
    argp.add_argument("-c", "--cookies", type=str, help="Path to json file with cookies", required=True)
    argp.add_argument("-d", "--date", type=str, help="Week to get information about (set the Wednesday day). Example: 2023-09-26", required=True)
    argp.add_argument("-a", "--attendance", type=str, help="Path to csv file with attendance", required=True)
    args = argp.parse_args()
    return {
        "cookie": args.cookies,
        "table": args.attendance,
        "date": args.date,
    }


def create_session(cookies_filename: str) -> requests.Session:
    with open(cookies_filename, "r") as f:
        cookies = json.load(f)
    s = requests.Session()
    for k, v in cookies.items():
        s.cookies.set(k, v)
    return s


def create_lessons_data(session: requests.Session, date: str) -> dict[str, LessonData]:
    data = session.get(f"{BASE_URL}?date={date}").json()
    result = {}
    for lesson in data:
        if lesson.get("lesson", {}).get("title", "") != LESSON_TITLE or lesson.get("lesson", {}).get("subjectType", "") != LESSON_TYPE:
            continue
        for group in lesson.get("groups", []):
            lesson_data = LessonData(
                group_id=group.get("id", -1),
                group_name=group.get("name", ""),
                instance_id=group.get("lessonInstanceId", -1)
            )
            result[lesson_data.group_name] = lesson_data
    return result


def add_students_info(session: requests.Session, lessons: dict[str, LessonData]):
    lesson_by_id = {lesson.group_id: lesson for lesson in lessons.values()}
    users = session.get(f"{BASE_URL}/lesson-instances?{'&'.join([f'lessonInstanceId={lesson.instance_id}' for lesson in lesson_by_id.values()])}").json()
    for user in users.get("users", []):
        lesson = lesson_by_id[user.get("groupId")]
        student_data = user.get("user", {})
        st_id = student_data.get("id", -1)
        surname = student_data.get("surname", "")
        name = student_data.get("name", "")
        full_name = f"{lesson.group_name}_{surname}_{name}".lower()
        if lesson.students_ids.get(full_name) is None:
            lesson.students_ids[full_name] = set()
        lesson.students_ids[full_name].add(st_id)


def get_lessons(session: requests.Session, date: str) -> dict[str, LessonData]:
    lessons = create_lessons_data(session, date)
    add_students_info(session, lessons)
    return lessons


def read_attendance(filename: str) -> pd.DataFrame:
    return pd.read_csv(filename)


def convert_time_to_secs(time_str: str) -> int:
    result = 0
    multiplier = 1
    for val in time_str.strip().split(":")[::-1]:
        try:
            result += multiplier * int(val)
        except ValueError:
            pass
        multiplier *= 60
        if multiplier > 3600:
            # no days+
            break
    return result


def filter_attendance(attendance: pd.DataFrame) -> set:
    attendance["Имя"] = attendance["Имя"].str.lower().str.strip()
    checks = attendance["Подтверждений присутствия"].str.extract("(\\d+) / (\\d+)")[0].fillna("0").astype(np.int32)
    passed_checks = checks >= CHECKS_COUNT
    result_attendance = attendance[passed_checks]
    time_attendance = attendance[~passed_checks]
    time_attendance["Продолжительность"] = time_attendance["Продолжительность"].apply(convert_time_to_secs)
    summed_times = time_attendance.groupby("Имя")["Продолжительность"].sum()
    result_names = set()
    result_names.update(result_attendance["Имя"])
    result_names.update(summed_times[summed_times > MIN_TIME].index)
    return result_names


def get_attendance(filename: str) -> set:
    return filter_attendance(read_attendance(filename))


def main(cookies_filename: str, table_path: str, date: str):
    s = create_session(cookies_filename)
    lessons = get_lessons(s, date)
    attendance_names = get_attendance(table_path)
    for lesson in lessons.values():
        lesson.check_attendance(attendance_names)
        r = s.post(f"{BASE_URL}/lesson-instances", json=lesson.get_post_data())
        print(f"{lesson.group_name}: status code is {r.status_code}")


if __name__ == "__main__":
    args = parse_args()
    main(
        args["cookie"],
        args["table"],
        args["date"],
    )
