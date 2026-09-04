import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


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
        value=book.get("language") if book else "",
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
        st.image(cover_image_url, width=180)

    reading_age = st.text_input(
        "Reading Age",
        value=book.get("reading_age", "") if book else "",
    )

    # --------------------------------------------------
    # Seller Information
    # --------------------------------------------------

    st.subheader("Seller Information")

    selling_price = st.number_input(
        "Selling Price",
        step=10.0,
    )

    original_price = st.number_input(
        "Original Price",
        step=10.0,
    )

    stock = st.number_input(
        "Stock",
        min_value=1,
        value=1,
        step=1,
    )

    # --------------------------------------------------
    # Review Product
    # --------------------------------------------------

    if st.button("Review Product"):

        st.session_state["product"] = {
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
                "categories": [],
                "cover_image_url": cover_image_url,
            },
            "seller": {
                "selling_price": selling_price,
                "original_price": original_price,
                "stock": stock,
            },
            "category_ids": selected_category_ids,
        }

        st.session_state["review_mode"] = True


# --------------------------------------------------
# Product Review
# --------------------------------------------------

if st.session_state.get("review_mode"):

    product = st.session_state.get("product")

    if product:

        st.divider()
        st.subheader("Review Product")

        book_data = product["book"]
        seller_data = product["seller"]

        st.write("### Book Information")

        st.write(f"**Title:** {book_data['title']}")
        st.write(f"**Authors:** {', '.join(book_data['authors'])}")
        st.write(f"**Publisher:** {book_data['publisher']}")
        st.write(f"**Publication Date:** " f"{book_data['publication_date']}")
        st.write(f"**Language:** {book_data['language']}")
        st.write(f"**Binding:** {book_data['binding']}")
        st.write(f"**Pages:** {book_data['page_count']}")
        st.write(f"**ISBN-10:** {book_data['isbn_10']}")
        st.write(f"**ISBN-13:** {book_data['isbn_13']}")
        st.write(f"**Categories:** " f"{', '.join(book_data['categories'])}")
        st.write(f"**Reading Age:** {book_data['reading_age']}")

        st.write("### Description")

        st.write(book_data["description"] or "")

        if book_data["cover_image_url"]:
            st.image(
                book_data["cover_image_url"],
                width=180,
            )

        st.write("### Seller Information")

        st.write(f"**Selling Price:** " f"{seller_data['selling_price']}")
        st.write(f"**Original Price:** " f"{seller_data['original_price']}")
        st.write(f"**Stock:** {seller_data['stock']}")

        # --------------------------------------------------
        # Create Product
        # --------------------------------------------------

        if st.button("Create Product"):

            try:
                response = requests.post(
                    f"{API_URL}/books/products",
                    json=product,
                    timeout=30,
                )

                response.raise_for_status()

                created_product = response.json()

                st.success("Product created successfully in WooCommerce!")

                if created_product.get("id"):
                    st.write(f"**WooCommerce Product ID:** " f"{created_product['id']}")

                st.session_state["review_mode"] = False
                st.session_state["product"] = None

            except requests.exceptions.RequestException as exc:

                st.error("Failed to create the product in WooCommerce.")

                if exc.response is not None:
                    st.error(exc.response.text)
