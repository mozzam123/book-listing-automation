# Automated Book Listing System

An automated book listing system that allows a seller to scan or enter a book's ISBN, automatically fetch book metadata from Google Books, review/edit the information, and publish the book as a product on a WooCommerce store.

The system is designed with a provider-based architecture so external services such as book metadata providers and e-commerce platforms can be replaced without changing the core business logic.

## Features

- ISBN-10 / ISBN-13 input and validation
- Barcode scanner support through keyboard emulation
- Automatic book metadata lookup using Google Books API
- Manual fallback when book metadata is unavailable
- Editable book information before publishing
- Cover image retrieval and upload to WordPress
- Dynamic WooCommerce category selection
- Seller information:
  - Selling price
  - Original price
  - Stock
- Product review before creation
- Automatic WooCommerce product creation
- Automatic product image attachment
- Formatted product description
- Separation between book metadata and seller/product information
- Provider/adapter-based architecture for external integrations

## Architecture

```text
Barcode Scanner / Manual ISBN
            |
            v
     Streamlit Frontend
            |
            | HTTP
            v
       FastAPI Backend
            |
            v
    Book Metadata Service
            |
            v
     Google Books Provider
            |
            v
      Normalized BookMetadata
            |
            v
       Review / Edit
            |
            v
      Product Information
            |
            v
      Product Service
            |
            v
    CommerceProvider
            |
            v
    WooCommerce Provider
            |
            +--------------------+
            |                    |
            v                    v
      WordPress Media      WooCommerce REST API
       Upload API             Product API

```
## Project Structure

```text
book-listing-automation/
│
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       │       ├── books.py
│       │       └── categories.py
│       │
│       ├── core/
│       │   └── config.py
│       │
│       ├── integrations/
│       │   ├── commerce.py
│       │   └── woocommerce.py
│       │
│       ├── models/
│       │   ├── book.py
│       │   └── product.py
│       │
│       ├── providers/
│       │   └── google_books.py
│       │
│       ├── schemas/
│       │   └── book.py
│       │
│       ├── services/
│       │   ├── book_metadata.py
│       │   ├── image.py
│       │   └── product.py
│       │
│       ├── utils/
│       │   └── isbn.py
│       │
│       └── main.py
│
├── frontend/
│   └── app.py
│
├── .gitignore
├── requirements.txt
└── README.md
```


## Tech Stack

### Backend
* Python
* FastAPI
* Pydantic
* HTTPX

### Frontend
* Streamlit

### External Services
* Google Books API
* WooCommerce REST API
* WordPress Media REST API


## Core Flow

### 1. ISBN Lookup
The user scans a barcode or enters an ISBN.

```text
ISBN
 ↓
FastAPI
 ↓
Google Books API
 ↓
BookMetadata
```

The Google Books response is normalized into the application's internal `BookMetadata` model instead of passing Google's response directly through the application.

### 2. Manual Fallback
If Google Books does not return a result, the user can manually enter the book information.

```text
ISBN
 ↓
Google Books
 ↓
Book Found?
 ├── Yes → Auto-fill metadata
 └── No  → Manual entry
```

The product creation flow does not depend entirely on external metadata availability.

### 3. Product Review
Before creating the WooCommerce product, the seller can review and modify:

* Title
* Author
* Publisher
* Publication date
* Pages
* ISBN-10
* ISBN-13
* Description
* Language
* Binding
* Categories
* Cover image
* Selling price
* Original price
* Stock

### 4. Product Creation
Once the product is reviewed, the backend:

1. Uploads the book cover to WordPress.
2. Creates the WooCommerce product.
3. Assigns the selected WooCommerce categories.
4. Sets pricing and stock.
5. Attaches the uploaded cover image.
6. Adds the formatted book description.


## Pricing

The application maps seller pricing to WooCommerce as:

* **Original Price** → WooCommerce Regular Price  
* **Selling Price** → WooCommerce Sale Price  

This allows the WooCommerce product to display the original price alongside the discounted selling price.

## Product Description

The generated WooCommerce description contains:

* About the Book
* Author
* Publisher
* Publication date
* Language
* Binding / pages
* ISBN-10
* ISBN-13

The same formatted content is currently used for both the WooCommerce long description and short description.

## Architecture

The project follows a few important system-design principles.

### Provider Pattern
External metadata providers are isolated from the rest of the application.

```text
BookMetadataService
        │
        ▼
GoogleBooksProvider
```

This makes it possible to add another metadata provider later without changing the rest of the business flow.

### Commerce Abstraction
WooCommerce is accessed through a commerce abstraction:

```text
ProductService
      │
      ▼
CommerceProvider
      │
      ▼
WooCommerceProvider
```

The core product service therefore does not need to know WooCommerce-specific API details. This makes the application easier to extend to another commerce platform in the future.

### Normalized Internal Model
External API responses are converted into the application's own model:

```text
Google Books JSON
       │
       ▼
GoogleBooksProvider
       │
       ▼
BookMetadata
```

This prevents external API structures from leaking into the rest of the application.

## Environment Variables

Create a `.env` file locally:

```env
GOOGLE_BOOKS_API_KEY=your_google_books_api_key

WOOCOMMERCE_URL=[https://your-store.com](https://your-store.com)
WOOCOMMERCE_CONSUMER_KEY=your_consumer_key
WOOCOMMERCE_CONSUMER_SECRET=your_consumer_secret

WORDPRESS_USERNAME=your_wordpress_username
WORDPRESS_APPLICATION_PASSWORD=your_application_password
```

> **Warning:** Never commit `.env` or API credentials to GitHub.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd book-listing-automation
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   * **macOS / Linux:**
     ```bash
     source .venv/bin/activate
     ```
   * **Windows:**
     ```bash
     .venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the environment variables** in `.env`.

## Running the Application

### Backend
From the backend directory:

```bash
cd backend
uvicorn app.main:app --reload
```

* **API URL:** `http://127.0.0.1:8000`
* **API Documentation:** `http://127.0.0.1:8000/docs`

### Frontend
From the project root:

```bash
streamlit run frontend/app.py
```

The Streamlit application will open in the browser.

---

## API Endpoints

### Book Lookup
```http
POST /books/lookup
```
Looks up book metadata using an ISBN.

### Product Creation
```http
POST /books/products
```
Creates a WooCommerce product using the reviewed book and seller information.

### Categories
```http
GET /categories
```
Fetches available product categories from WooCommerce.

---

## Security

Sensitive credentials are loaded through environment variables. The following should never be committed:

* `.env`
* API keys
* WooCommerce consumer secrets
* WordPress application passwords
