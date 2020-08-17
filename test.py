from datetime import datetime


def format_date(input_date, personal_number):
    if not personal_number:
        input_date = f"20{input_date}"
    elif personal_number[0] == '3' or personal_number[0] == '4':
        input_date = f"19{input_date}"
    elif personal_number[0] == '5' or personal_number[0] == '6':
        input_date = f"20{input_date}"
    return datetime.strptime(input_date, '%Y%m%d').strftime('%Y-%m-%d')

a = format_date('190122', '32')
print(a)
b = format_date('190122', '52')
print(b)
c = format_date('190122', None)
print(c)


