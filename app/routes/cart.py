import os
from flask import (
    Blueprint,
    request,
    jsonify,
)
import requests
from uuid import uuid4
from app.models import Order
from app.forms.order import OrderForm
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Cart, CartItem, Product
from app.controllers.mailing import send_email
from dotenv import load_dotenv, find_dotenv

from app.utils import generate_tracking_number

load_dotenv(find_dotenv())

BASE_URL = os.getenv("BASE_URL")

if BASE_URL is None:
    raise Exception("BASE_URL not provided!")

cart_route = Blueprint("cart_route", __name__, url_prefix="/ringstech/api/v1/cart")


@cart_route.route("/", methods=["POST"])
def add_item_to_cart_route():
    """Route to add new item to cart"""
    cart_id = request.args.get("cart_id")
    product_id = request.args.get("product_id")
    quantity = request.args.get("quantity")
    color = request.args.get("color")

    if not cart_id:
        return jsonify(error="Cart Id not provided")

    if not product_id:
        return jsonify(error="Product Id not provided")

    if not quantity:
        return jsonify(error="Item Quantity not provided")

    product = db.session.query(Product).filter_by(product_id=product_id).scalar()

    cart_item = CartItem(
        item_id=str(uuid4()),
        cart_id=cart_id,
        product_id=product_id,
        product_name=product.product_name,
        color=color,
        quantity=quantity,
        price=product.product_unit_price,
    )

    try:
        if (
                db.session.query(CartItem)
                        .filter_by(product_id=product_id, color=color)
                        .count()
                > 0
        ):
            (
                db.session.query(CartItem)
                .filter_by(product_id=product_id, color=color)
                .update({"quantity": CartItem.quantity + quantity})
            )
        else:
            db.session.add(cart_item)

        db.session.commit()

        return jsonify(
            msg="Successfully Added item {} to cart {}".format(
                cart_item.item_id, cart_item.cart_id
            )
        ), 200

    except Exception as ex:
        print(ex)
        return jsonify(error=str(ex))


@cart_route.route("/", methods=["GET"])
def view_cart_route():
    """Route to View Cart"""
    cart_id = request.args.get("cart_id")

    if not cart_id:
        return jsonify(error="Please provide Cart ID")

    # query = db.select(CartItem).order_by(CartItem.item_id)
    # query = query.where(CartItem.cart_id == cart_id)
    #
    # cart = db.session.execute(query).scalars().all()

    cart = db.session.query(Cart).filter_by(cart_id=cart_id, checked_out=False).scalar()
    print(cart)

    if not cart:
        return jsonify(f"Cart {cart_id} does not exist!"), 404

    cart_items = db.session.query(CartItem).filter_by(cart_id=cart.cart_id)

    if not cart_items:
        return jsonify([]), 200

    serialized_cart_items = [item.serialize() for item in cart_items]
    return jsonify(serialized_cart_items)


@cart_route.route("/checkout", methods=["POST"])
def checkout_cart():
    """New Order"""

    cart_id = request.args.get("cart_id")

    if not cart_id:
        return jsonify(error="Cart ID Required")

    cart = db.session.query(Cart).filter_by(cart_id=cart_id).scalar()

    if not cart:
        return jsonify(error="Cart does not exist!")

    total_amount = int(cart.total_amount)

    try:
        new_order_form = OrderForm(request.form)

        if new_order_form.validate():

            payment_url = BASE_URL + "/payment/pay?phone_number={}&total_amount={}".format(
                new_order_form.mpesa_number.data, total_amount
            )

            order = Order(
                order_id=str(uuid4()),
                cart_id=cart_id,
                first_name=new_order_form.first_name.data,
                middle_name=new_order_form.middle_name.data,
                last_name=new_order_form.last_name.data,
                street_address=new_order_form.street_address.data,
                city=new_order_form.city.data,
                state_or_province=new_order_form.state_or_province.data,
                email_address=new_order_form.email_address.data,
                phone_number=new_order_form.phone_number.data,
                total_amount=cart.total_amount,
                tracking_number=generate_tracking_number(),
                zip_code=new_order_form.zip_code.data,
            )

            db.session.add(order)
            db.session.commit()

            # Make Payment
            response = requests.get(payment_url)
            response_data = response.json()

            if response.status_code == 200:
                return jsonify(msg="Payment initiated!",
                               response_code=response_data['ResponseCode'],
                               checkout_request_id=response_data['CheckoutRequestID'],
                               ), response.status_code

            return jsonify(response.content.decode()), response.status_code

        else:
            print(new_order_form.errors)
            return jsonify(new_order_form.errors), 400

    except SQLAlchemyError as ex:
        print(ex)
        return jsonify(error="Order already exists!"), 500


@cart_route.route("/clear", methods=["GET"])
def clear_cart():
    cart_id = request.args.get("cart_id")

    try:
        if cart_id is None:
            return jsonify("Cart ID Not Provided")

        db.session.query(Cart).filter_by(cart_id=cart_id).update({'checked_out': True})
        db.session.commit()

        return jsonify("Successfully Cleared Cart"), 200

    except Exception as ex:
        print(ex)
        return jsonify("Could not clear cart!"), 500
