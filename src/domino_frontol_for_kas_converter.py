import os
import logging
import datetime


def parse_line(line):
    parts = line.split(",")
    data = {}
    for part in parts:
        key, value = part.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def convert_file(input_filename, output_filename):
    """
    Преобразует файл.  Возвращает True при успехе, False при неудаче.
    Обрабатывает исключения UnicodeDecodeError и общие исключения.
    формат файла на входе
    OBJ=TMC,CMD=MOD,CODE=332332,BC=2900003323329,VCODE=1,PTYPE=0,PRICE=1.00,
        DEPT=0,NAME=!!!ТЕСТ КАССЫ БЕЗ ЧЗ!!! ТЕСТОВЫЙ ТОВАР,
        MEASURE=2,QUANT=1,QMODE=15,BMODE=3

    в домино функция выглядит так
    Печать 'OBJ=TMC,CMD=MOD,CODE='&ТоварКод&',BC='&ТоварПродажныйКод&',
        VCODE='&КодВалюты&',PTYPE='&КодЦены&',PRICE='&ТоварЦена&',
        DEPT='&DEPT &',NAME='&ТоварИмя& ',MEASURE='&ПризнакВесовой&',
        QUANT='&количество_по_умолчанию&',QMODE=15,
        BMODE='&(ПризнакМаркированный ? 7 : '3') поз 1,1 формат 'S255';

    на выходе числа ждут в кавычках
    """
    try:
        with open(input_filename, "r", encoding="cp866") as infile, open(
            output_filename, "w", encoding="windows-1251"
        ) as outfile:

            # Записываем строки в начало файла
            outfile.write("##@@&&\n")
            outfile.write("#\n")
            outfile.write("$$$ADDQUANTITY\n")

            # Поднимем флаг для обработки запроса на удаление штрихкодов
            del_mode_flag = False

            for line in infile:
                line = line.strip()
                # удаление штрихкожов
                if line.startswith("OBJ=TMC,CMD=DEL"):
                    # команда на удаление, один раз, одну строку
                    # если удалять, то весь файл на удаление придет
                    if not del_mode_flag:
                        outfile.write("$$$DELETEBARCODESBYWARECODE\n")
                        del_mode_flag = True

                    data = parse_line(line)
                    output_fields = [""] * 2  # Формируем пустой список из 2 полей
                    output_fields[0] = data.get("CODE", "")  # 1
                    output_fields[1] = data.get("BC", "")  # 2

                    output_line = ";".join(output_fields) + "\n"
                    outfile.write(output_line)
                # загрузка товара на кассы
                elif line.startswith("OBJ=TMC"):
                    data = parse_line(line)
                    # заменяем точку на запятую в строках PRICE и QUANT
                    # чтобы с настройками локали не танцевать
                    data["PRICE"] = data.get("PRICE", "").replace(".", ",")
                    data["QUANT"] = data.get("QUANT", "").replace(".", ",")
                    # заменяем 3 на 0 для не маркированного товара
                    # 7 как у нас - иная маркированная продукция
                    data["BMODE"] = data.get("BMODE", "").replace("3", "0")

                    output_fields = [""] * 67  # Формируем пустой список из 67 полей
                    output_fields[0] = data.get("CODE", "")  # 1
                    output_fields[1] = data.get("BC", "")  # 2
                    output_fields[2] = data.get("NAME", "")  # 3
                    output_fields[4] = data.get("PRICE", "")  # 5
                    output_fields[13] = data.get("QUANT", "")  # 14 Коэфф штрихкода
                    output_fields[22] = "3"  # 23 код налоговой группы 20%
                    # 52 Маркировка флаг для маркированного запрет
                    output_fields[51] = "0" if data.get("BMODE", "") == "7" else "1"
                    output_fields[54] = data.get("BMODE", "")  # 55 Маркировка
                    # 66 Для мерного метр
                    output_fields[65] = "6" if data.get("MEASURE", "") == "2" else "0"

                    output_line = ";".join(output_fields) + "\n"
                    outfile.write(output_line)

        logging.info(f"Файл успешно обработан: {input_filename}")
        return True

    except UnicodeDecodeError as e:
        logging.error(f"Ошибка декодирования файла: {input_filename} - {e}")
        return False
    except Exception as e:
        logging.error(f"Ошибка при обработке файла: {input_filename} - {e}")
        return False


def ensure_directories_exist(input_dir, output_dir, log_dir):
    """
    Проверяет существование директорий.
    Вызывает FileNotFoundError, если директория не существует.
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Входная папка не существует: {input_dir}")

    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Выходная папка не существует: {output_dir}")

    if not os.path.exists(log_dir):
        raise FileNotFoundError(f"Лог директория не существует: {log_dir}")


def ensure_files_exist(input_dir):
    """
    Проверяет, есть ли в input_dir хотя бы один файл, начинающийся с '$'.
    Возвращает True, если такие файлы есть, False в противном случае.
    """
    for filename in os.listdir(input_dir):
        if filename.startswith("$"):
            return True
    logging.warning(f"В папке {input_dir} нет файлов, начинающихся с '$'")
    return False


def create_flag_file(output_dir):
    """
    Создает файл-флаг "ready_to_load.flag" в output_dir, если он не существует.
    """
    flag_file_path = os.path.join(output_dir, "ready_to_load.flag")
    if not os.path.exists(flag_file_path):
        try:
            with open(flag_file_path, "w") as f:
                pass  # Просто создаем пустой файл
            logging.info(f"Создан файл-флаг: {flag_file_path}")
        except Exception as e:
            logging.error(f"Не удалось создать файл-флаг: {flag_file_path} - {e}")
            return False
    return True


def process_directory(input_dir, output_dir, log_dir):
    """
    Обрабатывает файлы, начинающиеся с '$', в указанной папке.
    Обрабатывает исключения на уровне директории и отдельных файлов.
    """
    # Проверка на суещствование директорий
    try:
        ensure_directories_exist(input_dir, output_dir, log_dir)
    except FileNotFoundError as e:
        logging.error(f"Ошибка: {e}")
        return  # Прекращаем выполнение, если директории не существуют

    # Настраиваем логирование
    log_file = os.path.join(
        log_dir, f"convert_{datetime.date.today().strftime('%Y-%m-%d')}.log"
    )
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if not ensure_files_exist(input_dir):
        # вот это нам лог не забьет с концами?
        logging.warning(
            f"Нет файлов для обработки в {input_dir}.  Прекращаем выполнение."
        )
        return  # Прекращаем выполнение, если файлов для обработки не существуют

    try:

        for filename in os.listdir(input_dir):
            if filename.startswith("$"):
                input_path = os.path.join(input_dir, filename)
                output_filename = filename + ".txt"
                output_path = os.path.join(output_dir, output_filename)

                logging.info(f"Обрабатываем файл: {input_path}")
                if convert_file(input_path, output_path):
                    logging.info(f"Файл обработан и сохранен: {output_path}")
                    try:
                        os.remove(input_path)
                        logging.info(f"Удален исходный файл: {input_path}")
                    except Exception as e:
                        logging.error(
                            f"Не удалось удалить исходный файл: {input_path} - {e}"
                        )
                else:
                    logging.error(f"Ошибка при обработке файла: {input_path}")

        # Создаем файл-флаг после обработки всех файлов
        if not create_flag_file(output_dir):
            logging.error(f"Не удалось создать файл-флаг в {output_dir}.")
        else:
            logging.info(f"Файл-флаг успешно создан в {output_dir}.")

    except Exception as e:
        logging.error(f"Общая ошибка при обработке директории: {e}")


if __name__ == "__main__":
    # TODO 8е поле флаги, разобраться с ними, что должно быть
    # TODO Оттестировать что все работает как надо
    # TODO Убрать конечный принт после отладки?

    # Желательно
    # TODO контроль за размером логов, удалять все, что старше 30 дней?
    # TODO контроль за размером входной папки фронтола,
    # TODO удалять обработанные файлы (2я строка = @) старше 30 дней?
    # Это все можно на отдельный скрипт повесить и запускать раз в сутки например
    """
    Применение:
    1. Измените путь в переменной `base_path`.
    2. Измените `for_kas_dir`, если используется другая.
    3. Укажите номер кассы в переменной `input_dir_name`.
    4. Необходимо создать директории вручную, так как автоматическое создание
    может быть опасным. При необходимости можно раскомментировать os.makedirs()
    для создания директорий. Логика требует доработки в таком случае. Проверка
    на наличие input_directory как минимум

    Для кассы 2 (FOR_KAS/2) создаются директории:
    - `FOR_KAS/2_FRONTOL`
    - `FOR_KAS/2_CONVERT_LOG`

    Описание работы:
    Скрипт сканирует `input_directory` на наличие файлов, начинающихся с `$`,
    которые создаются АСТУ при передаче товара на кассу в формате "Пилот".
    При наличии таких файлов в `output_directory` создается файл-флаг
    `ready_to_load.flag` и сами конвертированные файлы в формате "Атол".

    При обработке таких файлов `FrontolService` заменяет во второй строке
    признак `#` на `@` для обработанных, сам флаг удаляется.
    """

    # base_input_path = "w:/MAIL"
    base_input_path = "//server/Domino/MAIL"
    base_output_path = "c:/Users/A.Pinevich/YandexDisk/domino_frontol_converter/data"
    for_kas_dir = "FOR_KAS"
    input_dir_name = "2"
    output_dir_name = f"{input_dir_name}_FRONTOL"
    log_dir_name = f"{input_dir_name}_CONVERT_LOG"

    input_directory = f"{base_input_path}/{for_kas_dir}/{input_dir_name}"
    output_directory = f"{base_output_path}/{for_kas_dir}/{output_dir_name}"
    log_directory = f"{base_output_path}/{for_kas_dir}/{log_dir_name}"

    # Создаем директории для логов и выходных файлов, если их нет
    # os.makedirs(log_directory, exist_ok=True)
    # os.makedirs(output_directory, exist_ok=True)

    process_directory(input_directory, output_directory, log_directory)
    # print("Обработка завершена.")
