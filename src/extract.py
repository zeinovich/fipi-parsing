import os
import requests
import json
import urllib3
# from tqdm import tqdm

from .constants import (
    QUANTITY_PAGES,
    URL_PAGES,
    NAME_FOR_ID,
    ATTRS_ID,
    NAME_FOR_BLOCK,
    ATTRS_BLOCK,
    NAME_FOR_CONDITION,
    ATTRS_CONDITION,
)
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def html_page_processing():

    for button_number in range(0, QUANTITY_PAGES + 1):
        print(f"Page {button_number}/{QUANTITY_PAGES}")
        url_page = URL_PAGES + str(button_number)

        getting_data_from_html(
            url_page
        )  # Формируем url на конкретную страничку и отправляем в обработчик


def getting_data_from_html(url_page):
    request = requests.get(url_page, verify=False)
    soup = BeautifulSoup(request.text, "html.parser")

    list_id = list()
    list_task = list()
    for id_number in soup.find_all(NAME_FOR_ID, ATTRS_ID):  # id
        for string_id_number in id_number.strings:  # Получаем список id на странице
            list_id.append(string_id_number)

    for block in soup.find_all(
        NAME_FOR_BLOCK, ATTRS_BLOCK
    ):  # Обращаемся к конкретному заданию
        string = ""  # Сюда будем записывать текст задания

        for response_condition in block.find_all(
            NAME_FOR_CONDITION, ATTRS_CONDITION
        ):  # Условие записи ответа(верхнее)
            for string_response_condition in response_condition.strings:
                string += string_response_condition + "\n"

                # Тут идёт вся обработка
                for task in block.find_all("p"):  # Само задание
                    input_string = list(task.strings)

                    output_string = list()
                    for i in range(len(input_string)):
                        input_string[i] = input_string[i].replace(
                            "\xa0", ""
                        )  # избавляемся от лишних пробелов
                        input_string[i] = input_string[i].replace(
                            "-", "- "
                        )  # решаем проблемы "приклеивания" тире к словам

                        if input_string[i] != " ":
                            output_string.append(input_string[i])

                    try:
                        if output_string[0] != "":
                            result_string = "".join(output_string)

                            string += result_string + "\n"
                    except Exception as ex:
                        print(ex)

            list_task.append(string)  # Тут получаем список из заданий

    if os.path.isfile(
        "data.json"
    ):  # Проверка на существование файла. Создаст в случае отсутствия.
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        for lid, ltask in zip(list_id, list_task):
            data.append({"id": lid, "task": ltask, "answer": "", "tags": []})

        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )
    else:
        with open("data.json", "w", encoding="utf-8") as file:
            file.write(str([]))


if __name__ == "__main__":
    html_page_processing()
