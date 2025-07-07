import pytest
from query_engine import QueryEngine
from utils import str_to_number

def write_csv(tmp_path, content: str) -> str:
    path = tmp_path / "data.csv"
    path.write_text(content, encoding='utf-8')
    return str(path)

BASIC_CSV = """name,brand,price,rating
"""

EXT_CSV = BASIC_CSV + """
iphone 15 pro,apple,999,4.9
Galaxy S23 Ultra,samsung,1199,4.8
Redmi Note 12,xiaomi,199,4.6
Poco X5 Pro,xiaomi,299,4.4
OnePlus 11,oneplus,699,4.5
Nokia 3310,nokia,59,3.5
TestPhone,test,0,0.0
"""

@pytest.fixture
def engine_basic(tmp_path):
    csv_path = write_csv(tmp_path, EXT_CSV)
    return QueryEngine.from_csv(csv_path)

def test_filter_gt_numeric(engine_basic):
    filtered = engine_basic.filter("price>500")
    prices = sorted(str_to_number(r['price']) for r in filtered.rows)
    assert prices == [699, 999, 1199]

def test_filter_lt_numeric(engine_basic):
    filtered = engine_basic.filter("price<300")
    values = sorted(str_to_number(r['price']) for r in filtered.rows)
    assert values == [0, 59, 199, 299]

def test_filter_eq_zero_numeric(engine_basic):
    filtered = engine_basic.filter("price=0")
    assert len(filtered.rows) == 1
    assert filtered.rows[0]['name'] == 'TestPhone'

def test_filter_eq_string_case(engine_basic):
    # exact match, case-sensitive
    filtered = engine_basic.filter("brand=xiaomi")
    assert len(filtered.rows) == 2
    assert all(r['brand'] == 'xiaomi' for r in filtered.rows)
    # no match when case differs
    filtered2 = engine_basic.filter("brand=Samsung")
    assert len(filtered2.rows) == 0

def test_filter_gte_lte(engine_basic):
    ge = engine_basic.filter("rating>=4.8")
    le = engine_basic.filter("rating<=3.5")
    assert all(str_to_number(r['rating']) >= 4.8 for r in ge.rows)
    assert all(str_to_number(r['rating']) <= 3.5 for r in le.rows)

def test_order_by_asc(engine_basic):
    asc = engine_basic.order_by("price=asc")
    prices = [str_to_number(r['price']) for r in asc.rows]
    assert prices == sorted(prices)

def test_order_by_desc(engine_basic):
    desc = engine_basic.order_by("price=desc")
    prices = [str_to_number(r['price']) for r in desc.rows]
    assert prices == sorted(prices, reverse=True)

def test_distinct(engine_basic):
    distinct = engine_basic.distinct("brand")
    brands = [r['brand'] for r in distinct.rows]
    assert len(brands) == len(set(brands))
    assert set(brands) == set(r['brand'] for r in engine_basic.rows)

def test_limit_only(engine_basic):
    limited = engine_basic.limit_offset(limit=3)
    assert len(limited.rows) == 3

def test_offset_only(engine_basic):
    offsetted = engine_basic.limit_offset(offset=5)
    assert len(offsetted.rows) == len(engine_basic.rows) - 5

def test_limit_and_offset(engine_basic):
    subset = engine_basic.limit_offset(limit=2, offset=2)
    assert len(subset.rows) == 2
    assert subset.rows == engine_basic.rows[2:4]

# Aggregation tests
def test_aggregate_avg(engine_basic):
    result = engine_basic.aggregate("rating=avg")
    expected = sum(str_to_number(r['rating']) for r in engine_basic.rows) / len(engine_basic.rows)
    assert pytest.approx(result['avg'], rel=1e-3) == expected

def test_aggregate_min_max(engine_basic):
    mn = engine_basic.aggregate("price=min")
    mx = engine_basic.aggregate("price=max")
    assert mn['min'] == 0
    assert mx['max'] == 1199

def test_aggregate_empty(tmp_path):
    path = write_csv(tmp_path, BASIC_CSV)
    eng = QueryEngine.from_csv(path)
    with pytest.raises(ValueError):
        eng.aggregate("price=avg")

def test_invalid_where_syntax(engine_basic):
    with pytest.raises(ValueError):
        engine_basic.filter("invalid")

def test_invalid_order_by_syntax(engine_basic):
    with pytest.raises(ValueError):
        engine_basic.order_by("bad")

def test_invalid_aggregate_syntax(engine_basic):
    with pytest.raises(ValueError):
        engine_basic.aggregate("price=median")

def test_missing_column(engine_basic):
    with pytest.raises(ValueError):
        engine_basic.filter("nope>1")
    with pytest.raises(ValueError):
        engine_basic.order_by("nope=asc")
    with pytest.raises(ValueError):
        engine_basic.distinct("nope")
