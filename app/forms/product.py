from wtforms import StringField, validators, BooleanField, IntegerField, FileField, FloatField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed


class ProductForm(FlaskForm):
    """A form representing Product registration"""

    in_stock = IntegerField(
        "Product in Stock", [validators.DataRequired("Product in Stock required!")]
    )
    brand = StringField(
        "Product Brand", []
    )
    model = StringField("Product Model", [])
    battery = StringField("Product Battery", [])
    cameras = StringField("Product Cameras", [])
    product_image = (
        FileField("Product Image", [FileRequired("Product Image is required"), FileAllowed(
            {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp',
             'avif', 'bmp', 'tiff', 'ico', 'svg', 'psd', 'eps',
             'ai', 'raw', 'heic', 'heif'
             })]
            ))
    processor = StringField("Product Processor", [])
    display = StringField("Product Display", [])
    ram = StringField("Product RAM", [])

    product_name = StringField(
        "Product Name", [validators.DataRequired("Product Name is required!")]
    )
    product_unit_price = FloatField(
        "Product Unit Price",
        [
            validators.DataRequired("Product Unit Price is required!"),
            validators.NumberRange(min=1.00, message="Unit Price must be a minimum of Kshs 1.00"),
        ],

    )

    description = StringField(
        "Product Description",
        [validators.DataRequired("Product Description is required!")],
    )
    product_category = StringField(
        "Product Category", [validators.DataRequired("Product Category is required!")]
    )

    available_colors = StringField(
        "Available Color",
        [validators.DataRequired("Product Available Colors is required!")],
    )

    is_available = BooleanField(
        "Product Is Available",
        [],
    )


class ProductUpdateForm(FlaskForm):
    """A form representing Product update"""

    product_id = StringField(
        "Product ID", [validators.DataRequired("Product ID is required!")]
    )
    product_name = StringField(
        "Product Name", [validators.DataRequired("Product Name is required!")]
    )
    product_unit_price = StringField(
        "Product Unit Price",
        [validators.DataRequired("Product Unit Price is required!")],
    )

    description = StringField(
        "Product Description",
        [validators.DataRequired("Product Description is required!")],
    )
    product_category = StringField(
        "Product Category", [validators.DataRequired("Product Category is required!")]
    )

    available_colors = StringField(
        "Available Color",
        [validators.DataRequired("Product Available Colors is required!")],
    )

    is_available = BooleanField(
        "Product Is Available",
        [validators.DataRequired("Product Availability is required!")],
    )
