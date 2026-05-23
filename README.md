# Maritime Email Extraction System

## Overview

The Maritime Email Extraction System is an intelligent platform developed to automatically extract structured maritime business information from unstructured shipping and chartering emails.

In the maritime industry, brokers, charterers, ship owners, and operators exchange thousands of emails daily. These emails contain important operational and commercial details such as:

* Cargo details
* Vessel information
* Laycan dates
* Load and discharge ports
* Delivery and redelivery
* DWT capacity
* Chartering terms
* Commission details
* Voyage instructions
* Tonnage positions

However, maritime emails are highly unstructured and vary significantly in format, abbreviations, language style, and broker writing patterns. Manual extraction of this information is time-consuming and error-prone.

This platform was developed to automate that process using a hybrid extraction architecture.

---

# Project Objective

The main goal of this project is:

* To reduce manual maritime email processing effort
* To automate extraction of voyage charter, time charter, and tonnage information
* To convert raw maritime emails into structured JSON data
* To improve operational efficiency for maritime chartering workflows
* To provide a searchable and analyzable maritime data platform

---

# Key Features

## Voyage Charter (VC) Extraction

Extracts:

* Cargo
* Quantity
* Load Port
* Discharge Port
* Laycan
* Freight terms
* Commission
* Cargo rates

---

## Time Charter (TC) Extraction

Extracts:

* Delivery
* Redelivery
* Duration
* DWT
* Vessel type
* Laycan
* Charter period
* Commission

---

## Tonnage Position Extraction

Extracts:

* Vessel Name
* Open Port
* Open Date
* DWT
* Vessel specifications
* Crane and grab information
* Speed and consumption

---

# Technology Stack

## Backend

* Python
* FastAPI

## Frontend

* Streamlit

## NLP & Extraction

* Regex-based semantic extraction
* Rule-based parsing
* Maritime routing engine
* Entity filtering
* Confidence scoring
* Segmentation engine

---

# Project Architecture

The platform uses a hybrid enterprise-style extraction pipeline:

Email Input
↓
Segmentation Engine
↓
Email Type Detection
↓
Specialized Parser
↓
Regex Extraction
↓
Semantic Validation
↓
Confidence Engine
↓
Structured JSON Output

---

# Supported Maritime Email Types

The system currently supports:

* Voyage Charter emails
* Time Charter emails
* Tonnage position emails
* Vessel specification emails
* Mixed broker-chain emails

---

# Major Components

## 1. Router Engine

Detects email type:

* VC
* TC
* TONNAGE
* VESSEL_SPEC

---

## 2. Segmentation Engine

Breaks large broker-chain emails into semantic blocks.

---

## 3. Specialized Parsers

Separate extraction logic for:

* VC Parser
* TC Parser
* Tonnage Parser

---

## 4. Confidence Engine

Scores extraction quality based on:

* Field completeness
* Semantic validity
* Maritime extraction rules

---

## 5. Maritime Search Dashboard

Provides:

* Maritime email upload
* Extraction display
* Structured analytics
* Search functionality

---

# Challenges Faced

Maritime emails are extremely difficult to process because:

* Every broker uses different formats
* Heavy abbreviation usage
* Mixed language styles
* Broken formatting
* Forwarded email chains
* Unstructured text
* Missing delimiters
* Multiple cargo fixtures in one email

Because of these challenges, achieving perfect extraction accuracy is extremely difficult in real-world maritime systems.

---

# Current System Strengths

The platform successfully:

* Detects maritime email types
* Extracts key operational fields
* Handles multiple broker formats
* Processes large maritime emails
* Generates structured JSON output
* Provides confidence-based extraction

---

# Future Improvements

Potential future enhancements include:

* Advanced NLP integration
* ML-based entity classification
* Better semantic ownership detection
* Improved broker-chain segmentation
* Real-time maritime analytics
* Historical trade intelligence
* Improved edge-case handling
* Enhanced extraction accuracy

---

# How to Run the Project

## Step 1 — Clone Repository

```bash
git clone <your-github-repo>
cd maritime-email-extractor
```

---

## Step 2 — Create Virtual Environment

```bash
python -m venv venv
```

---

## Step 3 — Activate Environment

### Windows

```bash
venv\Scripts\activate
```

---

## Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Backend

```bash
uvicorn api.app:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

---

# Run Frontend

```bash
streamlit run dashboard.py
```

Frontend URL:

```text
http://localhost:8501
```

---

# API Documentation

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

---

# Example Output

```json
{
  "email_type": "TC",
  "cargo": "Bulk Harmless Cargo",
  "dwt": "58K-60K",
  "delivery": "1SP WAFR",
  "redelivery": "1SP South China",
  "duration": "45-55 DAYS",
  "confidence_score": 92
}
```

---

# Learning Outcome

This project helped in understanding:

* Maritime business workflows
* Real-world unstructured data problems
* NLP pipeline design
* Enterprise parser architecture
* FastAPI backend development
* Streamlit dashboard integration
* Confidence-based extraction systems

---

# Conclusion

The Maritime Email Extraction System is an enterprise-style maritime intelligence platform designed to automate extraction of shipping and chartering information from complex maritime emails.

The project demonstrates practical implementation of:

* NLP
* Regex extraction
* Semantic routing
* Structured maritime analytics
* Hybrid parsing systems

for solving real-world maritime communication problems.
