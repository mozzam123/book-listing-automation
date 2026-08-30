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
                "Unable to connect to the backend. " "Please try again."
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

    subtitle = st.text_input(
        "Subtitle",
        value=book.get("subtitle") if book else "",
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

    categories = st.text_input(
        "Categories",
        value=", ".join(book.get("categories", [])) if book else "",
    )

    description = st.text_area(
        "Description",
        value=book.get("description") if book else "",
    )

    cover_image_url = st.text_input(
        "Cover Image URL",
        value=book.get("cover_image_url") if book else "",
    )

    if cover_image_url:
        st.image(cover_image_url, width=180)

    asin = st.text_input(
        "ASIN",
        value=book.get("asin", "") if book else "",
    )

    format = st.text_input(
        "Format",
        value=book.get("format", "") if book else "",
    )

    edition = st.text_input(
        "Edition",
        value=book.get("edition", "") if book else "",
    )

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
                "asin": asin,
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
                "format": format,
                "edition": edition,
                "reading_age": reading_age,
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
