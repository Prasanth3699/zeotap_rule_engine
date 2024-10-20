# Rule Engine with AST

## Overview

This project is a rule engine application that allows dynamic evaluation of user eligibility based on attributes like age, department, income, spend, etc. For example, a financial institution could use the rule engine to determine whether a user qualifies for a loan based on their income, credit score, and employment status. This flexibility allows businesses to dynamically adjust their eligibility criteria to meet changing requirements. The system is designed with a 3-tier architecture, including a simple UI, an API layer, and a backend for data management. The 3-tier architecture was chosen for its benefits such as separation of concerns, scalability, and ease of maintenance. This design helps ensure that each layer can be developed, tested, and maintained independently, leading to a more robust and scalable application. The rule engine leverages an Abstract Syntax Tree (AST) to represent and manipulate conditional rules, allowing for dynamic rule creation, combination, and modification.

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

## Design Choices

### Abstract Syntax Tree (AST) for Rule Evaluation

The rule engine utilizes an Abstract Syntax Tree (AST) to efficiently represent and evaluate complex conditional expressions. An AST is a tree-like representation of the syntactic structure of code, where each node represents a construct occurring in the source code. This allows for easy manipulation and evaluation of the rules. Using AST provides flexibility to dynamically create, modify, and combine rules. It also allows for:

- **Modularity**: Each part of the rule is represented as a node, making it easier to modify individual components.
- **Error Handling**: AST parsing helps in identifying syntax errors early during rule creation.
- **Dynamic Evaluation**: The AST can be easily traversed and evaluated based on the given user data, making it ideal for dynamic rule evaluations.

### 3-Tier Architecture

The application is designed using a 3-tier architecture to separate concerns:

1. **Frontend (Client Tier)**: The UI is built using React with Vite and TailwindCSS to provide a user-friendly interface for rule creation, combination, and evaluation.
2. **API Layer (Middle Tier)**: The API is built using Django REST Framework, serving as the intermediary between the frontend and backend. This layer handles rule management, combination, and evaluation requests.
3. **Backend (Data Tier)**: The backend consists of a Django application with an SQLite database for storing rules and application metadata. The use of Django's ORM simplifies database interactions.

### Error Handling

Custom error handling is implemented to manage scenarios like invalid rule syntax, missing attributes, or incorrect data types. For example, if a user attempts to create a rule with an undefined attribute, they will receive an error message like 'Invalid attribute: The attribute "age_group" is not recognized.' This ensures a smooth user experience and provides meaningful feedback when errors occur. This ensures a smooth user experience and provides meaningful feedback when errors occur.

## Usage

- **Create Rules**: Use the UI or API to define conditional rules for evaluating user data.
- **Combine Rules**: Combine existing rules using logical operators to form more complex eligibility criteria.
- **Evaluate Rules**: Use user-provided data to evaluate if it meets the conditions defined in the rules.
