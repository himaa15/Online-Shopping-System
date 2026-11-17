
class Product:
    def __init__(self, product_id, name, price, category, stock):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.stock = stock


class ShoppingCart:
    def __init__(self):
        self.cart = {}

    def add_to_cart(self, product_id, quantity):
        self.cart[product_id] = self.cart.get(product_id, 0) + quantity

    def remove_from_cart(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]

    def clear_cart(self):
        self.cart.clear                                                                                                                                                   ()

    def calculate_total(self, products):
        total = 0

        for product_id, quantity in self.cart.items():
            for product in products:
                if product["id"] == product_id:
                    total += float(product["price"]) * quantity

        return total
