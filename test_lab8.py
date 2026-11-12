# test_lab8.py

# IMPORTANT: Adjust the import below if your main file has a different name
from lab8 import (
    Supplier, PhysicalProduct, DigitalProduct, 
    Inventory, Order, show_product_details
)

def main():
    print("=== Section 2.2: Association (Supplier shared by two products) ===")
    # Create one supplier
    shared_supplier = Supplier("S001", "Global Tech Supplies", "contact@globaltech.com")
    
    # Create two different products using the same supplier
    laptop = PhysicalProduct("P001", "Gaming Laptop", 1500.00, 10, shared_supplier, 2.5)
    software = DigitalProduct("D001", "Antivirus Software", 49.99, 100, shared_supplier, 150.0)
    
    print("Supplier Details from Product 1:")
    laptop.display_information()
    print("\nSupplier Details from Product 2:")
    software.display_information()
    print("\nObservation: Both products share the same Supplier object, showing association.")

    print("\n\n=== Section 3.2: Aggregation (Moving product from Inventory A to B) ===")
    inventory_a = Inventory()
    inventory_b = Inventory()
    
    # Add product to Inventory A
    inventory_a.add_product(laptop)
    print("\nInventory A after adding:")
    inventory_a.display_all()
    
    # Move from A to B
    print("\nRemoving product from Inventory A and adding to Inventory B...")
    inventory_a.remove_product(laptop.product_id)
    inventory_b.add_product(laptop)
    
    print("\nInventory A after removal:")
    inventory_a.display_all()
    print("Inventory B after addition:")
    inventory_b.display_all()
    print("Observation: The product was not destroyed when removed from Inventory A, proving aggregation.")

    print("\n\n=== Section 4.3: Composition (Same product in two different orders) ===")
    order1 = Order("ORD-001")
    order2 = Order("ORD-002")
    
    # Add the same product to two different orders
    order1.add_order_line(laptop, 2)
    order2.add_order_line(laptop, 1)
    
    print(f"Order 1 Total (2 Laptops): ${order1.calculate_total():.2f}")
    print(f"Order 2 Total (1 Laptop): ${order2.calculate_total():.2f}")
    
    # Checking object IDs to prove unique OrderLine objects exist for the same Product
    line_id_order1 = id(order1.order_lines[0])
    line_id_order2 = id(order2.order_lines[0])
    product_id_order1 = id(order1.order_lines[0].product)
    product_id_order2 = id(order2.order_lines[0].product)
    
    print(f"\nOrder 1 Line ID: {line_id_order1} | Product ID: {product_id_order1}")
    print(f"Order 2 Line ID: {line_id_order2} | Product ID: {product_id_order2}")
    print("Observation: The Product object is the exact same (same ID), but each Order created its own unique OrderLine object (different IDs). This proves Composition.")

    print("\n\n=== Section 6.2 & 7.2: LSP & Polymorphism (show_product_details) ===")
    # Using the function defined in your lab8 file that accepts the abstract 'Product' type
    print("Calling show_product_details() with a PhysicalProduct:")
    show_product_details(laptop)
    
    print("\nCalling show_product_details() with a DigitalProduct:")
    show_product_details(software)
    print("\nObservation: The exact same function successfully processes both child classes, dispatching the correct fulfilment info without needing `isinstance()` checks.")

if __name__ == "__main__":
    main()