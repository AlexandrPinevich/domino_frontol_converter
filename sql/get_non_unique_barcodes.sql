-- this will select non unique barcodes
SELECT s.Code, b.Barcode, b.CHNG, b.INSCHNG, b.DELETED
FROM BarCode b
JOIN SprT s ON s.ID = b.WareID
WHERE b.Barcode IN (
    SELECT Barcode
    FROM BarCode
    GROUP BY Barcode
    HAVING COUNT(*) > 1
)
ORDER BY b.Barcode, b.CHNG
;