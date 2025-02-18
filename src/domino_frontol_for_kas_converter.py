import os
import logging
import datetime


def convert_file(input_filename, output_filename):
    """
    Преобразует файл.  Возвращает True при успехе, False при неудаче.
    Обрабатывает исключения UnicodeDecodeError и общие исключения.
    формат на входе
    OBJ=TMC,CMD=MOD,CODE=332332,BC=2900003323329,VCODE=1,PTYPE=0,PRICE=1.00,DEPT=0,NAME=!!!ТЕСТ КАССЫ БЕЗ ЧЗ!!! ТЕСТОВЫЙ ТОВАР,MEASURE=2,QUANT=1,QMODE=15,BMODE=3
        Печать 'OBJ=TMC,CMD=MOD,CODE='&ТоварКод&',BC='&ТоварПродажныйКод&',VCODE='&КодВалюты&',
        PTYPE='&КодЦены&',PRICE='&ТоварЦена&',DEPT='&DEPT &',NAME='&ТоварИмя& ',
        MEASURE='&ПризнакВесовой&',QUANT='&количество_по_умолчанию&',QMODE=15,BMODE='&(ПризнакМаркированный ? 7 : '3') поз 1,1 формат 'S255';
    на выходе целые числа ждут в кавычках
    """
    try:
        with open(input_filename, "r", encoding="cp866") as infile, open(
            output_filename, "w", encoding="windows-1251"
        ) as outfile:

            # Записываем строки в начало файла
            outfile.write("##@@&&\n")
            outfile.write("#\n")
            outfile.write("$$$ADDQUANTITY\n")

            for line in infile:
                line = line.strip()
                if line.startswith("OBJ=TMC"):
                    parts = line.split(",")
                    data = {}
                    for part in parts:
                        key, value = part.split("=", 1)
                        data[key.strip()] = value.strip()

                    # заменяем точку на запятую в строке PRICE чтобы с настройками локали не танцевать
                    data["PRICE"] = data.get("PRICE", "").replace(".", ",")
                    # заменяем 3 на 0 для не маркированного товара 7 как у нас - иная маркированная продукция
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


def ensure_directories_exist(input_dir, output_dir):
    """
    Проверяет существование входной и выходной директорий.
    Вызывает FileNotFoundError, если директория не существует.
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Входная папка не существует: {input_dir}")

    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Выходная папка не существует: {output_dir}")


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
    Создает файл-флаг "in.f" в output_dir, если он не существует.
    """
    flag_file_path = os.path.join(output_dir, "in.f")
    if not os.path.exists(flag_file_path):
        try:
            with open(flag_file_path, "w") as f:
                pass  # Просто создаем пустой файл
            logging.info(f"Создан файл-флаг: {flag_file_path}")
        except Exception as e:
            logging.error(f"Не удалось создать файл-флаг: {flag_file_path} - {e}")
            return False
    return True


def process_directory(input_dir, output_dir):
    """
    Обрабатывает файлы, начинающиеся с '$', в указанной папке.
    Обрабатывает исключения на уровне директории и отдельных файлов.
    """
    # Настраиваем логирование
    log_dir = "c:/Users/A.Pinevich/YandexDisk/Ньюмарк Домашний Фронтол Кассы/FOR_KAS/CONVERT_LOG"
    os.makedirs(log_dir, exist_ok=True)  # Создаем директорию для логов, если ее нет
    log_file = os.path.join(
        log_dir, f"convert_log_kassa2_{datetime.date.today().strftime('%Y-%m-%d')}.log"
    )
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    try:
        ensure_directories_exist(input_dir, output_dir)
    except FileNotFoundError as e:
        logging.error(f"Ошибка: {e}")
        return  # Прекращаем выполнение, если директории не существуют

    if not ensure_files_exist(input_dir):
        logging.warning(
            f"Нет файлов для обработки в {input_dir}.  Прекращаем выполнение."
        )
        return

    if not create_flag_file(output_dir):
        logging.error(
            f"Не удалось создать файл-флаг в {output_dir}.  Прекращаем выполнение."
        )
        return

    try:

        for filename in os.listdir(input_dir):
            if filename.startswith("$"):
                input_path = os.path.join(input_dir, filename)
                output_filename = filename + ".txt"
                output_path = os.path.join(output_dir, output_filename)

                logging.info(f"Обрабатываем файл: {input_path}")
                if convert_file(input_path, output_path):
                    logging.info(f"Файл обработан и сохранен: {output_path}")
                else:
                    logging.error(f"Ошибка при обработке файла: {input_path}")

    except Exception as e:
        logging.error(f"Общая ошибка при обработке директории: {e}")


if __name__ == "__main__":
    # TODO удаление обрадотанных файлов из input_directory
    # TODO удаление обрадотанных файлов из output_directory ?
    # TODO 8е поле флаги, разобраться с ними, что должно быть
    # TODO удаление штрихкодов по CMD=DEL
    input_directory = "c:/Users/A.Pinevich/YandexDisk/Ньюмарк Домашний Фронтол Кассы/FOR_KAS/2"  # Замените на имя вашей входной папки
    output_directory = "c:/Users/A.Pinevich/YandexDisk/Ньюмарк Домашний Фронтол Кассы/FOR_KAS/2_FRONTOL"  # Замените на имя вашей выходной папки

    process_directory(input_directory, output_directory)
    print("Обработка завершена.")
