from predictor import predict_ticket
from gemini_service import generate_support_response
from database import save_ticket

# ---------------------------------------------------------
# Analyze complete support ticket
# ---------------------------------------------------------

def analyze_ticket(subject, body):
    """
    Run the complete AI SupportDesk pipeline.

    Steps:
        1. Classify ticket
        2. Determine confidence
        3. Determine priority
        4. Route to department
        5. Generate Gemini response

    Returns:
        dictionary containing the complete analysis.
    """

    subject = str(subject or "").strip()
    body = str(body or "").strip()

    if not subject and not body:
        raise ValueError(
            "Please provide a ticket subject or message."
        )

    # -----------------------------------------------------
    # ML prediction
    # -----------------------------------------------------

    prediction = predict_ticket(
        subject=subject,
        body=body,
    )

    # -----------------------------------------------------
    # Extract prediction values
    # -----------------------------------------------------

    category = prediction["category"]

    confidence = prediction["confidence"]

    priority = prediction["priority"]

    department = prediction["department"]

    needs_human_review = prediction[
        "needs_human_review"
    ]

    # -----------------------------------------------------
    # Generate Gemini response
    # -----------------------------------------------------

    suggested_response = (
        generate_support_response(
            subject=subject,
            body=body,
            category=category,
            priority=priority,
            department=department,
            confidence=confidence,
        )
    )

    # -----------------------------------------------------
    # Complete result
    # -----------------------------------------------------

    result = {
        "subject": subject,
        "body": body,
        "category": category,
        "confidence": confidence,
        "priority": priority,
        "department": department,
        "needs_human_review": needs_human_review,
        "suggested_response": suggested_response,
    }

    # -----------------------------------------------------
    # Save to database
    # -----------------------------------------------------

    ticket_id = save_ticket(result)

    result["ticket_id"] = ticket_id

    return result

# ---------------------------------------------------------
# Local test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 65)
    print("AI SUPPORTDESK - COMPLETE PIPELINE TEST")
    print("=" * 65)

    subject = (
        "Payment deducted but order failed"
    )

    body = (
        "I tried to place an order today. "
        "The money was deducted from my account "
        "but the order failed. Please help me "
        "get my money back."
    )

    try:

        result = analyze_ticket(
            subject=subject,
            body=body,
        )

        print("\n" + "-" * 65)
        print("TICKET")
        print("-" * 65)

        print(
            f"Subject: {result['subject']}"
        )

        print(
            f"Message: {result['body']}"
        )

        print("\n" + "-" * 65)
        print("AI ANALYSIS")
        print("-" * 65)

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

        print("\n" + "-" * 65)
        print("GEMINI SUGGESTED RESPONSE")
        print("-" * 65)

        print(
            result["suggested_response"]
        )

        print("\n" + "=" * 65)
        print("PIPELINE TEST SUCCESSFUL")
        print("=" * 65)

    except Exception as error:

        print("\nPipeline failed:")

        print(error)