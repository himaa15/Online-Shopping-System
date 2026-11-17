import json
import streamlit as st
from classes import Product, ShoppingCart

# Configure the application
st.set_page_config(
    page_title = "Online Shopping System",
    page_icon = "🛍️",
    layout = "wide"
)
# Read products from the Json file
with open("products.json","r") as f:
    products = json.load(f)

# Initialize shopping cart object
if "shopping_cart" not in st.session_state:
    st.session_state.shopping_cart = ShoppingCart()

shopping_cart = st.session_state.shopping_cart
cart = shopping_cart.cart

if "show_cart" not in st.session_state:
    st.session_state.show_cart = False

# Intialize order history
if "order_history" not in st.session_state:
    st.session_state.order_history = []

# Intialize order history visibility

if "show_order_history" not in st.session_state:
    st.session_state.show_order_history = False


# Application heading
header_left, header_right = st.columns([10,1])

with header_left:
    st.title("🛍️ online shopping system")
    st.subheader("Welcome! Browse our available products.")

with header_right:
    st.write("")
    if st.button("your🛒",key = "cart_icon",help="Open Shopping cart"):
        st.session_state.show_cart = not st.session_state.show_cart

# Search box
search = st.text_input("🔍 Search for a product")

# category filter 
categories = ["All"] + list(dict.fromkeys(product["category"] for product in products))

category = st.selectbox("Select Category",categories)

# Filter products
filtered_products = []

for product in products:

    if search.lower() not in product["name"].lower():
        continue

    if category != "All" and product["category"] != category:
        continue

    filtered_products.append(product)

# Display the products only when checkout is hiddden
if not st.session_state.get("show_buy_now",False):

    st.subheader("Product Catalogue")

    columns = st.columns(4)

    for index , product in enumerate(filtered_products):

        with columns[index % 4]:

            with st.container(border=True):

                st.image(product["image"],width = 150)
                st.subheader(product["name"])
                st.write("Price: ₹", product["price"])
                st.caption(f"Category: {product['category']}")
                st.caption(f"Available stock:{ product['stock']}")

                quantity = st.number_input(
                    "Quantity",
                    min_value = 1,
                    max_value = max(1,int(product['stock'])),
                    value = 1,
                    key = f"quantity_{product['id']}",
                    disabled = int(product["stock"]) == 0
                )

                if int(product["stock"]) > 0:
                    btn1, btn2 = st.columns(2)
                
                    with btn1:
                        if st.button("Add to Cart", key=f"add_{product['id']}", use_container_width=True):

                            current_quantity = cart.get(product["id"], 0)

                            if current_quantity + quantity <= int(product["stock"]):
                                shopping_cart.add_to_cart(product["id"], quantity)
                                st.success("Product added to cart!")
                            else:
                                st.error("Not enough stock!")

                    with btn2:

                        if st.button("Buy Now",key=f"buy_{product['id']}",use_container_width = True):
                            if int(product["stock"]) > 0:
                                st.session_state.buy_now_product = product["id"]
                                st.session_state.buy_now_quantity = int(quantity)
                                st.session_state.show_buy_now = True
                                st.session_state.show_cart = False
                                st.rerun()

                            else:
                                st.warning("This product is out of stock")
# Buy Now - Direct Checkout
if st.button("Back to shopping", key = "back_to_shopping"):
    st.session_state.show_buy_now = False
    st.rerun()

if st.session_state.get("show_buy_now",False):
    st.divider()
    st.header("Buy Now - Checkout")

    product_id = st.session_state.buy_now_product
    buy_quantity = st.session_state.buy_now_quantity

    selected_product = None

    for product in products:
        if int(product['id']) == int(product_id):
            selected_product = product
            break
    if selected_product is not None:
        st.write(f"**Product:**{selected_product['name']}")
        st.write(f"**price:** Rs{selected_product['price']}")
        st.write(f"**Quantity:**{buy_quantity}")

        total = float(selected_product["price"]) * buy_quantity
        st.subheader(f'Total Amount: Rs{total:g}')

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Confirm Purchase",key = "confirm_buy_now"):
                if buy_quantity > int(selected_product["stock"]):
                    st.error('Requested quantity exceeds available stock.')
                else:
                    order = {"items": [{
                            "name": selected_product["name"],
                            "quantity": buy_quantity,
                            "price": float(selected_product["price"])
                        }],
                        "total": total
                    }

                    st.session_state.order_history.append(order)
                    st.session_state.last_order_total = total
                    st.session_state.last_order_items = 1
                    st.session_state.order_confirmed = True
                    st.session_state.show_buy_now = False
                    st.rerun()

        with col2:
            if st.button("Cancel", key="cancel_buy_now"):
                st.session_state.show_buy_now = False
                st.rerun()

# Display shopping cart only when the icon is clicked
if st.session_state.show_cart:
    st.divider()  
    st.header("🛒 My shopping Cart")

    if st.button("✖ Close Cart", key = "close_cart"):
        st.session_state.show_cart = False
        st.rerun()

    if not cart:
        st.write("your cart is empty.")
    else:
        total = 0
        
        for product_id , quantity in cart.items():
            for product in products:
                if product["id"] == product_id:
                    amount = int(product['price']) * int(quantity)
                    total += amount

                    col1,col2,col3 = st.columns([3,1,1])

                    with col1:
                        st.write(f"**{product['name']}**")
                        st.write(f"Quantity:{quantity}")

                    with col2:
                        st.write(f"Rs{amount}")

                    with col3:
                        if st.button("Remove",key =f"remove_{product_id}"):

                            shopping_cart.remove_from_cart(product_id)
                            st.rerun()

        st.subheader(f"Totat :₹{total}")

        if st.button("🗑️ Clear Cart", key ="clear_cart"):
            shopping_cart.clear_cart()
            st.rerun()
# checkout

        if st.button("🏷️checkout",key = "checkout"):
            if cart:
                order = {
                    "items": [],
                    "total": total
                }

                for product_id, quantity in cart.items():
                    for product in products:
                        if int(product["id"]) == int(product_id):
                            order["items"].append({
                                "name": product["name"],
                                "quantity": int(quantity),
                                "price": float(product["price"])
                            })

                # Save order before clearing the cart
                if "order_history" not in st.session_state:
                    st.session_state.order_history = []

                st.session_state.order_history.append(order)

                st.session_state.last_order_total = total
                st.session_state.last_order_items = len(order["items"])
                st.session_state.order_confirmed = True

                shopping_cart.clear_cart()
                st.session_state.show_cart = False
                st.rerun()

            else:
                st.warning("Your cart is empty!")

# order Confirmation
if st.session_state.get("order_confirmed",False):
    st.success("🥳🎊 Order palced successfully ")

    st.write(f"Total paid:{st.session_state.last_order_total}")

    st.write(f"Different products ordered:" f"{st.session_state.get('last_order_items',0)}")

    if st.button("Continue shopping"):
        st.session_state.order_confirmed = False
        st.session_state.show_buy_now = False
        st.rerun()
# Order History Button

st.divider()

if "show_order_history" not in st.session_state:
    st.session_state.show_order_history = False

if st.button("📦My Order History", key = "order_history_button"):
    st.session_state.show_order_history =(not st.session_state.show_order_history)


# Display Order History only when clicked

if st.session_state.show_order_history:
    st.header("📦 My Order History")

if not st.session_state.order_history:
    st.info("You haven't palced any orders yet.")

else:
    for index,order in enumerate(st.session_state.order_history, start = 1):

        with st.expander(f"Order{index}-Rs{order['total']}"):
            for item in order["items"]:
                amount = (float(item["price"])*int(item["quantity"]))

                st.write(f"{item['name']} x {item['quantity']} -Rs{amount:g}")


            st.write(f"**Order Total:Rs{order['total']}**")



                