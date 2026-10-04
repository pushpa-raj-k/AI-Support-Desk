import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# Add src directory to Python path
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ---------------------------------------------------------
# Import project modules
# ---------------------------------------------------------

from analyzer import analyze_ticket
from database import (
    get_all_tickets,
    update_ticket_status,
)


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI SupportDesk",
    page_icon="🎧",
    layout="wide",
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #666666;
        margin-bottom: 25px;
    }

    .metric-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dddddd;
        text-align: center;
    }

    .response-box {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dddddd;
        background-color: #f5f5f5;
        color: #222222;
        font-size: 16px;
        line-height: 1.6;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">🎧 AI SupportDesk</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Intelligent customer support ticket classification "
    "and response generation"
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Analyze Ticket",
        "Dashboard",
        "Ticket History",
    ],
)


# =========================================================
# ANALYZE TICKET
# =========================================================

if page == "Analyze Ticket":

    st.header("Analyze Support Ticket")

    st.write(
        "Enter a customer support ticket below. "
        "The AI system will classify it, determine "
        "priority, route it to the appropriate department, "
        "and generate a suggested response."
    )

    st.divider()

    # -----------------------------------------------------
    # Input fields
    # -----------------------------------------------------

    subject = st.text_input(
        "Ticket Subject",
        placeholder=(
            "Example: Payment deducted but order failed"
        ),
    )

    body = st.text_area(
        "Customer Message",
        height=180,
        placeholder=(
            "Describe the customer's issue here..."
        ),
    )

    analyze_button = st.button(
        "🔍 Analyze Ticket",
        type="primary",
        use_container_width=True,
    )

    # -----------------------------------------------------
    # Analyze
    # -----------------------------------------------------

    if analyze_button:

        if not subject.strip() and not body.strip():

            st.error(
                "Please enter a ticket subject or message."
            )

        else:

            with st.spinner(
                "Analyzing ticket and generating response..."
            ):

                try:

                    result = analyze_ticket(
                        subject=subject,
                        body=body,
                    )

                    st.session_state[
                        "latest_result"
                    ] = result

                except Exception as error:

                    st.error(
                        f"Analysis failed: {error}"
                    )


    # -----------------------------------------------------
    # Display latest result
    # -----------------------------------------------------

    if "latest_result" in st.session_state:

        result = st.session_state[
            "latest_result"
        ]

        st.divider()

        st.subheader(
            f"Ticket #{result['ticket_id']} — AI Analysis"
        )

        # -------------------------------------------------
        # Metrics
        # -------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Category",
                result["category"],
            )

        with col2:

            st.metric(
                "Priority",
                result["priority"],
            )

        with col3:

            st.metric(
                "Department",
                result["department"],
            )

        with col4:

            st.metric(
                "Confidence",
                f"{result['confidence']}%",
            )

        # -------------------------------------------------
        # Human review
        # -------------------------------------------------

        st.write("")

        if result["needs_human_review"]:

            st.warning(
                "⚠️ Low classification confidence. "
                "This ticket should be reviewed by a human agent."
            )

        else:

            st.success(
                "✅ Classification confidence is sufficient "
                "for automated routing."
            )

        # -------------------------------------------------
        # Suggested response
        # -------------------------------------------------

        st.subheader(
            "💬 Suggested Customer Response"
        )

        st.markdown(
            f"""
            <div class="response-box">
            {result["suggested_response"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "The response is AI-generated and should be "
            "reviewed before sending to the customer."
        )


# =========================================================
# DASHBOARD
# =========================================================

elif page == "Dashboard":

    st.header("📊 Support Dashboard")

    tickets = get_all_tickets()

    if not tickets:

        st.info(
            "No tickets have been analyzed yet."
        )

    else:

        # -------------------------------------------------
        # Convert database rows to DataFrame
        # -------------------------------------------------

        df = pd.DataFrame(
            [dict(ticket) for ticket in tickets]
        )

        # -------------------------------------------------
        # Metrics
        # -------------------------------------------------

        total_tickets = len(df)

        critical_tickets = len(
            df[
                df["priority"] == "Critical"
            ]
        )

        human_review = int(
            df["human_review"].sum()
        )

        resolved_tickets = len(
            df[
                df["status"] == "Resolved"
            ]
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Tickets",
                total_tickets,
            )

        with col2:

            st.metric(
                "Critical Tickets",
                critical_tickets,
            )

        with col3:

            st.metric(
                "Human Review",
                human_review,
            )

        with col4:

            st.metric(
                "Resolved",
                resolved_tickets,
            )

        st.divider()

        # -------------------------------------------------
        # Category chart
        # -------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "Tickets by Category"
            )

            category_counts = (
                df["category"]
                .value_counts()
                .reset_index()
            )

            category_counts.columns = [
                "Category",
                "Count",
            ]

            fig_category = px.bar(
                category_counts,
                x="Count",
                y="Category",
                orientation="h",
                title="Ticket Categories",
            )

            st.plotly_chart(
                fig_category,
                use_container_width=True,
            )

        # -------------------------------------------------
        # Priority chart
        # -------------------------------------------------

        with col2:

            st.subheader(
                "Tickets by Priority"
            )

            priority_counts = (
                df["priority"]
                .value_counts()
                .reset_index()
            )

            priority_counts.columns = [
                "Priority",
                "Count",
            ]

            fig_priority = px.pie(
                priority_counts,
                names="Priority",
                values="Count",
                title="Priority Distribution",
            )

            st.plotly_chart(
                fig_priority,
                use_container_width=True,
            )

        # -------------------------------------------------
        # Department chart
        # -------------------------------------------------

        st.subheader(
            "Tickets by Department"
        )

        department_counts = (
            df["department"]
            .value_counts()
            .reset_index()
        )

        department_counts.columns = [
            "Department",
            "Count",
        ]

        fig_department = px.bar(
            department_counts,
            x="Department",
            y="Count",
            title="Department Workload",
        )

        st.plotly_chart(
            fig_department,
            use_container_width=True,
        )


# =========================================================
# TICKET HISTORY
# =========================================================

elif page == "Ticket History":

    st.header("📋 Ticket History")

    tickets = get_all_tickets()

    if not tickets:

        st.info(
            "No tickets have been analyzed yet."
        )

    else:

        df = pd.DataFrame(
            [dict(ticket) for ticket in tickets]
        )

        # -------------------------------------------------
        # Filters
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            categories = [
                "All"
            ] + sorted(
                df["category"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_category = st.selectbox(
                "Category",
                categories,
            )

        with col2:

            priorities = [
                "All"
            ] + sorted(
                df["priority"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_priority = st.selectbox(
                "Priority",
                priorities,
            )

        with col3:

            statuses = [
                "All"
            ] + sorted(
                df["status"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_status = st.selectbox(
                "Status",
                statuses,
            )

        # -------------------------------------------------
        # Apply filters
        # -------------------------------------------------

        filtered_df = df.copy()

        if selected_category != "All":

            filtered_df = filtered_df[
                filtered_df["category"]
                == selected_category
            ]

        if selected_priority != "All":

            filtered_df = filtered_df[
                filtered_df["priority"]
                == selected_priority
            ]

        if selected_status != "All":

            filtered_df = filtered_df[
                filtered_df["status"]
                == selected_status
            ]

        st.divider()

        # -------------------------------------------------
        # Display tickets
        # -------------------------------------------------

        st.write(
            f"Showing {len(filtered_df)} ticket(s)"
        )

        for _, ticket in filtered_df.iterrows():

            with st.expander(
                f"#{ticket['id']} — "
                f"{ticket['subject']}"
            ):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        "**Category:**",
                        ticket["category"],
                    )

                    st.write(
                        "**Department:**",
                        ticket["department"],
                    )

                with col2:

                    st.write(
                        "**Priority:**",
                        ticket["priority"],
                    )

                    st.write(
                        "**Confidence:**",
                        f"{ticket['confidence']}%",
                    )

                with col3:

                    st.write(
                        "**Created:**",
                        ticket["created_at"],
                    )

                    st.write(
                        "**Status:**",
                        ticket["status"],
                    )

                st.write(
                    "**Customer Message:**"
                )

                st.write(
                    ticket["body"]
                )

                st.write(
                    "**Suggested Response:**"
                )

                st.info(
                    ticket["suggested_response"]
                )

                # -----------------------------------------
                # Status update
                # -----------------------------------------

                status_options = [
                    "Open",
                    "In Progress",
                    "Resolved",
                ]

                current_status = ticket["status"]

                new_status = st.selectbox(
                    "Update Status",
                    status_options,
                    index=status_options.index(
                        current_status
                    ),
                    key=f"status_{ticket['id']}",
                )

                if new_status != current_status:

                    if st.button(
                        "Update Status",
                        key=f"update_{ticket['id']}",
                    ):

                        update_ticket_status(
                            int(ticket["id"]),
                            new_status,
                        )

                        st.success(
                            "Ticket status updated."
                        )

                        st.rerun()