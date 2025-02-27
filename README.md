# Конвертер кассовых файлов из формата Пилот во Фронтол
Учетная система Домино 7.8 
Кассовая программа Фронтол 6 

## Оглавление

0. [Цель проекта](#Цель-проекта)
1. [Номера касс](#Номера-касс)
2. [Установка и запуск](#Установка-и-запуск)
3. [TODO](#TODO)


## Цель проекта 
Внешний обработчик файлов для кассы из формата Пилот в формат Фронтол

Цель проекта - конвертировать файлы из формата Пилот в формат Фронтол
Для каждой кассы существует своя папка в директории w:/MAIL/FOR_KAS/
по ее номеру, например w:/MAIL/FOR_KAS/**1**
сделать w:/MAIL/FOR_KAS/**1_FRONTOL** и конвертированные файлы складывать туда
из директории-источника сконвертированное удалять

Учетная система Домино 7.8 ведет обмен с кассами по формату Пилот 
(см. руководство интегратора) Передача товаров на кассу производится через меню
"Передать товар на кассу" из реестра переоценки / справочника
При попытке интеграции с Фронтол 6 поддерживаемый формат обмена 
имеет следующие ограничения:

- Формат устарел и похоже что не поддерживается со стороны Фронтол
- В формате «PILOT» автоматическая загрузка данных невозможна. 
- Отсутствует поле для ставки НДС
- Отсутствует поле признака маркированного товара
- Кастомные поля ломают обмен

Преимущества использования конвертера:
- Обратная совместимость с уже существующими кассами, можно работать паралленьно
на старых и новых
- Гибкость, можно не дорабатывать выгрузку в Домино, настройки менять в скрипте 


[:arrow_up:Оглавление](#Оглавление)


## Номера касс

1. Касса1 живая Домино
2. Касса2 резерв тестовая Фронтол
3. Касса3 резерв
4. Касса4 живая Домино
5. Касса5 резерв
6. Касса6 живая Домино
7. Касса7 обмен с прайсчекером

## Установка и запуск

- На машине должен быть установлен Python 3.13
- domino_frontol_for_kas_converter.py сам скрипт
    - в скрипте поправить пути для каждой кассы
    - пути к сетевм папкам абсолютные
    - создать директории куда конвертировать и для логов для каждой кассы
- frontol_converter_run.bat  
    - для каждой кассы свой, поправить пути для каждой кассы
    - запускать планировщиком раз в минуту
    - чтобы окно терминала запускалось в скрытом режиме:
        - выбрать опцию "Run whether user is logged on or not" 
        - установить опцию "Hidden" в настройках задачи
    - если надо чаще, смотрим в сторону библиотеки schedule

## TODO

- [ ] Тестирование
    - [X] Загрузка - обычный товар 
    - [X] Загрузка - маркированный товар
    - [X] Загрузка - мерный товар 
    - [X] Загрузка - коэффициент штрихкода целый
    - [-] Загрузка - коэффициент штрихкода дробный Домино не поддерживает
    - [X] Удаление штрихкода из карточки  
    - [х] Зарузка всей базы (нужен контроль)
- [Х] Весь товар грузится как мерный, разобраться с флагами 
- [X] Запуск каждую минуту по шедулеру     
- [ ] Прогрузить дисконтные карты
- [X] Режим удаления штрихкодов
- [ ] Снятие касс
    - [ ] бьет со склада CT поле 6 должно быть 4
         или заставить фронтол в 4ку или менять процедуру акцепта в Домино
    - [ ] Бьется ли возврат? C поле 5 CT поле 11
    - [ ] Скидки показвает? C поле 9
    - [ ] Нал/безнал?  CM поле 6
- [ ] Процесс ломается на кривых штрихкодах вида код 350935 06000229868146E+25
    прогружается только половина файла и зависает в вечном цикле
    симптомы - из папки источника файл не удаляется, вылезло на всей базе
- [ ] Подумать про мониторинг
- [ ] Контроль задвоенных штрихкодов