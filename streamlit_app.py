
# Import Python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

# Instructions
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Get the active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()
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
