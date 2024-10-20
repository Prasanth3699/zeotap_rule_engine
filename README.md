# Rule Engine with AST

## Overview

This project is a rule engine application that allows dynamic evaluation of user eligibility based on attributes like age, department, income, spend, etc. The system is designed with a 3-tier architecture, including a simple UI, an API layer, and a backend for data management. The rule engine leverages an Abstract Syntax Tree (AST) to represent and manipulate conditional rules, allowing for dynamic rule creation, combination, and modification.

The project features user-friendly functionality to create rules, combine multiple rules, and evaluate these rules against user-provided data.

## Features

- **Dynamic Rule Creation**: Users can create custom rules using a simple syntax.
- **Combine Rules**: Users can combine multiple rules using logical operators (AND/OR).
- **Evaluate Rules**: Evaluate user data against the defined rules to determine eligibility.
- **Error Handling**: Custom error handling for invalid rule formats or missing attributes.
- **Rule Modification**: Update existing rules by changing operators, operand values, or sub-expressions.

## Tech Stack

- **Frontend**: React, Vite, TailwindCSS
- **Backend**: Django, Django REST Framework
- **API**: RESTful API for rule management
- **Database**: SQLite for storing rules and application metadata

## Prerequisites

- Python 3.8+
- Node.js and npm

## Installation

### Backend Setup

#### 1. Clone the Repository

```bash
$ git clone https://github.com/Prasanth3699/zeotap_rule_engine.git
$ cd rule-engine
```

#### 2. Set Up a Virtual Environment

```bash
$ python -m venv venv
$ source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

#### 3. Install Dependencies

```bash
$ pip install -r requirements.txt
```

#### 4. Apply Database Migrations

```bash
$ python manage.py migrate
```

#### 5. Create a Superuser

To access the Django admin panel:

```bash
$ python manage.py createsuperuser
```

#### 6. Start the Development Server

```bash
$ python manage.py runserver
```

The server will be running on `http://127.0.0.1:8000/`.

### Frontend Setup

#### 1. Navigate to the Frontend Directory

```bash
$ cd rule-engine-frontend
```

#### 2. Install Dependencies

```bash
$ npm install
```

#### 3. Set Up Environment Variables

Create a `.env` file in the `frontend` directory and add the following variables:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1/
```

#### 4. Start the Development Server

```bash
$ npm run dev
```

The frontend will be running on `http://127.0.0.1:5173/`.

## API Endpoints

### Rule Management

- **POST** `api/v1/rules/` - Create a new rule.
- **GET** `api/v1/rules/` - List all rules.
- **PUT/PATCH** `api/v1/rules/{id}/` - Update an existing rule.
- **DELETE** `api/v1/rules/{id}/` - Delete a rule.

### Combine Rules

- **POST** `api/v1/rules/combine/` - Combine multiple rules into a new rule.

### Evaluate Rule

- **POST** `api/v1/rules/evaluate/` - Evaluate a rule against user-provided data.

## Usage

- **Create Rules**: Use the UI or API to define conditional rules for evaluating user data.
- **Combine Rules**: Combine existing rules using logical operators.
- **Evaluate Rules**: Use user-provided data to evaluate if it meets the conditions defined in the rules.
