# ============================================
#   SMART VENDOR MARKETPLACE SYSTEM
#   logic.py - Pure Functions Only
#   (No input, No print, No globals)
# ============================================

DELIVERY_CHARGE = 50
FREE_DELIVERY   = 500      # Free delivery if subtotal >= Rs.500
HANDLING_RATE   = 0.10

# ============================================
# FUNCTION 1 - Validate Vendor Name
# ============================================
def validate_vendor_name(name):
    if not name:
        return False, "Error: name cannot be empty"
    if not name.isalpha():
        return False, "Error: name must contain letters only"
    return True, "Valid"

# ============================================
# FUNCTION 2 - Validate License Number
# ============================================
def validate_license(license):
    if not license:
        return False, "Error: license number cannot be empty"
    if not license.isdigit():
        return False, "Error: license number must contain digits only"
    return True, "Valid"

# ============================================
# FUNCTION 3 - Validate Product Name
# ============================================
def validate_product_name(name):
    if not name:
        return False, "Error: product name cannot be empty"
    if not name.isalpha():
        return False, "Error: product name must contain letters only"
    return True, "Valid"

# ============================================
# FUNCTION 4 - Validate Original Price
# ============================================
def validate_original_price(orig):
    try:
        orig = float(orig)
    except (ValueError, TypeError):
        return False, "Error: original price must be a number"
    if orig <= 0:
        return False, "Error: original price must be greater than zero"
    return True, orig

# ============================================
# FUNCTION 5 - Validate Selling Price
# ============================================
def validate_selling_price(sell, orig):
    try:
        sell = float(sell)
    except (ValueError, TypeError):
        return False, "Error: selling price must be a number"
    if sell <= orig:
        return False, "Error: selling price must be greater than original price"
    return True, sell

# ============================================
# FUNCTION 6 - Validate Stock
# ============================================
def validate_stock(stock):
    try:
        stock = int(stock)
    except (ValueError, TypeError):
        return False, "Error: stock must be a whole number"
    if stock <= 0:
        return False, "Error: stock must be at least 1"
    return True, stock

# ============================================
# FUNCTION 7 - Validate Quantity
# ============================================
def validate_quantity(qty):
    try:
        qty = int(qty)
    except (ValueError, TypeError):
        return False, "Error: quantity must be a whole number"
    if qty <= 0:
        return False, "Error: quantity must be at least 1"
    return True, qty

# ============================================
# FUNCTION 8 - Check Stock Availability
# ============================================
def check_stock(products, product, qty):
    if product not in products:
        return False, "Error: product not found"
    if products[product]["stock"] == 0:
        return False, "Error: product is out of stock"
    if qty > products[product]["stock"]:
        return False, f"Error: only {products[product]['stock']} units available"
    return True, qty

# ============================================
# FUNCTION 9 - Calculate Bill
# ============================================
def calculate_bill(products, product, qty):
    sell     = products[product]["sell"]
    subtotal = sell * qty
    handling = round(subtotal * HANDLING_RATE, 2)
    delivery = DELIVERY_CHARGE if subtotal < FREE_DELIVERY else 0
    total    = round(subtotal + handling + delivery, 2)
    return subtotal, handling, delivery, total

# ============================================
# FUNCTION 10 - Calculate Vendor Profit
# ============================================
def calculate_profit(products, product, qty):
    sell   = products[product]["sell"]
    orig   = products[product]["orig"]
    profit = round((sell - orig) * qty, 2)
    return profit

# ============================================
# FUNCTION 11 - Validate Return
# ============================================
def validate_return(orders, order_id, reason):
    if order_id not in orders:
        return False, "Error: order ID not found"
    if orders[order_id]["status"] == "Returned":
        return False, "Error: order already returned"
    if reason not in [1, 2, 3]:
        return False, "Error: return option not available"
    return True, "Valid"

# ============================================
# FUNCTION 12 - Generate Report Data
# ============================================
def generate_report_data(orders):
    if not orders:
        return None, "No transactions today. Report empty"

    total_revenue  = 0
    vendor_profit  = 0
    handling_total = 0
    delivery_total = 0
    refund_amount  = 0

    for order in orders.values():
        # ALL orders count for revenue, handling, delivery
        total_revenue  += order["total"]
        handling_total += order["handling"]
        delivery_total += order["delivery"]

        if order["status"] == "Delivered":
            vendor_profit += order["profit"]
        elif order["status"] == "Returned":
            refund_amount += order["subtotal"]

    net_app_profit = round(handling_total + delivery_total - refund_amount, 2)

    report = {
        "total_revenue" : round(total_revenue,  2),
        "handling_total": round(handling_total, 2),
        "delivery_total": round(delivery_total, 2),
        "net_app_profit": net_app_profit,
        "vendor_profit" : round(vendor_profit,  2)
    }
    return report, "Success"

# ============================================
# FUNCTION 13 - Check Vendor Exists
# ============================================
def vendor_exists(vendors, license):
    return license in vendors

# ============================================
# FUNCTION 14 - Generate Order ID
# ============================================
def generate_order_id(count):
    return f"ORD-{str(count).zfill(3)}"