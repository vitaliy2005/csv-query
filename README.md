# csv-query

Простой скрипт для фильтрации, агрегации, сортировки, paging и distinct CSV.

## Установка

```bash
pip install tabulate
```

## Примеры

```bash
python3 main.py -f products.csv
python3 main.py -f products.csv -w "rating>4.7"
python3 main.py -f products.csv -a "rating=avg"
python3 main.py -f products.csv -w "brand=xiaomi" -a "rating=min"
python3 main.py -f products.csv --distinct brand
python3 main.py -f products.csv --order-by "price=desc"
python3 main.py -f products.csv --limit 5 --offset 10
```

## Тесты

```bash
pip install pytest pytest-cov
pytest --cov=.
```
