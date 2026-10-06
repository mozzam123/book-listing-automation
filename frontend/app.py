import requests
import streamlit as st
import os
import json
import time

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
)


@st.cache_data(ttl=300)
def get_categories():
    response = requests.get(
        f"{API_URL}/categories",
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


st.set_page_config(
    page_title="Book Listing Automation",
    page_icon="📚",
)

st.title("Add New Book")


# --------------------------------------------------
# ISBN Search
# --------------------------------------------------

isbn = st.text_input(
    "Scan ISBN",
    placeholder="Scan or enter ISBN...",
    key="isbn_input",
)


if st.button("Search Book"):
    if not isbn.strip():
        st.session_state["error"] = "Please scan or enter an ISBN."
        st.session_state["book"] = None
        st.session_state["manual_entry"] = False

    else:
        try:
            response = requests.post(
                f"{API_URL}/books/lookup",
                json={"isbn": isbn},
                timeout=15,
            )

            response.raise_for_status()
            result = response.json()

            if result.get("found"):
                st.session_state["book"] = result["data"]
                st.session_state["manual_entry"] = False
                st.session_state["error"] = None

            else:
                st.session_state["book"] = None
                st.session_state["manual_entry"] = True
                st.session_state["error"] = result.get(
                    "error",
                    "Book could not be found.",
                )

        except requests.exceptions.RequestException:
            st.session_state["book"] = None
            st.session_state["manual_entry"] = False
            st.session_state["error"] = (
                "Unable to connect to the backend. Please try again."
            )


book = st.session_state.get("book")
manual_entry = st.session_state.get("manual_entry", False)
error = st.session_state.get("error")


# --------------------------------------------------
# Error / Manual Entry
# --------------------------------------------------

if error and manual_entry:
    st.warning("Book not found in Google Books. " "Please enter the details manually.")

elif error:
    st.error(error)


# --------------------------------------------------
# Book Form
# --------------------------------------------------

if book is not None or manual_entry:

    if book is not None:
        st.success("Book found!")

    st.subheader("Book Information")

    title = st.text_input(
        "Title",
        value=book.get("title") if book else "",
    )

    authors = st.text_input(
        "Authors",
        value=", ".join(book.get("authors", [])) if book else "",
    )

    publisher = st.text_input(
        "Publisher",
        value=book.get("publisher") if book else "",
    )

    publication_date = st.text_input(
        "Publication Date",
        value=book.get("publication_date") if book else "",
    )

    page_count = st.number_input(
        "Pages",
        min_value=0,
        value=book.get("page_count") or 0 if book else 0,
    )

    isbn_10 = st.text_input(
        "ISBN-10",
        value=book.get("isbn_10") if book else "",
    )

    isbn_13 = st.text_input(
        "ISBN-13",
        value=book.get("isbn_13") if book else isbn,
    )

    language = st.text_input(
        "Language",
        value=(book.get("language") or "English") if book else "English",
    )

    try:
        available_categories = get_categories()

        category_map = {
            category["name"]: category["id"] for category in available_categories
        }

        category_names = list(category_map.keys())

        selected_category_names = st.multiselect(
            "Categories",
            category_names,
        )

        selected_category_ids = [category_map[name] for name in selected_category_names]

    except requests.exceptions.RequestException:
        st.error("Unable to load WooCommerce categories.")

        selected_category_names = []
        selected_category_ids = []

    description = st.text_area(
        "Description",
        value=book.get("description") if book else "",
    )

    binding = st.selectbox(
        "Binding",
        [
            "Paperback",
            "Hardcover",
        ],
        index=0,
    )

    cover_image_url = st.text_input(
        "Cover Image URL",
        value=book.get("cover_image_url") if book else "",
    )

    if cover_image_url:

        st.image(
            cover_image_url,
            caption="Google Books Cover",
            width=200,
        )

    uploaded_image = st.file_uploader(
        "Upload Custom Image (optional)",
        type=["jpg", "jpeg", "png", "webp"],
    )

    if uploaded_image:

        st.image(
            uploaded_image,
            caption="Custom Cover",
            width=200,
        )

    reading_age = st.text_input(
        "Reading Age",
        value=book.get("reading_age", "") if book else "",
    )

    # --------------------------------------------------
    # Seller Information
    # --------------------------------------------------

    st.subheader("Seller Information")

    original_price = st.number_input(
        "Original Price",
        min_value=0.0,
        step=10.0,
        value=None,
        placeholder="Enter original price",
    )

    selling_price = st.number_input(
        "Selling Price",
        min_value=0.0,
        step=10.0,
        value=None,
        placeholder="Enter selling price",
    )

    sku = st.text_input(
        "SKU",
        value="",
        placeholder="Enter SKU (optional)",
    )

    stock = st.number_input(
        "Stock",
        min_value=1,
        value=1,
        step=1,
    )

    # --------------------------------------------------
    # Create Product
    # --------------------------------------------------

    if st.button("Create Product"):
        product = {
            "book": {
                "isbn_10": isbn_10,
                "isbn_13": isbn_13,
                "title": title,
                "authors": [
                    author.strip() for author in authors.split(",") if author.strip()
                ],
                "publisher": publisher,
                "publication_date": publication_date,
                "language": language,
                "binding": binding,
                "page_count": page_count,
                "reading_age": reading_age,
                "description": description,
                "categories": selected_category_names,
                "cover_image_url": cover_image_url,
            },
            "seller": {
                "original_price": original_price,
                "selling_price": selling_price,
                "sku": sku,
                "stock": stock,
            },
            "category_ids": selected_category_ids,
        }

        files = None

        if uploaded_image:
            files = {
                "image": (
                    uploaded_image.name,
                    uploaded_image.getvalue(),
                    uploaded_image.type,
                )
            }

        try:
            response = requests.post(
                f"{API_URL}/books/products",
                data={"product": json.dumps(product)},
                files=files,
                timeout=60,
            )

            response.raise_for_status()
            created_product = response.json()

            st.success("Product created successfully in WooCommerce!")

            if created_product.get("id"):
                st.write(
                    f"**WooCommerce Product ID:** {created_product['id']}"
                )

            time.sleep(2)
            st.session_state.clear()
            st.rerun()

        except requests.exceptions.RequestException as exc:
            st.error("Failed to create the product in WooCommerce.")

            if exc.response is not None:
                st.error(exc.response.text)
