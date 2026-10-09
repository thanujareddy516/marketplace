# ============================================
#   SMART VENDOR MARKETPLACE SYSTEM
#   main.py - Menu + All Input/Output
# ============================================

from logic import (
    validate_vendor_name, validate_license,
    validate_product_name,
    validate_original_price, validate_selling_price,
    validate_stock, validate_quantity,
    check_stock, calculate_bill, calculate_profit,
    validate_return, generate_report_data,
    vendor_exists, generate_order_id
)
import database as db

# ---- DATA STORAGE (runtime in-memory state) ----
vendors     = {}
products    = {}
orders      = {}

# ============================================
# LOAD SAVED DATA FROM DATABASE
# ============================================
def load_data():
    for v in db.list_vendors():
        vendors[v["license"]] = {
            "name"     : v["name"],
            "status"   : v["status"],
            "products" : [],
            "orders"   : [],
            "vendor_id": v["vendor_id"]
        }

    for p in db.list_products():
        products[p["name"]] = {
            "vendor"    : p["vendor_name"],
            "orig"      : p["orig_price"],
            "sell"      : p["sell_price"],
            "stock"     : p["stock"],
            "product_id": p["product_id"],
            "license"   : p["license"]
        }
        vendors[p["license"]]["products"].append({
            "name" : p["name"],
            "orig" : p["orig_price"],
            "sell" : p["sell_price"],
            "stock": p["stock"]
        })

    for o in db.list_all_orders():
        order = {
            "id"      : o["order_code"],
            "product" : o["product_name"],
            "qty"     : o["quantity"],
            "subtotal": o["subtotal"],
            "handling": o["handling"],
            "delivery": o["delivery"],
            "total"   : o["total"],
            "profit"  : o["profit"],
            "status"  : o["status"],
            "license" : o["license"]
        }
        orders[order["id"]] = order
        vendors[o["license"]]["orders"].append(order)

# ============================================
# VENDOR LOGIN / REGISTER
# ============================================
def vendor_login():
    while True:
        license = input("Enter License Number : ").strip()
        ok, msg = validate_license(license)
        if not ok:
            print(msg)
            continue
        break

    if vendor_exists(vendors, license):
        print(f"\nWelcome back {vendors[license]['name']}!")
        show_vendor_profile(license)
    else:
        while True:
            name = input("Enter Your Name      : ").strip()
            ok, msg = validate_vendor_name(name)
            if not ok:
                print(msg)
                continue
            break

        # Save to database
        vendor_id = db.add_vendor(license, name)

        vendors[license] = {
            "name"     : name,
            "status"   : "Active",
            "products" : [],
            "orders"   : [],
            "vendor_id": vendor_id
        }
        print(f"\nWelcome! Vendor registered successfully!")
        show_vendor_profile(license)

    return license

# ============================================
# SHOW VENDOR PROFILE
# ============================================
def show_vendor_profile(license):
    vendor = vendors[license]

    print("\n" + "="*40)
    print("         VENDOR PROFILE")
    print("="*40)
    print(f"Vendor Name : {vendor['name']}")
    print(f"License ID  : {license}")
    print(f"Status      : {vendor['status']}")

    print("\nProducts Listed:")
    print(f"{'Product':<12}{'Sell':>8}{'Stock':>8}")
    print("-"*40)
    if vendor["products"]:
        for p in vendor["products"]:
            print(f"{p['name']:<12}{p['sell']:>8}{p['stock']:>8}")
    else:
        print("No products added yet")

    print("\nOrder History:")
    print(f"{'Order ID':<12}{'Product':<12}{'Total':>8}{'Status':>10}")
    print("-"*40)
    if vendor["orders"]:
        for o in vendor["orders"]:
            print(f"{o['id']:<12}{o['product']:<12}{o['total']:>8}{o['status']:>10}")
    else:
        print("No orders yet")

    total_sales  = sum(o["total"]  for o in vendor["orders"] if o["status"] == "Delivered")
    total_profit = sum(o["profit"] for o in vendor["orders"] if o["status"] == "Delivered")

    print("\n" + "-"*40)
    print(f"Total Sales  : Rs.{total_sales}")
    print(f"Total Profit : Rs.{total_profit}")
    print("="*40)

# ============================================
# ADD PRODUCT
# ============================================
def add_product(license):

    while True:
        name = input("Enter Product Name   : ").strip()
        ok, msg = validate_product_name(name)
        if not ok:
            print(msg)
            continue
        break

    while True:
        orig_input = input("Enter Original Price : ").strip()
        ok, orig = validate_original_price(orig_input)
        if not ok:
            print(orig)
            continue
        break

    while True:
        sell_input = input("Enter Selling Price  : ").strip()
        ok, sell = validate_selling_price(sell_input, orig)
        if not ok:
            print(sell)
            continue
        break

    while True:
        stock_input = input("Enter Stock          : ").strip()
        ok, stock = validate_stock(stock_input)
        if not ok:
            print(stock)
            continue
        break

    profit = sell - orig

    # Save to database
    vendor_id  = vendors[license]["vendor_id"]
    product_id = db.add_product(vendor_id, name, orig, sell, stock)

    products[name] = {
        "vendor"    : vendors[license]["name"],
        "orig"      : orig,
        "sell"      : sell,
        "stock"     : stock,
        "product_id": product_id,
        "license"   : license
    }

    vendors[license]["products"].append({
        "name" : name,
        "orig" : orig,
        "sell" : sell,
        "stock": stock
    })

    print(f"\n{name} added successfully!")
    print(f"Selling Price   : Rs.{sell}")
    print(f"Profit per unit : Rs.{profit}")
    print(f"Stock           : {stock} units")

# ============================================
# VIEW ALL PRODUCTS
# ============================================
def view_products():
    if not products:
        print("No products available")
        return False

    print("\n" + "="*50)
    print("          AVAILABLE PRODUCTS")
    print("="*50)
    print(f"{'Product':<12}{'Vendor':<12}{'Sell':>8}{'Stock':>8}")
    print("-"*50)
    for name, details in products.items():
        print(f"{name:<12}{details['vendor']:<12}"
              f"{details['sell']:>8}"
              f"{details['stock']:>8}")
    print("="*50)
    return True

# ============================================
# PLACE ORDER
# ============================================
def place_order(license):
    if not view_products():
        return

    product = input("\nSelect Product  : ").strip()

    if product not in products:
        print("Error: product is not available")
        return

    while True:
        qty_input = input("Enter Quantity  : ").strip()
        ok, qty = validate_quantity(qty_input)
        if not ok:
            print(qty)
            continue
        break

    ok, result = check_stock(products, product, qty)
    if not ok:
        print(result)
        if "only" in result:
            confirm = input("Order available quantity? (yes/no): ")
            if confirm.lower() == "yes":
                qty = products[product]["stock"]
            else:
                return
        else:
            return

    subtotal, handling, delivery, total = calculate_bill(products, product, qty)
    profit = calculate_profit(products, product, qty)

    order_id_str = generate_order_id(db.next_order_number())

    # Credit the order to the vendor who owns the product
    license = products[product]["license"]

    product_id = products[product]["product_id"]
    vendor_id  = vendors[license]["vendor_id"]

    # Save order to database first, so stock is only reduced if it succeeds
    db.save_order(
        order_id_str, vendor_id, product_id,
        qty, subtotal, handling, delivery, total, profit
    )

    # Update stock in database
    products[product]["stock"] -= qty
    db.update_stock(product_id, products[product]["stock"])

    order = {
        "id"      : order_id_str,
        "product" : product,
        "qty"     : qty,
        "subtotal": subtotal,
        "handling": handling,
        "delivery": delivery,
        "total"   : total,
        "profit"  : profit,
        "status"  : "Delivered",
        "license" : license
    }
    orders[order_id_str] = order
    vendors[license]["orders"].append(order)

    for p in vendors[license]["products"]:
        if p["name"] == product:
            p["stock"] -= qty

    sell = products[product]["sell"]

    print("\n" + "="*35)
    print("          ORDER BILL")
    print("="*35)
    print(f"Product         : {product}")
    print(f"Quantity        : {qty}")
    print(f"Selling Price   : Rs.{sell} x {qty} = Rs.{subtotal}")
    print(f"Handling Fee    : Rs.{handling}")
    if delivery > 0:
        print(f"Delivery Charge : Rs.{delivery}")
    else:
        print(f"Delivery Charge : FREE!")
    print(f"Total           : Rs.{total}")
    print(f"Order ID        : {order_id_str}")
    print("Order Confirmed!")
    print("="*35)

# ============================================
# PROCESS RETURN
# ============================================
def process_return():
    order_id_str = input("Enter Order ID : ").strip()

    if order_id_str not in orders:
        print("Error: order ID not found")
        return

    if orders[order_id_str]["status"] == "Returned":
        print("Error: order already returned")
        return

    print("\nReturn Reasons:")
    print("1. Item damaged")
    print("2. No delivery")
    print("3. Late delivery")

    while True:
        try:
            reason = int(input("Enter Reason   : "))
        except ValueError:
            print("Error: reason must be a number")
            continue

        ok, msg = validate_return(orders, order_id_str, reason)
        if not ok:
            print(msg)
            return
        break

    order    = orders[order_id_str]
    subtotal = order["subtotal"]
    product  = order["product"]
    qty      = order["qty"]
    license  = order["license"]

    old_stock = products[product]["stock"]
    products[product]["stock"] += qty
    product_id = products[product]["product_id"]

    for p in vendors[license]["products"]:
        if p["name"] == product:
            p["stock"] += qty

    # Update database: mark order returned, restore stock, save return record
    db_order = db.get_order_by_code(order_id_str)
    if db_order:
        db.mark_order_returned(db_order["order_id"])
        db.save_return(db_order["order_id"], reason, subtotal)
    db.update_stock(product_id, products[product]["stock"])

    orders[order_id_str]["status"] = "Returned"
    for o in vendors[license]["orders"]:
        if o["id"] == order_id_str:
            o["status"] = "Returned"

    print(f"\nRefund of Rs.{subtotal} approved!")
    print(f"Stock restored: {product} {old_stock} -> {products[product]['stock']} units")

# ============================================
# SHOW MERCHANT REPORT
# ============================================
def show_report():
    report, msg = generate_report_data(orders)

    if report is None:
        print(msg)
        return

    print("\n" + "="*45)
    print("      MERCHANT DAILY PROFIT REPORT")
    print("="*45)
    print(f"Total Revenue             : Rs.{report['total_revenue']}")
    print(f"Handling Fee Collected    : Rs.{report['handling_total']}")
    print(f"Delivery Charge Collected : Rs.{report['delivery_total']}")
    print(f"Net App Profit            : Rs.{report['net_app_profit']}")
    print(f"Vendor Profit             : Rs.{report['vendor_profit']}")

    print("\nProfit by Vendor:")
    print(f"{'Vendor':<20}{'License':<12}{'Profit':>13}")
    print("-"*45)
    for license, vendor in vendors.items():
        profit = sum(o["profit"] for o in vendor["orders"]
                     if o["status"] == "Delivered")
        print(f"{vendor['name']:<20}{license:<12}{'Rs.' + str(round(profit, 2)):>13}")
    print("="*45)

# ============================================
# MAIN MENU
# ============================================
def main():
    db.init_db()   # Create tables if they don't exist
    load_data()    # Restore vendors, products and orders from earlier runs

    print("\n" + "="*45)
    print("   SMART VENDOR MARKETPLACE SYSTEM")
    print("="*45)

    current_license = None

    while True:
        print("\n--- MAIN MENU ---")
        print("1. Vendor Login / Register")
        print("2. Add Product")
        print("3. View Products")
        print("4. Place Order")
        print("5. Return Order")
        print("6. Merchant Report")
        print("7. Exit")

        choice = input("\nEnter Choice : ").strip()

        if choice == "1":
            current_license = vendor_login()

        elif choice == "2":
            if not current_license:
                print("Error: please login first (Option 1)")
            else:
                add_product(current_license)

        elif choice == "3":
            view_products()

        elif choice == "4":
            if not current_license:
                print("Error: please login first (Option 1)")
            else:
                place_order(current_license)

        elif choice == "5":
            process_return()

        elif choice == "6":
            show_report()

        elif choice == "7":
            print("\nThank you! Goodbye!")
            break

        else:
            print("Error: please enter a number between 1 and 7")

if __name__ == "__main__":
    main()