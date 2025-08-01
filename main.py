# encoding utf-8
import json
import copy
import time
import pandas as pd
import random

start_time = time.time()
src_path = "src/CourseList.json"
config_path = "config/config.json"


class Instruction:
    def __init__(self, week, day, time, loc):
        self.week: list[int] = week
        self.day: int = day
        self.time: list[int] = time
        self.loc: str = loc

    def display(self):
        print(self.week)
        print(self.day)
        print(self.time)
        print(self.loc)

    def is_conflicted(self, other) -> bool:
        other: Instruction
        ins1, ins2 = self, other
        co_week = list(set(ins1.week) & set(ins2.week))
        if len(co_week) == 0:
            return False
        if ins1.day != ins2.day:
            return False
        co_time = list(set(ins1.time) & set(ins2.time))
        if len(co_time) == 0:
            return False
        return True

    def __eq__(self, other):
        other: Instruction
        if self.week != other.week:
            return False
        if self.day != other.day:
            return False
        if self.time != other.time:
            return False
        return True


class Class:
    def __init__(self, name, code, teacher, score, instruction=None):
        self.name: str = name
        self.code: str = code
        self.teacher: str = teacher
        self.instruction: list[Instruction] = instruction
        self.score = score

    def display(self):
        print(self.name)
        print(self.code)
        print(self.teacher)

    def is_conflicted(self, other) -> bool:
        other: Class
        cls1, cls2 = self, other
        for ins1 in cls1.instruction:
            for ins2 in cls2.instruction:
                if ins1.is_conflicted(ins2):
                    return True
        return False

    def __eq__(self, other) -> bool:
        other: Class
        ins1 = self.instruction
        ins2 = other.instruction
        for i in ins1:
            for j in ins2:
                if ins2 == ins1:
                    break
            else:
                return False
        return True


class Course:
    def __init__(self, name, course_id, score, class_list=None):
        self.name: str = name
        self.id: str = course_id
        self.class_list: list[Class] = class_list
        self.score = score

    def display(self):
        print(self.name)
        print(self.id)

    def clean(self):
        if len(self.class_list) < 2:
            return
        cls_lst = [self.class_list[0]]
        for cls1 in self.class_list[1:]:
            for cls2 in cls_lst:
                if cls1 == cls2:
                    break
            else:
                cls_lst.append(cls1)
        self.class_list = cls_lst


num_to_day = {
    1: "Mon.",
    2: "Tue.",
    3: "Wed.",
    4: "Thu.",
    5: "Fri.",
    6: "Sat.",
    7: "Sun."
}


class Scheduler:
    def __init__(self, semester):
        self.semester: str = semester
        self.class_list: list[Class] = []
        self.score = 0

    def to_csv(self):
        df = pd.DataFrame(
            {
                "Index": range(1, 13 + 1),
                "Mon.": ["" for _ in range(13)],
                "Tue.": ["" for _ in range(13)],
                "Wed.": ["" for _ in range(13)],
                "Thu.": ["" for _ in range(13)],
                "Fri.": ["" for _ in range(13)],
                "Sat.": ["" for _ in range(13)],
                "Sun.": ["" for _ in range(13)]
            }
        )
        for cls in self.class_list:
            for ins in cls.instruction:
                for t in ins.time:
                    new_con = f"{cls.name}${cls.teacher}#第{ins.week[0]}-{ins.week[-1]}周@{ins.loc}|"
                    df.at[t - 1, num_to_day[ins.day]] += new_con
        df.to_csv(f"res/{self.semester}|{time.asctime(time.localtime(start_time))}.csv", index=False)

    def is_available(self, new_cls: Class) -> bool:
        for cls in self.class_list:
            if cls.is_conflicted(new_cls):
                return False
        return True

    def append(self, new_cls: Class):
        self.class_list.append(new_cls)
        self.score += new_cls.score


course_list = []
semester = ""
schedulers = []

if __name__ == "__main__":

    with open(src_path, "r") as f:
        f = json.load(f)
        semester = f["semester"]
        f = f["course_list"]
        for course in f:
            new_course = Course(course["name"], course["id"], course["score"])
            class_list = []
            for cls in course["class_list"]:
                new_cls = Class(course["name"] if cls["other_name"] == "" else cls["other_name"], cls["code"],
                                cls["teacher"],
                                course["score"])
                ins_list = []
                for ins in cls["instruction"]:
                    new_ins = Instruction(ins["week"], ins["day"], ins["time"], ins["location"])
                    ins_list.append(new_ins)
                new_cls.instruction = ins_list
                class_list.append(new_cls)
            new_course.class_list = class_list
            course_list.append(new_course)
        new_sch = Scheduler(semester)
        schedulers.append(new_sch)
    limit_score = sum([c.score for c in course_list])
    for cou in course_list:
        cou.clean()
    if len(schedulers) == 0:
        print("CourseList.json is empty!")
        exit()
    max_score = 0.0
    target = schedulers[0]
    with open(config_path, "r") as f:
        f = json.load(f)
        max_schedulers = f["max_schedulers"]
        rate = f["rate"]
    while len(course_list) > 0:
        if len(schedulers) > max_schedulers:
            schedulers = random.sample(schedulers, int(len(schedulers) ** rate))
        prev = copy.copy(schedulers)
        course = course_list.pop(0)
        limit_score -= course.score
        course.display()
        for sch in prev:
            if sch.score + limit_score < max_score:
                schedulers.remove(sch)
        prev = copy.deepcopy(schedulers)
        for cls in course.class_list:
            for sch in prev:
                if sch.is_available(cls):
                    new_sch = copy.deepcopy(sch)
                    new_sch.append(cls)
                    if new_sch.score > max_score:
                        max_score = new_sch.score
                        target = new_sch
                    schedulers.append(new_sch)
    print("最大学分：", max_score)
    target.to_csv()
    end_time = time.time()
    print(f"runtime:{round(end_time - start_time, 4)}s")
