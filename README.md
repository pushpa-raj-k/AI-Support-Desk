# AI SupportDesk

An intelligent customer support ticket classification and response system built with Python, Scikit-learn, Gemini API, SQLite, and Streamlit.

AI SupportDesk analyzes incoming customer support tickets, predicts the most appropriate support category, determines priority, routes the ticket to a department, flags uncertain tickets for human review, and generates a professional suggested customer response.

## Features

- Automated support ticket classification
- Word-level and character-level TF-IDF NLP features
- LinearSVC machine learning classifier
- 10 support categories
- Automated priority detection
- Department routing
- Human-review flag for low-confidence predictions
- Gemini-powered suggested customer responses
- SQLite ticket storage
- Ticket history and status management
- Interactive Streamlit dashboard
- Category, priority, department, and resolution analytics

## System Architecture

```text
Customer Ticket
      |
      v
+----------------------+
|   NLP / ML Pipeline  |
| Word + Character     |
| TF-IDF + LinearSVC   |
+----------+-----------+
           |
           v
   Ticket Classification
           |
     +-----+------+
     |            |
     v            v
 Priority     Department
 Detection    Routing
     |            |
     +-----+------+
           |
           v
    Human Review Check
           |
           v
+----------------------+
|    Gemini API        |
| Suggested Response   |
+----------+-----------+
           |
           v
+----------------------+
|       SQLite         |
|   Ticket Database    |
+----------+-----------+
           |
           v
+----------------------+
| Streamlit Dashboard  |
| History + Analytics  |
+----------------------+
```

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application and ML development |
| Scikit-learn | NLP and machine learning |
| TF-IDF | Text feature extraction |
| LinearSVC | Ticket category classification |
| Gemini API | Suggested response generation |
| Streamlit | Web interface and dashboard |
| SQLite | Ticket persistence |
| Plotly | Interactive charts |
| Pandas | Data processing |
| NumPy | Numerical operations |
| SciPy | Sparse feature matrix operations |
| Joblib | ML model persistence |
| python-dotenv | Environment variable management |

## Machine Learning

The classifier uses a hybrid TF-IDF representation:

### Word TF-IDF

Word-level features use:

```text
ngram_range = (1, 2)
max_features = 40,000
sublinear_tf = True
```

This captures individual words and common two-word phrases.

### Character TF-IDF

Character-level features use:

```text
analyzer = "char"
ngram_range = (3, 5)
max_features = 30,000
sublinear_tf = True
```

Character features help capture spelling variations, partial words, technical terms, and similar textual patterns.

The two sparse feature matrices are combined and passed to a LinearSVC classifier.

## Supported Ticket Categories

The model predicts among 10 categories:

- Billing and Payments
- Customer Service
- General Inquiry
- Human Resources
- IT Support
- Product Support
- Returns and Exchanges
- Sales and Pre-Sales
- Service Outages and Maintenance
- Technical Support

## Model Performance

The current model was trained and evaluated using an 80/20 train-test split.

```text
Training samples: 3,200
Test samples:       800

Accuracy: 58.38%
```

The model performs particularly well on categories such as Billing and Payments and Returns and Exchanges, while broader categories such as Customer Service and IT Support remain more challenging.

The current result is treated as a practical baseline for the application, with further model improvement planned.

## Priority Detection

Priority is determined using business rules based on ticket content.

Examples of critical indicators include:

- Server/system outage
- Security breach
- Fraud
- Data loss
- Account lock
- Payment failure
- Money deducted from an unsuccessful transaction

High-priority indicators include terms such as:

- Urgent
- ASAP
- Immediately
- Critical
- Emergency
- Failed
- Error
- Not working

Tickets that do not match critical or high-priority rules are assigned Medium priority.

## Department Routing

Predicted categories are mapped to operational departments:

| Category | Department |
|---|---|
| Billing and Payments | Billing |
| Customer Service | Customer Service |
| General Inquiry | Customer Service |
| Human Resources | HR |
| IT Support | IT |
| Product Support | Product Support |
| Returns and Exchanges | Returns |
| Sales and Pre-Sales | Sales |
| Service Outages and Maintenance | Operations |
| Technical Support | Technical Support |

## Human Review

The system uses the model's decision-margin-based confidence score to identify uncertain predictions.

```text
Confidence < 70%  -> Human Review Required
Confidence >= 70% -> No Human Review Flag
```

The displayed confidence is a model confidence score derived from the LinearSVC decision function. It is not a calibrated probability.

## Gemini Response Generation

Gemini is used after the ML analysis to generate a concise customer-facing response.

The response-generation prompt instructs the model to:

1. Acknowledge the customer's issue
2. Show empathy when appropriate
3. Provide a useful next step
4. Avoid inventing policies, refunds, compensation, timelines, or technical facts
5. Avoid claiming that an action has already been completed
6. Ask for additional information when necessary
7. Remain concise and professional
8. Never mention AI or internal classification details

This creates a hybrid architecture where deterministic ML handles ticket classification while the LLM handles natural-language response generation.

## Project Structure

```text
AI-SupportDesk/
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
│
├── data/
│   └── supportdesk.db
│
├── models/
│   ├── word_vectorizer.joblib
│   ├── char_vectorizer.joblib
│   └── ticket_classifier.joblib
│
└── src/
    ├── __init__.py
    ├── predictor.py
    ├── gemini_service.py
    ├── analyzer.py
    └── database.py
```

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AI-SupportDesk
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Never commit `.env` or your API key to GitHub.

The project includes `.env.example` as a template.

## Run the Application

Start Streamlit:

```bash
streamlit run app.py
```

The application will open in your browser.

## Example Workflow

### Example 1 — Server Outage

**Input**

```text
Subject:
Server outage

Body:
Our service is completely down and users cannot access the system.
```

**Expected analysis**

```text
Category: Service Outages and Maintenance
Priority: Critical
Department: Operations
Human Review: True
```

### Example 2 — Product Return

**Input**

```text
Subject:
Need to return product

Body:
I would like to return the product and request a refund.
```

**Expected analysis**

```text
Category: Returns and Exchanges
Priority: Medium
Department: Returns
Human Review: False
```

## Dashboard

The Streamlit dashboard provides an overview of:

- Total tickets
- Critical tickets
- Tickets requiring human review
- Resolved tickets
- Ticket volume by category
- Priority distribution
- Department workload

## Ticket History

The Ticket History section allows users to:

- View previously analyzed tickets
- Filter by category
- Filter by priority
- Filter by status
- View predicted department
- View model confidence
- View suggested responses
- Update ticket status

Supported statuses:

```text
Open
In Progress
Resolved
```

## Security

- API credentials are stored in environment variables.
- `.env` is excluded from Git using `.gitignore`.
- API keys should never be hard-coded into Python files.
- The system does not expose the Gemini API key through the Streamlit interface.

## Limitations

The current implementation has several limitations:

- The training dataset is relatively small.
- Some support categories overlap semantically.
- The classifier's confidence score is not probability-calibrated.
- Priority detection currently relies on business rules.
- Gemini-generated responses depend on external API availability.
- SQLite is suitable for this prototype but would need to be replaced or upgraded for a large production workload.

## Future Improvements

Potential improvements include:

- Train a dedicated priority classifier
- Add sentiment analysis
- Improve category classification with larger real-world datasets
- Calibrate model probabilities
- Add authentication and role-based access
- Add REST API endpoints
- Add automated test coverage
- Add model monitoring
- Deploy using Streamlit Cloud or a cloud backend
- Replace SQLite with PostgreSQL for production-scale workloads
- Add feedback-based model retraining

## Why This Project?

AI SupportDesk demonstrates practical integration of:

- Machine learning
- Natural language processing
- Generative AI
- Database management
- Business-rule automation
- Data visualization
- Interactive web development

Rather than using an LLM for every task, the system combines traditional machine learning with generative AI. This makes the architecture easier to explain, test, and improve.

## Resume Highlights

- Built an AI-powered customer support platform using Python, Scikit-learn, Streamlit, SQLite, and Gemini API to automatically classify and route customer support tickets.
- Developed a hybrid NLP pipeline using word- and character-level TF-IDF with LinearSVC, achieving 58.38% test accuracy across 10 support categories.
- Integrated LLM-based response generation with automated priority detection, human-review flagging, persistent ticket history, and an interactive analytics dashboard.

## Interview Summary

A concise way to explain the project:

> "AI SupportDesk is a hybrid customer support automation system. I used word and character TF-IDF with LinearSVC to classify incoming support tickets into 10 categories. I then added business rules for priority and department routing, and integrated Gemini to generate a professional suggested response. The results are stored in SQLite and exposed through a Streamlit dashboard where support teams can review and update tickets."

## License

This project is intended for educational and portfolio purposes.
