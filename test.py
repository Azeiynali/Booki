# from itertools import zip_longest

# l1 = ["1", "4", 7]
# l2 = [2, 5, 8, "م"]
# l3 = [3, 6, 9, 11, 12]

# # ترکیب تمام لیست‌ها به صورت پاره‌ای
# combined_list = [item for sublist in zip_longest(l1, l2, l3) for item in sublist if item is not None]

# # چاپ لیست ترکیب شده
# print(combined_list)

from datetime import datetime

def format_age_output(date):
    now = datetime.now()
    age = now.year - date.year

    if now.month < date.month or (now.month == date.month and now.day < date.day):
        age -= 1

    return age
    if not age:
        return "به تازگی"
    elif age < 1:
        return f"{int(age*12)} ماه پیش"
    elif age < 12:
        return f"{age} سال پیش"
    elif age < 48:
        return f"{int(age/12)} سال و {age % 12} ماه پیش"
    else:
        return f"{int(age/48)} سال و {int((age % 48)/12)} سال پیش"
