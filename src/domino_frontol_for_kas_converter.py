import os
import sys
import shutil
import logging
import datetime


def parse_line(line):
    try:
        parts = line.split(",")
        data = {}
        for part in parts:
            key, value = part.split("=", 1)
            data[key.strip()] = value.strip()
        return data
    except ValueError as e:
        logging.error(f"Ошибка при разборе строки: {line} - {e}")
        return None
    except Exception as e:
        logging.error(f"Неожиданная ошибка при разборе строки: {line} - {e}")
        return None


def process_delete_mode(line, outfile):
    """
    Режим удаления штрихкодов с касс
    """
    data = parse_line(line)
    if data is None:
        logging.error(f"Не удалось разобрать строку: {line}")
        return  # Прекращаем обработку этой строки
    output_fields = [""] * 2
    output_fields[0] = data.get("CODE", "")
    output_fields[1] = data.get("BC", "")
    output_line = ";".join(output_fields) + "\n"
    outfile.write(output_line)


def process_tmc_mode(line, outfile):
    """
    Режим передачи товара на кассу
    """
    data = parse_line(line)
    if data is None:
        logging.error(f"Не удалось разобрать строку: {line}")
        return  # Прекращаем обработку этой строки

    # QUANT передается только целым, может округлиться в ноль
    # Чтобы с настройками локали не танцевать
    data["PRICE"] = data.get("PRICE", "").replace(".", ",")

    output_fields = [""] * 67  # Формируем пустой список из 67 полей
    output_fields[0] = data.get("CODE", "")  # 1
    output_fields[1] = data.get("BC", "")  # 2
    output_fields[2] = data.get("NAME", "")  # 3
    output_fields[3] = data.get("NAME", "")  # 4
    output_fields[4] = data.get("PRICE", "")  # 5
    # 08 Флаги через запятую: 1й флаг – дробное количество
    output_fields[7] = "1" if data.get("MEASURE", "") == "2" else "0"
    output_fields[12] = "1"  # 13 Признак предмета расчета = товар на всё
    output_fields[13] = data.get("QUANT", "")  # 14 Коэфф штрихкода
    output_fields[22] = "3"  # 23 код налоговой группы 20%
    # 52 Маркировка: флаг «Разрешить регистрацию без штрихкода маркировки» 1 = yes
    output_fields[51] = "1" if data.get("BMODE", "") == "0" else "0"
    output_fields[54] = data.get("BMODE", "")  # 55 Маркировка: тип номенклатуры
    # 66 Для мерного метр
    output_fields[65] = "6" if data.get("MEASURE", "") == "2" else "0"

    output_line = ";".join(output_fields) + "\n"
    outfile.write(output_line)


def convert_file(input_filename, output_filename):
    """
    Преобразует файл.  Возвращает True при успехе, False при неудаче.
    Обрабатывает исключения UnicodeDecodeError и общие исключения.
    формат файла на входе
    OBJ=TMC,CMD=MOD,CODE=332332,BC=2900003323329,VCODE=1,PTYPE=0,PRICE=1.00,
        DEPT=0,NAME=!!!ТЕСТ КАССЫ БЕЗ ЧЗ!!! ТЕСТОВЫЙ ТОВАР,
        MEASURE=2,QUANT=1,QMODE=15,BMODE=11

    в домино функция выглядит так
    Печать 'OBJ=TMC,CMD=MOD,CODE='&ТоварКод&',BC='&ТоварПродажныйКод&',
        VCODE='&КодВалюты&',PTYPE='&КодЦены&',PRICE='&ТоварЦена&',
        DEPT='&DEPT &',NAME='&ТоварИмя& ',MEASURE='&ПризнакВесовой&',
        QUANT='&количество_по_умолчанию&',QMODE=15,
        BMODE='&(ПризнакМаркированный ? 7 : '3') поз 1,1 формат 'S255';

    BMODE= доработано, нумерация соответствует фронтолу

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
                    process_delete_mode(line, outfile)
                # загрузка товара на кассы
                elif line.startswith("OBJ=TMC"):
                    process_tmc_mode(line, outfile)

        logging.info(f"Файл успешно обработан: {input_filename}")
        return True

    except UnicodeDecodeError as e:
        logging.error(f"Ошибка декодирования файла: {input_filename} - {e}")
        return False
    except Exception as e:
        logging.error(f"Ошибка при обработке файла: {input_filename} - {e}")
        return False


def check_old_format(input_filename):
    """
    Проверяет, содержит ли файл строки с BMODE=3 (старый формат).
    Возвращает True, если найден старый формат, иначе False.
    """
    try:
        with open(input_filename, "r", encoding="cp866") as infile:
            for line in infile:
                if "BMODE=3" in line:
                    return True
        return False
    except Exception as e:
        logging.error(
            f"Ошибка при проверке файла на старый формат: {input_filename} " f" - {e}"
        )
        return True  # Если не смогли проверить - считаем проблемным


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
    Проверяет, есть ли в input_dir хотя бы один файл, начинающийся с '$'
    или с расширением .txt
    Возвращает True, если такие файлы есть, False в противном случае.
    """
    for filename in os.listdir(input_dir):
        if filename.startswith("$") or filename.lower().endswith(".txt"):
            return True
    logging.info(f"В папке {input_dir} нет подходящих файлов для обработки")
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
    # Проверка на существование директорий
    try:
        ensure_directories_exist(input_dir, output_dir, log_dir)
    except FileNotFoundError as e:
        print(f"Отсутствуют директории: {e}", file=sys.stderr)
        sys.exit(1)  # Прекращаем выполнение, скрипт вернет код ошибки
        # return  # Прекращаем выполнение, если директории не существуют

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
        logging.info(f"Нет файлов для обработки в {input_dir}  Прекращаем выполнение")
        return  # Прекращаем выполнение, если файлов для обработки не существуют

    try:
        for filename in os.listdir(input_dir):
            input_path = os.path.join(input_dir, filename)
            # Если это файл переоценки
            if filename.startswith("$"):
                # Проверяем старый формат отдельной функцией
                if check_old_format(input_path):
                    # Переименовываем файл с добавлением "!"
                    new_name = "!" + filename
                    new_path = os.path.join(input_dir, new_name)
                    try:
                        os.rename(input_path, new_path)
                        logging.warning(
                            f"Файл с ошибкой старого формата переименован: "
                            f"{input_path} -> {new_path}"
                        )
                    except Exception as e:
                        logging.error(
                            f"Не удалось переименовать файл с ошибкой: "
                            f"{input_path} - {e}"
                        )
                    continue  # Переходим к следующему файлу

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
            # Остальные файлы с расширением .txt пробрасываем не изменяя
            elif filename.lower().endswith(".txt"):
                output_path = os.path.join(output_dir, filename)
                try:
                    shutil.move(input_path, output_path)
                    logging.info(f"Файл перемещен: {output_path}")
                except Exception as e:
                    logging.error(
                        f"Ошибка перемещения: {input_path} -> {output_path} - {e}"
                    )

        # Создаем файл-флаг после обработки всех файлов
        if not create_flag_file(output_dir):
            logging.error(f"Не удалось создать файл-флаг в {output_dir}")
        else:
            logging.info(f"Файл-флаг успешно создан в {output_dir}")

    except Exception as e:
        logging.error(f"Общая ошибка при обработке директории: {e}")


if __name__ == "__main__":
    # Обязательно

    # Желательно
    # TODO переделать чтобы запускать как службу Windows (pywin32/NSSM)
    # TODO логи в одну строку компактнее сделать
    # TODO контроль за размером логов, удалять все, что старше 30 дней?
    # TODO контроль за размером входной папки фронтола,
    # TODO удалять обработанные файлы (2я строка = @) старше 30 дней?
    # Это все можно на отдельный скрипт повесить и запускать раз в сутки например
    """
    Этот скрипт забирает файлы с ценами формата Пилот из сетевой папки кассы,
    преобразует их в формат Атол и кладет в локальную папку.
    Обработанные файлы удаляются из директории источника.
    Файлы в формате Атол с расширением .txt пробрасываются из папки источника
    в папку приемник без конвертации.

    Применение:
    В текущей конфигурации для передачи товара на кассу Домино задействует
    директорию //server/Domino/MAIL/FOR_KAS где для каждой кассы своя
    дочерняя директория соответствующая её номеру. Задейстуем на каждую
    фронтол-кассу одну такую директорию как источник.

    Для загрузки на кассу используем канал обмена формат Атол
    Для выгрузки оставляем стандартный канал обмена формат Пилот

    Скрипт должен запускаться планировщиком раз в минуту

    Используй абсолютне пути, W/MAIL работает плохо и не всегда,
    планировщик при запуске BAT файла не видит её в частности
    //server/Domino лучше, если не работает, то по статическому айпи

    Пути задаются в файлах:
        frontol_converter_run.bat
            запускает этот скрипт
        frontol_extractor.bat
            отправляет кассовый отчет на сетевую папку
            запускается средствами фронтола при выходе в ОС

    Создай директории INPUT_DIR OUTPUT_DIR LOG_DIR вручную.

    Например, для кассы 2 (FOR_KAS/2) создаются директории:
    - `FOR_KAS/2_FRONTOL`
    - `FOR_KAS/2_CONVERT_LOG`

    Описание работы:
    Скрипт сканирует `input_directory` на наличие файлов, начинающихся с `$`,
    которые создаются АСТУ при передаче товара на кассу в формате "Пилот".
    При наличии таких файлов в `output_directory` создаются конвертированные
    файлы в формате "Атол" с расширением .txt и файл-флаг автозагрузки
    `ready_to_load.flag`. В "настройки/системные/обмен данными" фронтола
    в явном виде в задании на вкладке формат указваем файл обмена по маске *.txt
    и файл-флаг.

    Обработанные файлы удаляются из директории источника

    Добавлен прямой проброс файлов в формате Атол из папки источника в
    папку приемник без конвертации. Название файла не должно начинаеться с $
    и должно иметь расширение .txt. Для удобства управления скидками.

    При обработке конвертированных файлов `FrontolService` заменяет во
    второй строке признак `#` на `@` для обработанных, сам флаг удаляется.

    добавлена проверка на соответствие новому формату файла, т.к. вылез риск
    при случайной выгрузке всей базы в старом формате (где BMODE=3 лекарственные
    препараты, у нас таких нет) положить кассы (весь товар маркированный будет)
    """

    if len(sys.argv) < 4:
        print(
            "Ошибка: недостаточно аргументов. Нужно 3 параметра: "
            "input_dir, output_dir, log_dir",
            file=sys.stderr,
        )
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    log_directory = sys.argv[3]

    process_directory(input_directory, output_directory, log_directory)
