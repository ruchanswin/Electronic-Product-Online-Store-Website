# product.py
class Product:
    def __init__(self, product_id, name, description, price, stock):
        self.id = product_id
        self.name = name
        self.description = description
        self.price = float(price)
        self.stock = int(stock)
