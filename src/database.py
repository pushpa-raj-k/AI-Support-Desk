from pathlib import Path
import sqlite3
from datetime import datetime


# ---------------------------------------------------------
# Database configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATA_DIR / "supportdesk.db"


# ---------------------------------------------------------
# Database connection
# ---------------------------------------------------------

def get_connection():
    """
    Create a connection to the SQLite database.
    """
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ---------------------------------------------------------
# Initialize database
# ---------------------------------------------------------

def initialize_database():
    """
    Create the tickets table if it does not exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            subject TEXT NOT NULL,

            body TEXT NOT NULL,

            category TEXT NOT NULL,

            priority TEXT NOT NULL,

            department TEXT NOT NULL,

            confidence REAL NOT NULL,

            human_review INTEGER NOT NULL,

            suggested_response TEXT,

            status TEXT NOT NULL DEFAULT 'Open',

            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


# ---------------------------------------------------------
# Save ticket
# ---------------------------------------------------------

def save_ticket(result):
    """
    Save a complete analyzed ticket.
    """

    connection = get_connection()

    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        INSERT INTO tickets (
            subject,
            body,
            category,
            priority,
            department,
            confidence,
            human_review,
            suggested_response,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result["subject"],
            result["body"],
            result["category"],
            result["priority"],
            result["department"],
            result["confidence"],
            int(result["needs_human_review"]),
            result["suggested_response"],
            "Open",
            created_at,
        ),
    )

    ticket_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return ticket_id


# ---------------------------------------------------------
# Get all tickets
# ---------------------------------------------------------

def get_all_tickets():
    """
    Retrieve all tickets from newest to oldest.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tickets
        ORDER BY id DESC
        """
    )

    tickets = cursor.fetchall()

    connection.close()

    return tickets


# ---------------------------------------------------------
# Get ticket by ID
# ---------------------------------------------------------

def get_ticket(ticket_id):
    """
    Retrieve one ticket by ID.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,),
    )

    ticket = cursor.fetchone()

    connection.close()

    return ticket


# ---------------------------------------------------------
# Update ticket status
# ---------------------------------------------------------

def update_ticket_status(
    ticket_id,
    status,
):
    """
    Update ticket status.
    """

    allowed_statuses = [
        "Open",
        "In Progress",
        "Resolved",
    ]

    if status not in allowed_statuses:
        raise ValueError(
            f"Invalid status: {status}"
        )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tickets
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            ticket_id,
        ),
    )

    connection.commit()

    connection.close()


# ---------------------------------------------------------
# Initialize when module is used
# ---------------------------------------------------------

initialize_database()


# ---------------------------------------------------------
# Local test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("AI SUPPORTDESK - DATABASE TEST")
    print("=" * 60)

    test_result = {
        "subject": "Test support ticket",
        "body": "This is a database test ticket.",
        "category": "Technical Support",
        "priority": "Medium",
        "department": "Technical Support",
        "confidence": 82.5,
        "needs_human_review": False,
        "suggested_response": (
            "Thank you for contacting support. "
            "We are looking into your issue."
        ),
    }

    ticket_id = save_ticket(
        test_result
    )

    print(
        f"\nTicket saved successfully."
    )

    print(
        f"Ticket ID: {ticket_id}"
    )

    ticket = get_ticket(
        ticket_id
    )

    print("\nRetrieved ticket:")

    print(
        f"ID: {ticket['id']}"
    )

    print(
        f"Subject: {ticket['subject']}"
    )

    print(
        f"Category: {ticket['category']}"
    )

    print(
        f"Priority: {ticket['priority']}"
    )

    print(
        f"Department: {ticket['department']}"
    )

    print(
        f"Confidence: {ticket['confidence']}%"
    )

    print(
        f"Status: {ticket['status']}"
    )

    print(
        f"Created: {ticket['created_at']}"
    )

    print("\n" + "=" * 60)
    print("DATABASE TEST SUCCESSFUL")
    print("=" * 60)