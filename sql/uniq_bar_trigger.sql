-- !!! требует тестирования
-- речь про триггер к таблице BARCODE

-- вариант 1
-- создать отдельный, контроль "RDB$TRIGGER_SEQUENCE" чтобы новый после был
-- в dbeaver выделить все и запустить
CREATE TRIGGER UNIQUE_BARCODE_CHECK
FOR BARCODE
BEFORE INSERT OR UPDATE
AS
DECLARE VARIABLE OLD_ID INTEGER;
BEGIN
  SELECT FIRST 1 ID FROM BARCODE
    WHERE BARCODE = NEW.BARCODE
      AND WAREID <> NEW.WAREID
      AND (DELETED IS NULL OR DELETED = 0)
    INTO :OLD_ID;
  IF (OLD_ID IS NOT NULL) THEN
  BEGIN
    UPDATE BARCODE SET DELETED = 1 WHERE ID = :OLD_ID;
  END
END

-- посмотреть порядок
SELECT rdb$trigger_name, rdb$trigger_type, rdb$trigger_sequence, rdb$trigger_inactive 
FROM rdb$triggers
WHERE rdb$relation_name = 'BARCODE';

-- изменить порядок выполнения
UPDATE RDB$TRIGGERS
SET RDB$TRIGGER_SEQUENCE = 1
WHERE RDB$TRIGGER_NAME = 'UNIQUE_BARCODE_CHECK';


-- вариант 2
-- в версии 2.1.7 CREATE OR ALTER TRIGGER не поддерживается
-- сначала удалить старый триггер командой:
DROP TRIGGER CHNG_BEF_BARCODE;

-- Создать триггер заново командой:
CREATE TRIGGER CHNG_BEF_BARCODE
FOR BARCODE
BEFORE INSERT OR UPDATE
AS
DECLARE VARIABLE OLD_ID INTEGER;
BEGIN
  -- Логическое удаление дубликата штрихкода
  SELECT FIRST 1 ID FROM BARCODE
    WHERE BARCODE = NEW.BARCODE
      AND WAREID <> NEW.WAREID
      AND (DELETED IS NULL OR DELETED = 0)
    INTO :OLD_ID;

  IF (OLD_ID IS NOT NULL) THEN
  BEGIN
    -- DELETE FROM BARCODE WHERE ID = :OLD_ID; -- совсем удалить
    UPDATE BARCODE SET DELETED = 1 WHERE ID = :OLD_ID; -- пометить как удаленный
  END

  NEW.INSCHNG = OLD.INSCHNG;

  IF ((NEW.CHNG > 0) OR (NEW.CHNG IS NULL)) THEN
  BEGIN
    NEW.CHNG = GEN_ID(GCHNG, 1);
    IF (OLD.INSCHNG IS NULL) THEN
      NEW.INSCHNG = NEW.CHNG;
  END

  IF (NEW.BDOCODE < 0) THEN
    NEW.BDOCODE = -NEW.BDOCODE;
  ELSE
    SELECT FIRST 1 DBIDENT FROM CUSTOMDB INTO NEW.BDOCODE;
END
