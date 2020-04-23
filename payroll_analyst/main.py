import requests
import numpy
import os
from dotenv import load_dotenv
from itertools import count
from terminaltables import AsciiTable


LANGUAGES = ['Java', 'JavaScript', 'Python', 'PHP', 'C#', 'C++']
SUPERJOB_TOKEN = os.getenv('SUPERJOB_TOKEN')


def get_number_of_vacancies_hh(language):
    """Получаем количество найденных вакансий по региону"""
    params = {
        'text': 'Программист {}'.format(language),
        'area': '1',
        'period': '30',
    }

    response = requests.get('https://api.hh.ru/vacancies/', params=params)
    response.raise_for_status()

    number_of_vacancies = response.json()['found']
    return number_of_vacancies


def get_vacancies_hh(language):
    """Получаем вакансии"""
    vacancies_all = {}
    vacancies_all['items'] = []
    for page in count(0):
        params = {
            'text': 'Программист {}'.format(language),
            'area': '1',
            'period': '30',
            'only_with_salary': True,
            'page': page
        }

        response = requests.get('https://api.hh.ru/vacancies/', params=params)
        response.raise_for_status()

        vacancies = response.json()
        if page >= vacancies['pages']:
            break
        vacancies_all['items'] += vacancies['items']

    return vacancies_all['items']


def predict_rub_salary_hh(vacancy):
    """Получаем среднюю зарплату вакансии c HH"""
    payment_from = vacancy['salary']['from']
    payment_to = vacancy['salary']['to']
    currency = vacancy['salary']['currency']

    if currency != 'RUR':
        return None
    else:
        return predict_salary(payment_from, payment_to)


def predict_rub_salary_sj(vacancy):
    """Получаем среднюю зарплату вакансии с SuperJob"""
    payment_from = int(vacancy['payment_from'])
    payment_to = int(vacancy['payment_to'])
    currency = vacancy['currency']

    if currency != 'rub':
        return None
    else:
        return predict_salary(payment_from, payment_to)


def predict_salary(salary_from, salary_to):
    """Расчитываем среднюю зарплату"""
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_to:
        return salary_to * 0.8
    elif salary_from:
        return salary_from * 1.2
    else:
        return None


def get_vacancies_sj(language):
    """Получаем список вакансий"""
    headers = {
        'X-Api-App-Id': SUPERJOB_TOKEN,
    }
    params = {
        'keyword': 'Программист {}'.format(language),
        'town': 'Москва'
    }
    response = requests.get('https://api.superjob.ru/2.20/vacancies/', headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def create_table(result, title):
    """Создаём таблицу с данными"""
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for row in result:
        data = []
        data.append(str(row))
        data.append(result[row]['vacancies_found'])
        data.append(result[row]['vacancies_processed'])
        data.append(result[row]['average_salary'])
        table_data.append(data)

    table_instance = AsciiTable(table_data, title)
    return table_instance.table


def main():
    load_dotenv()
    result_hh = {}
    result_sj = {}
    for language in LANGUAGES:
        result_hh[language] = {}
        result_sj[language] = {}
        try:
            result_hh[language]['vacancies_found'] = get_number_of_vacancies_hh(language)
            result_sj[language]['vacancies_found'] = get_vacancies_sj(language)['total']

            vacancies_hh = get_vacancies_hh(language)
            salaries_hh = []

            for vacancy in vacancies_hh:
                salary = predict_rub_salary_hh(vacancy)
                if salary != None: salaries_hh.append(salary)

            vacancies_sj = get_vacancies_sj(language)
            salaries_sj = []

            for vacancy in vacancies_sj['objects']:
                salary = predict_rub_salary_sj(vacancy)
                if salary: salaries_sj.append(salary)

            result_hh[language]['vacancies_processed'] = len(salaries_hh)
            result_hh[language]['average_salary'] = int(numpy.mean(salaries_hh))

            result_sj[language]['vacancies_processed'] = len(salaries_sj)
            result_sj[language]['average_salary'] = int(numpy.mean(salaries_sj))

        except requests.exceptions.HTTPError:
            print('Произошла ошибка, проверьте запрос')

    print(create_table(result_hh, 'HeadHunter Moscow'))
    print(create_table(result_sj, 'SuperJob Moscow'))


if __name__ == '__main__':
    main()
