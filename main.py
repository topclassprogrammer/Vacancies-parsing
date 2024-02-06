import json

import bs4
import fake_headers
import requests


def gen_headers():
    """Генерируем фейковые заголовки для GET запроса"""
    headers_gen = fake_headers.Headers(os="win", browser="chrome")
    return headers_gen.generate()


def del_unicode_chars(str_):
    """Удаляем Unicode символы на html странице в строках содержащие пробелы"""
    unicode_chars = ['\u202f', '\xa0']
    for char in unicode_chars:
        str_ = str_.replace(char, ' ')
    return str_


def find_vacancies():
    """Находим div тэги, содержащие записи о вакансиях"""
    URL = 'https://spb.hh.ru/search/vacancy'
    params = {'text': 'pyton django flask', 'area': (1, 2), 'page': 0}
    html_data = requests.get(URL, params=params, headers=gen_headers())
    response = html_data.text
    html_parser = bs4.BeautifulSoup(response, "lxml")
    vacancies = html_parser.find_all('div', class_='serp-item')
    return vacancies


def parse_vacancies():
    """Парсим каждый div тэг содержащий ссылку, зарплату, компанию и город"""
    result = {}
    for vacancy in vacancies:
        link = vacancy.find('a', class_='bloko-link')['href']

        salary = vacancy.find('span', class_='bloko-header-section-2')
        if salary:
            salary = salary.text
        else:
            salary = 'ЗП не указана'

        company = vacancy.find('a', class_=('bloko-link '
                                            'bloko-link_kind-tertiary'))
        if salary:
            company = company.text
        else:
            company = 'Город не указан'

        city = vacancy.find('div', attrs={'data-qa':
                            'vacancy-serp__vacancy-address'},
                            class_='bloko-text')
        if city:
            city = city.text
        else:
            city = 'Город не указан'

        non_unicode_list = []
        for item in [link, salary, company, city]:
            non_unicode_list.append(del_unicode_chars(item))
        for link, salary, company, city in [non_unicode_list]:
            result.setdefault(link, [salary, company, city])
    return result


def write_json(file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)


if __name__ == '__main__':
    vacancies = find_vacancies()
    result = parse_vacancies()
    write_json('vacancies.json')
