import re
from datetime import datetime
import unidecode


# remove < symbols if they are left in the string part
def replace(string):
    return string.replace('<', '')


# change date format into yyyy-mm-dd, turn into string
def format_date(input_date, personal_number):
    if not personal_number:
        input_date = f"20{input_date}"
    elif personal_number[0] == '3' or personal_number[0] == '4':
        input_date = f"19{input_date}"
    elif personal_number[0] == '5' or personal_number[0] == '6':
        input_date = f"20{input_date}"
    return datetime.strptime(input_date, '%Y%m%d').strftime('%Y-%m-%d')


def mrz_extract(text):
    # some symbols are read incorrectly: remove all newlines and spaces, change some (two that were encountered) into <
    text = text.replace('\n', '')
    text = text.replace(' ', '')
    text = text.replace('\u304f', '<')
    text = text.replace('\u3001', '<')

    # take only relevant part of the string
    pattern = re.compile(r'([A-Z])([A-Z0-9<])([A-Z]{3})([A-Z<]{1,39})([A-Z0-9<]{1,9})([O0-9])([A-Z]{3})([0-9]{6})([0-9])([MF<])([0-9]{6})([0-9])([A-Z0-9<]{14})([0-9])([0-9])')
    regex_result = pattern.search(text).group()

    # some < symbols were missing, made sure that string is 88 characters long
    while len(regex_result) < 88:
        pattern_2 = re.compile(r'[0-9]{1}')
        regex_result_2 = pattern_2.search(text).group()
        x = regex_result.find(f"{regex_result_2}")
        regex_result = regex_result[:x] + "<" + regex_result[x:]

    # organize string into meaningful data parts
    personal_number = regex_result[72:86]
    personal_number = replace(personal_number)

    country = regex_result[2:5]

    surname_name = regex_result[5:44]
    surname_name = surname_name.split('<')
    surname = surname_name[0]
    # person can have multiple names, possibly only first one is relevant
    names = surname_name[2]

    pass_number = regex_result[44:53]
    pass_number = replace(pass_number)

    nationality = regex_result[54:57]

    birth = regex_result[57:63]
    birth_date = format_date(birth, personal_number)

    sex = regex_result[64:65]
    if sex == 'F':
        sex = 'Female'
    elif sex == 'M':
        sex = 'Male'
    else:
        sex = 'Unspecified'

    pass_expiration = regex_result[65:71]
    pass_expiration_date = format_date(pass_expiration, None)

    return {
        'personal_number': personal_number,
        'country_code': country,
        'surname': surname,
        'name': names,
        'pass_number': pass_number,
        'nationality': nationality,
        'birth_date': birth_date,
        'sex': sex,
        'pass_expiration_date': pass_expiration_date
    }


def compare(manual, photo):
    # To compare names/surnames, transform all letters to lowercases, and switch accented letters to regular ones
    manual = unidecode.unidecode(manual).lower()
    photo = photo.lower()
    if manual != photo:
        return False
    return True
