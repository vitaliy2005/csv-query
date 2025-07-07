#!/usr/bin/env python3
import argparse
import sys
from tabulate import tabulate
from query_engine import QueryEngine

def parse_args():
    parser = argparse.ArgumentParser(
        description="CSV processor: фильтрация, агрегация, сортировка, paging и distinct."
    )
    parser.add_argument('--file', '-f', required=True, help='Путь к CSV-файлу')
    parser.add_argument('--where', '-w', metavar='"column>value"', help='Условие фильтрации')
    parser.add_argument('--aggregate', '-a', metavar='"column=agg"', help='Агрегация: avg|min|max')
    parser.add_argument('--order-by', metavar='"column=asc|desc"', help='Сортировка результата, напр. price=desc')
    parser.add_argument('--limit', type=int, help='Ограничить число строк вывода')
    parser.add_argument('--offset', type=int, default=0, help='Смещение для paging')
    parser.add_argument('--distinct', metavar='column', help='Уникальные значения по колонке')
    return parser.parse_args()

def main():
    args = parse_args()
    try:
        engine = QueryEngine.from_csv(args.file)

        if args.where:
            engine = engine.filter(args.where)

        if args.distinct:
            engine = engine.distinct(args.distinct)

        if args.order_by:
            engine = engine.order_by(args.order_by)

        if args.offset or args.limit is not None:
            engine = engine.limit_offset(limit=args.limit, offset=args.offset)

        if args.aggregate:
            result = engine.aggregate(args.aggregate)
            table = [[key, value] for key, value in result.items()]
            print(tabulate(table, headers=['aggregate', 'value'], tablefmt='github'))
        else:
            rows = [[row[h] for h in engine.headers] for row in engine.rows]
            print(tabulate(rows, headers=engine.headers, tablefmt='github'))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
