```python
# Import Python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from cryptography.hazmat.primitives import serialization

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

# Instructions
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Load Snowflake connection settings
config = dict(st.secrets["connections"]["snowflake"])

# Convert PEM private key to DER bytes
private_key_pem = config.pop("private_key")

private_key_obj = serialization.load_pem_private_key(
    private_key_pem.encode("utf-8"),
    password=None,
)

config["private_key"] = private_key_obj.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

# Create Snowpark session
session = Session.builder.configs(config).create()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options")

fruit_options = [
    row["FRUIT_NAME"]
    for row in my_dataframe.select(col("FRUIT_NAME")).collect()
]

# Select up to 5 ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5
)

# Submit the order
if ingredients_list:
    if st.button("Submit Order"):
        ingredients_string = ", ".join(ingredients_list)

        try:
            # Insert ingredients and smoothie name into Snowflake
            session.sql(
                """
                INSERT INTO smoothies.public.orders
                    (INGREDIENTS, NAME_ON_ORDER)
                SELECT ?, ?
                """,
                params=[ingredients_string, name_on_order]
            ).collect()

            # Show confirmation with the smoothie name
            if name_on_order.strip():
                st.success(
                    f"Your Smoothie is ordered, {name_on_order}! 🥤"
                )
            else:
                st.success("Your Smoothie is ordered! 🥤")

        except Exception as e:
            st.error(f"Unable to place your order: {e}")
```
