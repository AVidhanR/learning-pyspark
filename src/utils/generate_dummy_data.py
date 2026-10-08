"""
Generates a deliberately messy e-commerce dataset for a pandas cleaning project.

Creates three CSVs in ./data:
  customers.csv  ~1,000 rows
  products.csv   ~200 rows
  orders.csv     ~20,000 rows

Uses only the Python standard library. Run:  python generate_messy_data.py
Change SEED to get a different (but reproducible) dataset.
"""
import csv
import os
import random
from datetime import date, timedelta

SEED = 42
N_CUSTOMERS, N_PRODUCTS, N_ORDERS = 1000, 200, 20000
random.seed(SEED)
os.makedirs("data", exist_ok=True)

NULLS = ["", "N/A", "null", "-", "NaN", "none"]
FIRST = ["James", "Mary", "Wei", "Priya", "Carlos", "Fatima", "Liam", "Sofia",
         "Kenji", "Amara", "Noah", "Olivia", "Arjun", "Elena", "Omar", "Grace"]
LAST = ["Smith", "Garcia", "Chen", "Patel", "Kim", "Nguyen", "Okafor", "Silva",
        "Muller", "Rossi", "Khan", "Brown", "Ivanova", "Tanaka", "Lopez", "Dubois"]
COUNTRIES = {
    "United States": ["United States", "USA", "U.S.", "us", "United States of America"],
    "United Kingdom": ["United Kingdom", "UK", "U.K.", "england", "Great Britain"],
    "Germany": ["Germany", "DE", "germany", "Deutschland"],
    "India": ["India", "IN", "india ", "Bharat"],
    "Canada": ["Canada", "CA", "canada"],
}
CATEGORIES = ["Electronics", "Home & Kitchen", "Books", "Toys", "Sports", "Beauty"]
STATUSES = ["delivered", "Delivered", "DELIVERED ", "shipped", "Shipped",
            "cancelled", "canceled", "Cancelled", "returned", "pending", "Pending"]
TAGS = ["gift", "prime", "sale", "bulk", "first_order", "mobile", "coupon"]


def maybe_null(value, rate):
    return random.choice(NULLS) if random.random() < rate else value


def messy_case(s):
    r = random.random()
    if r < 0.15:
        return s.upper()
    if r < 0.30:
        return s.lower()
    if r < 0.40:
        return f"  {s} "
    return s


def messy_date(d):
    fmts = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%Y/%m/%d", "%b %d %Y", "%Y%m%d"]
    weights = [60, 10, 10, 8, 7, 5]
    return d.strftime(random.choices(fmts, weights)[0])


def messy_money(x):
    r = random.random()
    if r < 0.6:
        return f"{x:.2f}"
    if r < 0.8:
        return f"${x:,.2f}"
    if r < 0.9:
        return f"{x:,.2f} USD"
    return str(round(x))


# ---------- customers ----------
customers = []
for cid in range(1, N_CUSTOMERS + 1):
    first, last = random.choice(FIRST), random.choice(LAST)
    canon = random.choice(list(COUNTRIES))
    email = f"{first}.{last}{cid}@example.com".lower()
    signup = date(2019, 1, 1) + timedelta(days=random.randint(0, 1800))
    age = random.randint(18, 80)
    if random.random() < 0.02:
        age = random.choice([-1, 0, 150, 999])          # impossible ages
    customers.append({
        "customer_id": cid,
        "full_name": messy_case(f"{first} {last}"),
        "email": maybe_null(messy_case(email), 0.04),
        "country": random.choice(COUNTRIES[canon]),
        "signup_date": maybe_null(messy_date(signup), 0.03),
        "age": maybe_null(age, 0.05),
    })
# duplicate customers: same person re-registered with a new id and different casing
for _ in range(40):
    dup = dict(random.choice(customers))
    dup["customer_id"] = len(customers) + 1
    if dup["email"] not in NULLS:
        dup["email"] = dup["email"].strip().upper()
    customers.append(dup)

# ---------- products ----------
products = []
for pid in range(1, N_PRODUCTS + 1):
    cat = random.choice(CATEGORIES)
    price = round(random.uniform(3, 900), 2)
    products.append({
        "product_id": f"P{pid:04d}",
        "product_name": f"{cat.split()[0]} item {pid}",
        "category": maybe_null(messy_case(cat), 0.03),
        "unit_price": messy_money(price),
        "_true_price": price,                              # used internally, not written
    })

# ---------- orders ----------
orders = []
start = date(2023, 1, 1)
for oid in range(1, N_ORDERS + 1):
    cust = random.choice(customers)
    prod = random.choice(products)
    qty = random.choices([1, 2, 3, 4, 5, 10], [50, 20, 12, 8, 6, 4])[0]
    r = random.random()
    if r < 0.01:
        qty = -qty                                         # negative quantities
    elif r < 0.015:
        qty = 0
    discount = random.choice([0, 0, 0, 0.05, 0.1, 0.15, 0.2])
    if random.random() < 0.005:
        discount = random.choice([1.5, -0.1, 50])          # invalid discounts
    price = prod["_true_price"]
    if random.random() < 0.003:
        price *= 1000                                      # price outliers
    total = qty * price * (1 - discount)
    od = start + timedelta(days=random.randint(0, 600), seconds=random.randint(0, 86399))
    ship_days = random.randint(1, 10)
    if random.random() < 0.01:
        ship_days = -random.randint(1, 5)                  # shipped before ordered
    tags = ";".join(random.sample(TAGS, random.randint(0, 3)))
    pid = prod["product_id"]
    if random.random() < 0.01:
        pid = f"P{random.randint(900, 999):04d}"           # orphan product ids
    orders.append({
        "order_id": f"ORD-{oid:06d}",
        "customer_id": maybe_null(cust["customer_id"], 0.01),
        "product_id": maybe_null(pid.lower() if random.random() < 0.05 else pid, 0.01),
        "order_date": messy_date(od),
        "ship_date": maybe_null(messy_date(od + timedelta(days=ship_days)), 0.08),
        "quantity": qty,
        "discount": discount,
        "order_total": maybe_null(messy_money(total), 0.02),
        "status": random.choice(STATUSES),
        "tags": tags,
    })
# exact duplicates (double-loaded rows) and near-duplicates (same order, re-exported)
orders += random.sample(orders, 300)
for o in random.sample(orders, 100):
    nd = dict(o)
    nd["status"] = messy_case(nd["status"])
    orders.append(nd)
random.shuffle(orders)


def write(name, rows, drop=()):
    fields = [k for k in rows[0] if k not in drop]
    with open(os.path.join("data", name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote data/{name}: {len(rows):,} rows")


write("customers.csv", customers)
write("products.csv", products, drop=("_true_price",))
write("orders.csv", orders)
print("Done. Do not open the generator code again until you've finished profiling!")