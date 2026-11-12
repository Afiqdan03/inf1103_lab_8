import json
import os
from abc import ABC, abstractmethod


# Interface contract for products that support shipping calculations
class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass


# Supplier class for association - can exist independently from a product
class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_email: str):
        self.supplier_id: str = supplier_id
        self.name: str = name
        self.contact_email: str = contact_email

    def display_information(self) -> None:
        print(f"Supplier: {self.name} | Email: {self.contact_email}")


class Product(ABC):
    """Abstract base class representing a generic product with a Supplier association."""

    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier):
        self._product_id: str = product_id
        self._name: str = name
        self.price = price    # goes through the price setter (validation)
        self.stock = stock    # goes through the stock setter (validation)
        self.supplier: Supplier = supplier

    # ---- properties (backing fields use a leading underscore) ----
    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValueError("Price cannot be negative.")
        self._price = value

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, value: int) -> None:
        if value < 0:
            raise ValueError("Stock cannot be negative.")
        self._stock = value

    # ---- behaviour ----
    def update_stock(self, quantity: int) -> None:
        """Safely updates stock inventory level."""
        new_stock = self._stock + quantity
        if new_stock < 0:
            print("Error: Stock cannot be negative!")
        else:
            self._stock = new_stock
            print(f"Stock updated successfully for {self._name}. Current stock: {self._stock}")

    def display_information(self) -> None:
        """Displays common product details including associated supplier."""
        print(f"ID: {self._product_id} | Name: {self._name} | Price: ${self._price:.2f} | Stock: {self._stock}", end="")
        print(f" | Supplier: {self.supplier.name} ({self.supplier.contact_email})", end="")

    def _base_dict(self) -> dict:
        """Common fields (including supplier) shared by all subclasses."""
        return {
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "stock": self._stock,
            "supplier_id": self.supplier.supplier_id,
            "supplier_name": self.supplier.name,
            "supplier_email": self.supplier.contact_email,
        }

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        """Abstract method forcing subclasses to define fulfilment behavior."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Abstract method for dictionary serialization."""
        pass


class PhysicalProduct(Product, CanBeShipped):
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier, weight: float):
        super().__init__(product_id, name, price, stock, supplier)
        self.weight = weight  # goes through the weight setter

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    def weight(self, value: float) -> None:
        if value < 0:
            raise ValueError("Weight cannot be negative.")
        self._weight = value

    def display_information(self) -> None:
        super().display_information()
        print(f" | Weight: {self._weight} kg | Fulfilment: {self.get_fulfilment_info()}")

    def get_fulfilment_info(self) -> str:
        return "Requires physical shipping"

    def calculate_shipping_cost(self) -> float:
        return 5.00 + (2.00 * self._weight)

    def to_dict(self) -> dict:
        data = self._base_dict()
        data["type"] = "physical"
        data["weight"] = self._weight
        return data


class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier, download_size: float):
        super().__init__(product_id, name, price, stock, supplier)
        self.download_size = download_size  # goes through the setter

    @property
    def download_size(self) -> float:
        return self._download_size

    @download_size.setter
    def download_size(self, value: float) -> None:
        if value < 0:
            raise ValueError("Download size cannot be negative.")
        self._download_size = value

    def display_information(self) -> None:
        super().display_information()
        print(f" | Download Size: {self._download_size} MB | Fulfilment: {self.get_fulfilment_info()}")

    def get_fulfilment_info(self) -> str:
        return "Delivered via digital download link"

    def to_dict(self) -> dict:
        data = self._base_dict()
        data["type"] = "digital"
        data["download_size"] = self._download_size
        return data


class Inventory:
    """Manages a collection of Product objects using aggregation."""

    def __init__(self):
        self.products: list[Product] = []

    def add_product(self, product: Product) -> bool:
        if self.search_product(product.product_id) is not None:
            print(f"Error: a product with ID '{product.product_id}' already exists.")
            return False
        self.products.append(product)
        print(f"Added {product.name} to inventory.")
        return True

    def remove_product(self, product_id: str) -> bool:
        # removes the reference without destroying the product object itself
        product = self.search_product(product_id)
        if product:
            self.products.remove(product)
            return True
        return False

    def search_product(self, product_id: str):
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None

    def display_all(self) -> None:
        if not self.products:
            print("\nInventory is currently empty.")
            return

        print("\n--- Current Inventory ---")
        for product in self.products:
            product.display_information()
        print("-------------------------")

    def save_to_file(self, filename: str = "inventory.json") -> None:
        """Saves inventory items preserving their specific subclasses/types."""
        data = [product.to_dict() for product in self.products]
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Inventory successfully saved to {filename}.")
        except IOError as e:
            print(f"Error saving file: {e}")

    def load_from_file(self, filename: str = "inventory.json") -> None:
        if not os.path.exists(filename):
            return
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            self.products.clear()
            for item in data:
                ptype = item.get("type")

                # Recreate the associated Supplier object from saved data
                supplier = Supplier(
                    item.get("supplier_id", "S001"),
                    item.get("supplier_name", "Default Supplier"),
                    item.get("supplier_email", "supplier@email.com"),
                )

                if ptype == "physical":
                    product = PhysicalProduct(
                        item["product_id"],
                        item["name"],
                        float(item["price"]),
                        int(item["stock"]),
                        supplier,
                        float(item["weight"]),
                    )
                elif ptype == "digital":
                    product = DigitalProduct(
                        item["product_id"],
                        item["name"],
                        float(item["price"]),
                        int(item["stock"]),
                        supplier,
                        float(item["download_size"]),
                    )
                else:
                    continue

                self.products.append(product)
            print(f"Inventory successfully loaded from {filename}.")
        except (IOError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading file: {e}")


class OrderLine:
    """Represents a line item referencing a Product."""

    def __init__(self, product: Product, quantity: int):
        self.product: Product = product
        self.quantity: int = quantity

    def calculate_subtotal(self) -> float:
        return self.product.price * self.quantity


class Order:
    """Order owns OrderLine collection via composition."""

    def __init__(self, order_id: str):
        self.order_id: str = order_id
        self.order_lines: list[OrderLine] = []

    def add_order_line(self, product: Product, quantity: int) -> None:
        line = OrderLine(product, quantity)
        self.order_lines.append(line)

    def calculate_total(self) -> float:
        total: float = 0.0
        for line in self.order_lines:
            total += line.calculate_subtotal()
        return total


# test function to demonstrate LSP and polymorphism
def show_product_details(product: Product) -> None:
    product.display_information()
    print(f"   -> Fulfilment: {product.get_fulfilment_info()}")


def read_common_fields():
    """Prompts for the fields shared by every product type (including the supplier)."""
    pid = input("Enter Product ID: ").strip()
    if not pid:
        raise ValueError("Product ID cannot be empty.")
    name = input("Enter Product Name: ").strip()
    price = float(input("Enter Price ($): "))
    stock = int(input("Enter Initial Stock Quantity: "))
    sup_name = input("Enter Supplier Name: ").strip()
    sup_email = input("Enter Supplier Email: ").strip()
    supplier = Supplier(f"S_{pid}", sup_name, sup_email)
    return pid, name, price, stock, supplier


def main():
    inventory = Inventory()
    inventory.load_from_file("inventory.json")

    while True:
        print("\n=== Inventory Management System (Lab 8) ===")
        print("1. Display all products")
        print("2. Add a Physical Product")
        print("3. Add a Digital Product")
        print("4. Update stock")
        print("5. Search for a product & calculate shipping")
        print("6. Save inventory")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            inventory.display_all()

        elif choice in ("2", "3"):
            try:
                pid, name, price, stock, supplier = read_common_fields()
                if choice == "2":
                    weight = float(input("Enter Product Weight (kg): "))
                    new_product = PhysicalProduct(pid, name, price, stock, supplier, weight)
                else:
                    download_size = float(input("Enter Download Size (MB): "))
                    new_product = DigitalProduct(pid, name, price, stock, supplier, download_size)
                inventory.add_product(new_product)
            except ValueError as e:
                print(f"Invalid input! {e}")

        elif choice == "4":
            pid = input("Enter Product ID to update stock: ").strip()
            product = inventory.search_product(pid)
            if product:
                try:
                    qty = int(input("Enter stock change amount (negative to reduce): "))
                    product.update_stock(qty)
                except ValueError:
                    print("Invalid input! Quantity must be an integer.")
            else:
                print(f"Product with ID '{pid}' not found.")

        elif choice == "5":
            pid = input("Enter Product ID to search: ").strip()
            product = inventory.search_product(pid)
            if product:
                print("\nProduct Found:")
                product.display_information()
                if isinstance(product, CanBeShipped):
                    shipping_cost = product.calculate_shipping_cost()
                    print(f"Estimated Shipping Cost: ${shipping_cost:.2f}")
            else:
                print(f"Product with ID '{pid}' not found.")

        elif choice == "6":
            inventory.save_to_file("inventory.json")

        elif choice == "7":
            inventory.save_to_file("inventory.json")
            print("Exiting program. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


if __name__ == "__main__":
    main()