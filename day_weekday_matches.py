#!/usr/bin/env python3

import calendar
import json
import sys


def ask_yes_or_no(question: str):
    accepted_answers = ("y", "yes", "Yes", "YES", "Y", "n", "no", "No", "NO", "N")
    if not question.endswith(": "):
        question += ": "

    ret = input(question)
    opportunities = 2
    while ret not in accepted_answers and opportunities > 0:
        print("NOOOOOOOO! You gave a wrong answer! How hard can it be??")
        print(f"Hint: accepted ansers: {accepted_answers}")
        ret = input("Go for the good one!: ")
        opportunities -= 1

    if ret not in accepted_answers:
        print("Three attempts and no right response! Come again please :)")
        sys.exit(1)

    ret = ret.lower()
    if ret.startswith("y"):
        return True

    return False


def get_months_starting_same_weekday(day_offsets):
    rep_patterns = {}
    weekday_map = {}

    def get_months_by_type_of_year(leap=False):
        ret = {}
        month_map = {}
        day_offsets[1] = day_offsets[1] if not leap else day_offsets[1] + 1
        for idx, month in enumerate(calendar.month_name[1:]):
            months_starting_same_day = []
            for i in range(idx + 1, 12):
                if sum(day_offsets[idx:i]) % 7 == 0:
                    months_starting_same_day.append(calendar.month_name[i + 1])

            exists_group = False
            for k, v in ret.items():
                if month in v:
                    ret[k] += months_starting_same_day
                    ret[k] = list(set(ret[k]))
                    exists_group = True
                    break

            if not exists_group:
                ret[month] = months_starting_same_day

        for k, v in ret.items():
            if v:
                month_map[list(calendar.month_name).index(k)] = [
                    list(calendar.month_name).index(i) for i in v
                ]
                for i in v:
                    month_map[list(calendar.month_name).index(i)] = [
                        list(calendar.month_name).index(k) for k in v if k != i
                    ] + [list(calendar.month_name).index(k)]

        info = [[k] + v for k, v in ret.items() if v]
        return info, month_map

    rep_patterns["Regular Year"], weekday_map["Regular Year"] = get_months_by_type_of_year()
    rep_patterns["Leap Year"], weekday_map["Leap Year"] = get_months_by_type_of_year(True)

    print("--------------Groups of months starting on the same weekday--------------")
    print(json.dumps(rep_patterns, indent=4, separators=(",", ":")))

    return weekday_map


def get_repetitions(day, weekday, month_mapping, day_offsets):
    # Weekdays are 0 to 6, months 1 to 12
    # Day offsets array indices are 0 to 11
    first_appearence = {}

    def get_first_appearence(leap=False):
        day_offsets[1] = day_offsets[1] if not leap else day_offsets[1] + 1
        large_months = [1, 3, 5, 7, 8, 10, 12]
        first_month = {}
        for idx, _ in enumerate(calendar.day_name):
            # First check January
            calculated_weekday = idx + day % 7 - 1
            for month in range(1, 13):
                if calculated_weekday == weekday:
                    if day > 29 and month == 2:
                        continue

                    if day == 29 and month == 2 and not leap:
                        continue

                    if day == 31 and month not in large_months:
                        continue

                    first_month[idx] = month
                    break

                # Add offset
                calculated_weekday = calculated_weekday + day_offsets[month - 1]
                # Manage overflow
                calculated_weekday = (
                    calculated_weekday if calculated_weekday < 7 else (calculated_weekday % 7)
                )

        return first_month

    first_appearence["Regular Year"] = get_first_appearence()
    first_appearence["Leap Year"] = get_first_appearence(True)
    print(f"------Number of times the combination {calendar.day_name[weekday]}-{day} occurs...------")
    combinations = {"Regular Year": {}, "Leap Year": {}}
    for year, first_month in first_appearence.items():
        for wday, month in first_month.items():
            reps = [month] + month_mapping[year].get(month, [])
            reps = [calendar.month_name[i] for i in reps]
            combinations[year][
                f"when Jan 1st falls on {calendar.day_name[wday]}"
            ] = f"{len(reps)} time/s. In {', '.join(reps)}"

    print(json.dumps(combinations, indent=4))


def main():
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_offsets = list(map(lambda x: x - 28, month_lengths))
    month_weekday_mapping = {}

    print("Hi, some general facts first!")
    month_weekday_mapping = get_months_starting_same_weekday(day_offsets[:])
    if not ask_yes_or_no(
        "Do you want to see how many times a day of the month falls on the same weekday over a year?"
    ):
        print("Have a nice day then!")
        sys.exit(0)

    check = True
    while check:
        day = input("What day do you want to check?: ")
        while not day.isnumeric() or int(day) not in range(1, 32):
            day = input("Sorry, days in a month go from 1 to 31. Please try again: ")

        day = int(day)

        weekday = input("What weekday should the day fall on in different months? ").lower()
        while weekday not in list(map(str.lower, list(calendar.day_name))):
            weekday = input(
                f"Sorry, weekday shall one of the following: {list(calendar.day_name)}. Please try again: "
            )

        # Convert name to idx
        weekday = list(map(str.lower, list(calendar.day_name))).index(weekday)

        get_repetitions(day, weekday, month_weekday_mapping, day_offsets[:])

        check = ask_yes_or_no("Do you want to check other day/weekday combination?")

    print("Have a nice day!")


if __name__ == "__main__":
    main()
