from typing import List, Dict, Any, Callable
import operator
from utils import str_to_number

class QueryEngine:
    def __init__(self, headers: List[str], rows: List[Dict[str, Any]]):
        self.headers = headers
        self.rows = rows

    @classmethod
    def from_csv(cls, path: str) -> 'QueryEngine':
        import csv
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            rows = [dict(row) for row in reader]
        return cls(headers, rows)

    def filter(self, expr: str) -> 'QueryEngine':
        for op in ('>=', '<=', '>', '<', '='):
            if op in expr:
                col, raw = expr.split(op, 1)
                col = col.strip(); raw = raw.strip()
                break
        else:
            raise ValueError(f"Неправильный формат where: {expr}")

        ops_map = {'>': operator.gt, '<': operator.lt,
                   '>=': operator.ge, '<=': operator.le, '=': operator.eq}
        cmp_fn: Callable = ops_map[op]

        def matches(row):
            lhs = row.get(col)
            if lhs is None:
                raise ValueError(f"Колонка `{col}` не найдена")
            try:
                return cmp_fn(str_to_number(lhs), str_to_number(raw))
            except ValueError:
                return cmp_fn(lhs, raw)

        filtered = [r for r in self.rows if matches(r)]
        return QueryEngine(self.headers, filtered)

    def order_by(self, expr: str) -> 'QueryEngine':
        if '=' not in expr:
            raise ValueError(f"Неправильный формат order-by: {expr}")
        col, direction = expr.split('=', 1)
        col = col.strip(); direction = direction.strip().lower()
        if col not in self.headers:
            raise ValueError(f"Колонка `{col}` не найдена")
        rev = True if direction == 'desc' else False
        def key_fn(row):
            v = row[col]
            try:
                return str_to_number(v)
            except ValueError:
                return v
        sorted_rows = sorted(self.rows, key=key_fn, reverse=rev)
        return QueryEngine(self.headers, sorted_rows)

    def distinct(self, column: str) -> 'QueryEngine':
        if column not in self.headers:
            raise ValueError(f"Колонка `{column}` не найдена")
        seen = set()
        unique = []
        for r in self.rows:
            val = r[column]
            if val not in seen:
                seen.add(val)
                unique.append(r)
        return QueryEngine(self.headers, unique)

    def limit_offset(self, limit: int = None, offset: int = 0) -> 'QueryEngine':
        start = offset or 0
        end = start + limit if (limit is not None) else None
        sliced = self.rows[start:end]
        return QueryEngine(self.headers, sliced)

    def aggregate(self, expr: str) -> Dict[str, float]:
        col, agg_name = expr.split('=', 1)
        col = col.strip(); agg_name = agg_name.strip().lower()
        values = [str_to_number(r[col]) for r in self.rows]
        if not values:
            raise ValueError("Нет данных для агрегации")
        if agg_name == 'avg':
            return {'avg': sum(values) / len(values)}
        if agg_name == 'min':
            return {'min': min(values)}
        if agg_name == 'max':
            return {'max': max(values)}
        raise ValueError(f"Неизвестная функция агрегации: {agg_name}")
