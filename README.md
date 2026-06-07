# 📦 Warehouse Inventory Management System

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![DSA](https://img.shields.io/badge/DSA-BST%20%7C%20Queue%20%7C%20Stack-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A smart warehouse inventory management system built with **Python**, leveraging **Data Structures & Algorithms (DSA)** to optimize inventory lookup, stock-in, stock-out, and expiry management.

---

## 📑 Table of Contents

* [Overview](#-overview)
* [Core Data Structures](#-core-data-structures)
* [Project Architecture](#-project-architecture)
* [Directory Structure](#-directory-structure)
* [Core Features](#-core-features)
* [Installation Guide](#-installation-guide)
* [Environment Configuration](#-environment-configuration)
* [Running the Application](#-running-the-application)
* [Testing](#-testing)
* [Future Improvements](#-future-improvements)

---

# 🎯 Overview

Traditional inventory systems often rely heavily on database queries for every operation.

This project introduces an **in-memory inventory management architecture**, where products and batches are loaded into RAM using custom-built data structures. This approach significantly improves lookup and transaction performance while demonstrating practical applications of DSA concepts.

---

# 🏗️ Core Data Structures

## 1️⃣ Binary Search Tree (BST)

Used for managing the product catalog.

### Responsibilities

* Insert products
* Search products by barcode
* Delete products
* In-order traversal for sorted listing

### Time Complexity

| Operation | Complexity |
| --------- | ---------- |
| Search    | O(log n)   |
| Insert    | O(log n)   |
| Delete    | O(log n)   |

---

## 2️⃣ Queue (FIFO)

Used for products configured with:

> First In - First Out (FIFO)

Suitable for:

* Food
* Medicine
* Perishable goods

The oldest batch is always consumed first.

---

## 3️⃣ Stack (LIFO)

Used for products configured with:

> Last In - First Out (LIFO)

Suitable for:

* Palletized goods
* Stacked warehouse storage

The newest batch is consumed first.

---

# 🏛️ Project Architecture

The project follows a layered architecture:

```text
┌───────────────────────┐
│        API Layer      │
└──────────┬────────────┘
           │
┌──────────▼────────────┐
│    Service Layer      │
└──────────┬────────────┘
           │
┌──────────▼────────────┐
│      DSA Layer        │
│ BST • Queue • Stack   │
└──────────┬────────────┘
           │
┌──────────▼────────────┐
│    Database Layer     │
└───────────────────────┘
```

---

# 📂 Directory Structure

```text
warehouse_management/
├── app
│   ├── api
│   │   ├── routes.py
│   │   └── __init__.py
│   ├── dsa
│   │   ├── bst.py
│   │   ├── queue.py
│   │   ├── stack.py
│   │   └── __init__.py
│   ├── models
│   │   ├── db_models.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   ├── services
│   │   ├── expiry_service.py
│   │   ├── inventory_service.py
│   │   └── __init__.py
│   ├── database.py
│   └── __init__.py
├── tests
│   ├── conftest.py
│   ├── test_bst.py
│   └── test_inventory.py
├── ui
│   ├── assets
│   ├── components
│   └── main_window.py
├── .gitignore
├── Command_Guild.txt
├── main.py
├── README.md
├── requirements.txt
├── settings.json
└── StructureProject.txt

```

---

## 📁 Folder Responsibilities

| Folder       | Description                                 |
| ------------ | ------------------------------------------- |
| app/dsa      | Core DSA implementation (BST, Queue, Stack) |
| app/models   | Database models and Pydantic schemas        |
| app/services | Business logic layer                        |
| app/api      | API endpoints and routers                   |
| tests        | Automated unit and integration tests        |
| main.py      | Application entry point                     |

---

# 🚀 Core Features

## 📦 Product Catalog Management

* Add products
* Search by barcode
* Delete products
* Sorted product listing

---

## 📥 Batch Stock-In

Each inventory batch stores:

* Batch ID
* Quantity
* Received Date
* Expiry Date

---

## 📤 Automated Stock-Out

Supports:

* FIFO allocation
* LIFO allocation
* Partial batch consumption
* Automatic rollback when stock is insufficient

---

## ⏰ Expiry Warning System

Automatically scans inventory and identifies:

* Expired batches
* Near-expiry batches
* Products expiring within configurable thresholds

Default threshold:

```text
30 Days
```

---

## 📋 Audit Logging

Records every inventory transaction:

* Product movements
* Stock adjustments
* User actions
* Timestamp history

---

# ⚙️ Installation Guide

## 1. Clone Repository

```bash
git clone https://github.com/YourUsername/Warehouse-Inventory-Management.git

cd Warehouse-Inventory-Management
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔧 Environment Configuration

Create a file named:

```text
.env
```

Example:

```env
DATABASE_URL=sqlite:///./warehouse.db

ENVIRONMENT=development

DEBUG=True
```

---

# ▶️ Running the Application

Start the application:

```bash
python main.py
```

If using FastAPI:

```bash
uvicorn main:app --reload
```

Server will be available at:

```text
http://127.0.0.1:8000
```

Swagger API Documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🧪 Testing

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

---

# 📈 Future Improvements

* AVL Tree / Red-Black Tree balancing
* Multi-warehouse support
* Real-time dashboard
* Barcode scanner integration
* User authentication & authorization
* Export reports to Excel/PDF
* Inventory forecasting using Machine Learning

---

# 👨‍💻 Tech Stack

| Layer         | Technology                  |
| ------------- | --------------------------- |
| Language      | Python 3.10+                |
| API Framework | FastAPI                     |
| ORM           | SQLAlchemy                  |
| Validation    | Pydantic                    |
| Database      | SQLite / PostgreSQL / MySQL |
| Testing       | Pytest                      |
| DSA           | BST, Queue, Stack           |

---

# 📜 License

This project is licensed under the MIT License.

---

⭐ If you find this project useful, consider giving it a star on GitHub.
