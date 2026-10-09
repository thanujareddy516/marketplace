# ============================================
#   SMART VENDOR MARKETPLACE SYSTEM
#   test_logic.py - Unit Tests (Simple Style)
# ============================================

from logic import (
    validate_vendor_name,
    validate_license,
    validate_product_name,
    validate_original_price,
    validate_selling_price,
    validate_stock,
    validate_quantity,
    check_stock,
    calculate_bill,
    calculate_profit,
    validate_return,
    generate_report_data,
    vendor_exists,
    generate_order_id
)

# ============================================
# TEST 1 - Validate Vendor Name
# ============================================

def test_vendor_name_valid():
    ok, msg = validate_vendor_name("Ramu")
    assert ok == True

def test_vendor_name_empty():
    ok, msg = validate_vendor_name("")
    assert ok == False

def test_vendor_name_with_digits():
    ok, msg = validate_vendor_name("Ramu123")
    assert ok == False

def test_vendor_name_with_symbols():
    ok, msg = validate_vendor_name("Ramu@")
    assert ok == False

def test_vendor_name_digits_only():
    ok, msg = validate_vendor_name("123")
    assert ok == False

# ============================================
# TEST 2 - Validate License Number
# ============================================

def test_license_valid():
    ok, msg = validate_license("12345")
    assert ok == True

def test_license_empty():
    ok, msg = validate_license("")
    assert ok == False

def test_license_with_letters():
    ok, msg = validate_license("LIC001")
    assert ok == False

def test_license_with_symbols():
    ok, msg = validate_license("123@45")
    assert ok == False

# ============================================
# TEST 3 - Validate Product Name
# ============================================

def test_product_name_valid():
    ok, msg = validate_product_name("Apple")
    assert ok == True

def test_product_name_empty():
    ok, msg = validate_product_name("")
    assert ok == False

def test_product_name_with_digits():
    ok, msg = validate_product_name("Apple1")
    assert ok == False

def test_product_name_digits_only():
    ok, msg = validate_product_name("123")
    assert ok == False

# ============================================
# TEST 4 - Validate Original Price
# ============================================

def test_original_price_valid():
    ok, val = validate_original_price("100")
    assert ok == True
    assert val == 100.0

def test_original_price_zero():
    ok, msg = validate_original_price("0")
    assert ok == False

def test_original_price_negative():
    ok, msg = validate_original_price("-50")
    assert ok == False

def test_original_price_non_number():
    ok, msg = validate_original_price("abc")
    assert ok == False

# ============================================
# TEST 5 - Validate Selling Price
# ============================================

def test_selling_price_valid():
    ok, val = validate_selling_price("150", 100)
    assert ok == True
    assert val == 150.0

def test_selling_price_equal_to_original():
    ok, msg = validate_selling_price("100", 100)
    assert ok == False

def test_selling_price_less_than_original():
    ok, msg = validate_selling_price("80", 100)
    assert ok == False

def test_selling_price_non_number():
    ok, msg = validate_selling_price("abc", 100)
    assert ok == False

# ============================================
# TEST 6 - Validate Stock
# ============================================

def test_stock_valid():
    ok, val = validate_stock("10")
    assert ok == True
    assert val == 10

def test_stock_zero():
    ok, msg = validate_stock("0")
    assert ok == False

def test_stock_negative():
    ok, msg = validate_stock("-5")
    assert ok == False

def test_stock_non_number():
    ok, msg = validate_stock("abc")
    assert ok == False

# ============================================
# TEST 7 - Validate Quantity
# ============================================

def test_quantity_valid():
    ok, val = validate_quantity("3")
    assert ok == True
    assert val == 3

def test_quantity_zero():
    ok, msg = validate_quantity("0")
    assert ok == False

def test_quantity_negative():
    ok, msg = validate_quantity("-1")
    assert ok == False

def test_quantity_non_number():
    ok, msg = validate_quantity("abc")
    assert ok == False

# ============================================
# TEST 8 - Check Stock
# ============================================

products_sample = {
    "Apple": {"vendor": "Ramu", "orig": 20, "sell": 30, "stock": 5}
}

def test_check_stock_sufficient():
    ok, qty = check_stock(products_sample, "Apple", 3)
    assert ok == True
    assert qty == 3

def test_check_stock_product_not_found():
    ok, msg = check_stock(products_sample, "Mango", 1)
    assert ok == False

def test_check_stock_out_of_stock():
    p = {"Apple": {"vendor": "Ramu", "orig": 20, "sell": 30, "stock": 0}}
    ok, msg = check_stock(p, "Apple", 1)
    assert ok == False

def test_check_stock_exceeds_available():
    ok, msg = check_stock(products_sample, "Apple", 10)
    assert ok == False

# ============================================
# TEST 9 - Calculate Bill (FREE_DELIVERY = 500)
# ============================================

products_bill = {
    "Apple": {"vendor": "Ramu", "orig": 20, "sell": 100, "stock": 10}
}

def test_bill_with_delivery_charge():
    # subtotal = 100 * 2 = 200 < 500, delivery = 50
    subtotal, handling, delivery, total = calculate_bill(products_bill, "Apple", 2)
    assert subtotal == 200
    assert handling == 20.0
    assert delivery == 50
    assert total == 270.0

def test_bill_free_delivery():
    # subtotal = 100 * 5 = 500 >= 500, delivery = FREE
    subtotal, handling, delivery, total = calculate_bill(products_bill, "Apple", 5)
    assert subtotal == 500
    assert handling == 50.0
    assert delivery == 0
    assert total == 550.0

def test_handling_is_10_percent():
    subtotal, handling, delivery, total = calculate_bill(products_bill, "Apple", 1)
    assert handling == round(subtotal * 0.10, 2)

# ============================================
# TEST 10 - Calculate Profit
# ============================================

products_profit = {
    "Apple": {"vendor": "Ramu", "orig": 20, "sell": 30, "stock": 10}
}

def test_profit_multiple_units():
    profit = calculate_profit(products_profit, "Apple", 3)
    assert profit == 30.0  # (30-20) * 3

def test_profit_single_unit():
    profit = calculate_profit(products_profit, "Apple", 1)
    assert profit == 10.0  # (30-20) * 1

# ============================================
# TEST 11 - Validate Return
# ============================================

orders_sample = {
    "ORD-001": {"status": "Delivered", "subtotal": 200},
    "ORD-002": {"status": "Returned",  "subtotal": 100}
}

def test_return_valid():
    ok, msg = validate_return(orders_sample, "ORD-001", 1)
    assert ok == True

def test_return_order_not_found():
    ok, msg = validate_return(orders_sample, "ORD-999", 1)
    assert ok == False

def test_return_already_returned():
    ok, msg = validate_return(orders_sample, "ORD-002", 1)
    assert ok == False

def test_return_invalid_reason():
    ok, msg = validate_return(orders_sample, "ORD-001", 4)
    assert ok == False

def test_return_reason_1():
    ok, msg = validate_return(orders_sample, "ORD-001", 1)
    assert ok == True

def test_return_reason_2():
    ok, msg = validate_return(orders_sample, "ORD-001", 2)
    assert ok == True

def test_return_reason_3():
    ok, msg = validate_return(orders_sample, "ORD-001", 3)
    assert ok == True

# ============================================
# TEST 12 - Generate Report Data
# ============================================

def test_report_empty_orders():
    report, msg = generate_report_data({})
    assert report is None

def test_report_delivered_order():
    orders = {
        "ORD-001": {
            "status"  : "Delivered",
            "total"   : 270,
            "profit"  : 30,
            "handling": 20,
            "delivery": 50,
            "subtotal": 200
        }
    }
    report, msg = generate_report_data(orders)
    assert report["total_revenue"]  == 270
    assert report["handling_total"] == 20
    assert report["delivery_total"] == 50
    assert report["vendor_profit"]  == 30
    assert report["net_app_profit"] == 70   # 20+50

def test_report_after_return():
    orders = {
        "ORD-001": {
            "status"  : "Delivered",
            "total"   : 270,
            "profit"  : 30,
            "handling": 20,
            "delivery": 50,
            "subtotal": 200
        },
        "ORD-002": {
            "status"  : "Returned",
            "total"   : 160,
            "profit"  : 10,
            "handling": 10,
            "delivery": 50,
            "subtotal": 100
        }
    }
    report, msg = generate_report_data(orders)
    assert report["total_revenue"]  == 430   # 270+160
    assert report["net_app_profit"] == 30    # (20+10)+(50+50)-100

# ============================================
# TEST 13 - Generate Order ID
# ============================================

def test_order_id_format():
    assert generate_order_id(1)   == "ORD-001"
    assert generate_order_id(10)  == "ORD-010"
    assert generate_order_id(100) == "ORD-100"

# ============================================
# TEST 14 - Vendor Exists
# ============================================

vendors_sample = {"12345": {"name": "Ramu"}}

def test_vendor_exists_true():
    assert vendor_exists(vendors_sample, "12345") == True

def test_vendor_exists_false():
    assert vendor_exists(vendors_sample, "99999") == False