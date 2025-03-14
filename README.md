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
из директории-источника, сконвертированное удалять

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

[:arrow_up:Оглавление](#Оглавление)

## Установка и запуск

- На машине должен быть установлен Python 3.13
    - проверить: python --version  
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

[:arrow_up:Оглавление](#Оглавление)

## TODO

- [ ] Тестирование загрузка
    - [X] Загрузка - обычный товар 
    - [X] Загрузка - маркированный товар
    - [X] Загрузка - мерный товар 
    - [X] Загрузка - коэффициент штрихкода целый
    - [O] Загрузка - коэффициент штрихкода дробный Домино не отдаёт такие
    - [X] Удаление штрихкода из карточки  
    - [X] Зарузка всей базы
    - [ ] Дисконтные карты пакетом

- [ ] Тестирование регистрация
    - [X] Пробить обычный товар
    - [X] Вернуть обычный товар
    - [X] Пробить мерный товар
    - [ ] Вернуть мерный товар
    - [X] Пробить обычный товар как мерный - ждем ошибку
    - [ ] Вернуть старый товар по свободной цене (только ответственный)
    - [ ] Пробить маркированный товар
    - [ ] Пробить маркированный товар повторно - ждем ошибку    
    - [ ] Вернуть маркированный товар
    - [ ] Вернуть маркированный товар повторно - ждем ошибку
    - [ ] Автономный режим Пробить маркированный товар
    - [ ] Автономный режим Пробить маркированный товар повторно - ждем ошибку    
    - [ ] Автономный режим Вернуть маркированный товар
    - [ ] Автономный режим Вернуть маркированный товар повторно - ждем ошибку

- [X] Тестирование снятие касс
    - [X] бьет со склада CT поле 6 должно быть 4
         или заставить фронтол в 4ку или менять процедуру акцепта в Домино
         отшито в Домино, будет списывать всегда с 4го подразделения
    - [X] Бьется ли возврат? C поле 5 CT поле 11
    - [X] Скидки показвает? C поле 9 Номер карты обрезает фронтол, 
          номер карты показывает только в секции С, 
          8 знаков сначала видно, значащие 5 в конце отрезаны
    - [O] Нал/безнал?  CM поле 6 Не чинится, это код валюты, 
          по Пилотовскому формату Фронтол не отдаст как нам надо
    - [ ] Проверить, не попадает ли этот код валюты в проводки какие          

- [ ] Доработки
    - [X] Весь товар грузится как мерный, разобраться с флагами 
    - [X] Запуск каждую минуту по шедулеру     
    - [X] Режим удаления штрихкодов
    - [X] Процесс ломается на кривых штрихкодах вида 
          код 350935 06000229868146E+25
          прогружается только половина файла и зависает в вечном цикле
          симптомы - из папки источника файл не удаляется, вылезло на всей базе
    - [X] Разобраться как грузить дисконтные карты вручную
    - [ ] Очистить резервные папки от накопленного   
    - [ ] Перенос настроек БД с кассы на кассу как?       
    - [ ] Пофиксить работу фронтола с путями до сетевой папки Домино   

- [ ] Доработки 2й этап   
    - [ ] Подумать про мониторинг
    - [ ] Разобраться как грузить дисконтные карты пакетом
    - [ ] Контроль задвоенных штрихкодов на кассе, как? Firebird допилить?
    - [ ] Контроль размера папок лога и обработанных файлов Фронтола    

[:arrow_up:Оглавление](#Оглавление)