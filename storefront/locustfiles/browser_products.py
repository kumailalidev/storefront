from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):
    # Following tasks user will perform
    #   - Viewing products
    #   - Viewing product details
    #   - Add product to cart

    wait_time = between(
        1, 5
    )  # apply wait time after each time between 1 to 5 seconds (chosen randomly)

    @task(2)
    def view_products(self):
        # generate a random collection id
        collection_id = randint(2, 6)
        self.client.get(
            f"/store/products/?collection_id={collection_id}", name="/store/products/"
        )

    @task(4)  # 4 is weight, higher number means greater chance
    def view_product(self):
        product_id = randint(1, 1000)
        self.client.get(f"/store/products/{product_id}", name="/store/products/:id")

    @task(1)
    def add_to_cart(self):
        product_id = randint(1, 10)
        self.client.post(
            f"/store/carts/{self.cart_id}/items/",
            name="/store/carts/items",
            json={"product_id": product_id, "quantity": 1},  # sending data to server
        )

    # We need need a cart_id before user starts adding products to the cart
    # creating a lifecycle hook; it gets called whenever new user starts browsing our website
    def on_start(self):
        response = self.client.post("/store/cart/")
        result = response.json()
        self.cart_id = result["id"]
