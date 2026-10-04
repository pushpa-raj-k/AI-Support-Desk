from pathlib import Path

import joblib
import numpy as np
from scipy.sparse import hstack


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"

WORD_VECTORIZER_PATH = (
    MODEL_DIR / "word_vectorizer.joblib"
)

CHAR_VECTORIZER_PATH = (
    MODEL_DIR / "char_vectorizer.joblib"
)

MODEL_PATH = (
    MODEL_DIR / "ticket_classifier.joblib"
)


# ---------------------------------------------------------
# Load trained components
# ---------------------------------------------------------

def load_models():
    """
    Load the trained TF-IDF vectorizers and classifier.
    """

    if not WORD_VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            f"Word vectorizer not found:\n"
            f"{WORD_VECTORIZER_PATH}\n\n"
            "Run train_classifier.py first."
        )

    if not CHAR_VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            f"Character vectorizer not found:\n"
            f"{CHAR_VECTORIZER_PATH}\n\n"
            "Run train_classifier.py first."
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Classifier not found:\n"
            f"{MODEL_PATH}\n\n"
            "Run train_classifier.py first."
        )

    word_vectorizer = joblib.load(
        WORD_VECTORIZER_PATH
    )

    char_vectorizer = joblib.load(
        CHAR_VECTORIZER_PATH
    )

    model = joblib.load(
        MODEL_PATH
    )

    return (
        word_vectorizer,
        char_vectorizer,
        model,
    )


# ---------------------------------------------------------
# Department mapping
# ---------------------------------------------------------

QUEUE_TO_DEPARTMENT = {
    "Billing and Payments": "Billing",
    "Customer Service": "Customer Service",
    "General Inquiry": "Customer Service",
    "Human Resources": "HR",
    "IT Support": "IT",
    "Product Support": "Product Support",
    "Returns and Exchanges": "Returns",
    "Sales and Pre-Sales": "Sales",
    "Service Outages and Maintenance": "Operations",
    "Technical Support": "Technical Support",
}


# ---------------------------------------------------------
# Priority detection
# ---------------------------------------------------------

def determine_priority(text):
    """
    Determine ticket priority using business rules.

    This is intentionally rule-based rather than using
    the ML queue classifier.
    """

    text = text.lower()

    critical_keywords = [
        "server down",
        "system down",
        "service down",
        "outage",
        "security breach",
        "hacked",
        "fraud",
        "data loss",
        "cannot access",
        "can't access",
        "payment failed",
        "money deducted",
        "account locked",
    ]

    high_keywords = [
        "urgent",
        "asap",
        "immediately",
        "critical",
        "emergency",
        "not working",
        "failed",
        "error",
        "problem",
        "issue",
    ]

    if any(
        keyword in text
        for keyword in critical_keywords
    ):
        return "Critical"

    if any(
        keyword in text
        for keyword in high_keywords
    ):
        return "High"

    return "Medium"


# ---------------------------------------------------------
# Prediction
# ---------------------------------------------------------

def predict_ticket(subject, body):
    """
    Predict the queue/category for a support ticket.

    Returns:
        dictionary containing:
        - category
        - confidence
        - department
        - priority
        - needs_human_review
    """

    subject = str(subject or "").strip()
    body = str(body or "").strip()

    text = f"{subject} {body}".strip()

    if not text:
        raise ValueError(
            "Ticket subject/body cannot both be empty."
        )

    # Load model components.
    (
        word_vectorizer,
        char_vectorizer,
        model,
    ) = load_models()

    # -----------------------------------------------------
    # Transform text
    # -----------------------------------------------------

    word_features = word_vectorizer.transform(
        [text]
    )

    char_features = char_vectorizer.transform(
        [text]
    )

    combined_features = hstack([
        word_features,
        char_features,
    ])

    # -----------------------------------------------------
    # Predict category
    # -----------------------------------------------------

    prediction = model.predict(
        combined_features
    )[0]

    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------
    #
    # LinearSVC does not produce probabilities.
    #
    # decision_function gives scores for each class.
    # We convert the relative score into a soft confidence
    # value for UI / routing purposes.
    #
    # IMPORTANT:
    # This is NOT a calibrated probability.
    # -----------------------------------------------------

    decision_scores = model.decision_function(
        combined_features
    )[0]

    scores = np.asarray(
        decision_scores
    )

    # Handle binary classification safely.
    if scores.ndim == 0:
        confidence = float(
            1 / (1 + np.exp(-abs(scores)))
        )

    else:
        sorted_scores = np.sort(scores)

        best_score = sorted_scores[-1]

        second_best_score = sorted_scores[-2]

        margin = (
            best_score
            - second_best_score
        )

        # Convert margin into a bounded confidence-like score.
        confidence = (
            1 / (1 + np.exp(-margin))
        )

    confidence_percentage = round(
        confidence * 100,
        2,
    )

    # -----------------------------------------------------
    # Department
    # -----------------------------------------------------

    department = QUEUE_TO_DEPARTMENT.get(
        prediction,
        "General Support",
    )

    # -----------------------------------------------------
    # Priority
    # -----------------------------------------------------

    priority = determine_priority(
        text
    )

    # -----------------------------------------------------
    # Human review
    # -----------------------------------------------------

    needs_human_review = (
        confidence < 0.70
    )

    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {
        "category": prediction,
        "confidence": confidence_percentage,
        "priority": priority,
        "department": department,
        "needs_human_review": needs_human_review,
    }


# ---------------------------------------------------------
# Local testing
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("AI SUPPORTDESK - PREDICTION TEST")
    print("=" * 60)

    test_tickets = [
        {
            "subject": "Payment failed",
            "body": (
                "I tried to make a payment but "
                "the transaction failed."
            ),
        },
        {
            "subject": "Product not working",
            "body": (
                "The product I received is not "
                "working properly."
            ),
        },
        {
            "subject": "Server outage",
            "body": (
                "Our service is completely down "
                "and users cannot access the system."
            ),
        },
        {
            "subject": "Need to return product",
            "body": (
                "I would like to return the product "
                "and request a refund."
            ),
        },
    ]

    for index, ticket in enumerate(
        test_tickets,
        start=1,
    ):

        print("\n" + "-" * 60)

        print(
            f"TEST TICKET {index}"
        )

        print(
            f"Subject: {ticket['subject']}"
        )

        print(
            f"Body: {ticket['body']}"
        )

        try:

            result = predict_ticket(
                ticket["subject"],
                ticket["body"],
            )

            print("\nPrediction:")

            print(
                f"Category: "
                f"{result['category']}"
            )

            print(
                f"Confidence: "
                f"{result['confidence']}%"
            )

            print(
                f"Priority: "
                f"{result['priority']}"
            )

            print(
                f"Department: "
                f"{result['department']}"
            )

            print(
                f"Human Review: "
                f"{result['needs_human_review']}"
            )

        except Exception as error:

            print(
                f"\nPrediction failed: {error}"
            )