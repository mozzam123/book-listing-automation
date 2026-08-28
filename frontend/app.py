import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Book Listing Automation",
    page_icon="📚",
)

st.title("Add New Book")

isbn = st.text_input(
    "Scan ISBN",
    placeholder="Scan or enter ISBN...",
)

if st.button("Search Book"):
    if not isbn.strip():
        st.warning("Please scan or enter an ISBN.")
    else:
        response = requests.post(
            f"{API_URL}/books/lookup",
            json={"isbn": isbn},
            timeout=15,
        )

        result = response.json()

        if not result["found"]:
            st.error(result["error"])
        else:
            st.session_state["book"] = result["data"]


book = st.session_state.get("book")

if book:
    st.success("Book found!")

    st.subheader("Book Information")

    title = st.text_input(
        "Title",
        value=book.get("title") or "",
    )

    subtitle = st.text_input(
        "Subtitle",
        value=book.get("subtitle") or "",
    )

    authors = st.text_input(
        "Authors",
        value=", ".join(book.get("authors", [])),
    )

    publisher = st.text_input(
        "Publisher",
        value=book.get("publisher") or "",
    )

    publication_date = st.text_input(
        "Publication Date",
        value=book.get("publication_date") or "",
    )

    page_count = st.number_input(
        "Pages",
        min_value=0,
        value=book.get("page_count") or 0,
    )

    isbn_10 = st.text_input(
        "ISBN-10",
        value=book.get("isbn_10") or "",
    )

    isbn_13 = st.text_input(
        "ISBN-13",
        value=book.get("isbn_13") or "",
    )

    language = st.text_input(
        "Language",
        value=book.get("language") or "",
    )

    categories = st.text_input(
        "Categories",
        value=", ".join(book.get("categories", [])),
    )

    description = st.text_area(
        "Description",
        value=book.get("description") or "",
    )

    cover_image_url = st.text_input(
        "Cover Image URL",
        value=book.get("cover_image_url") or "",
    )

    if cover_image_url:
        st.image(cover_image_url, width=180)

    st.subheader("Seller Information")

    selling_price = st.number_input(
        "Selling Price",
        min_value=0.0,
        step=10.0,
    )

    original_price = st.number_input(
        "Original Price",
        min_value=0.0,
        step=10.0,
    )

    stock = st.number_input(
        "Stock",
        min_value=1,
        value=1,
        step=1,
    )

    condition = st.selectbox(
        "Condition",
        [
            "Pre-owned",
            "Used",
            "Good",
            "Very Good",
            "Like New",
        ],
    )

    condition_notes = st.text_area(
        "Condition Notes",
    )

    if st.button("Review Product"):
        st.session_state["product"] = {
            "book": {
                "isbn_10": isbn_10,
                "isbn_13": isbn_13,
                "title": title,
                "subtitle": subtitle,
                "authors": [
                    author.strip() for author in authors.split(",") if author.strip()
                ],
                "publisher": publisher,
                "publication_date": publication_date,
                "description": description,
                "page_count": page_count,
                "categories": [
                    category.strip()
                    for category in categories.split(",")
                    if category.strip()
                ],
                "language": language,
                "cover_image_url": cover_image_url,
            },
            "seller": {
                "selling_price": selling_price,
                "original_price": original_price,
                "stock": stock,
                "condition": condition,
                "condition_notes": condition_notes,
            },
        }

        st.success("Product information ready.")
