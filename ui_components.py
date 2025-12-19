"""
UI Components for Sabaza Optimizer
Handles all frontend interface elements and user input collection
"""

import streamlit as st

def draw_header():
    """
    Displays the app header with title and description.
    """
    # REMOVED st.set_page_config HERE because it is already in app.py

    st.title("📋 FieldScribe")
    st.markdown(
        """
        Generate professional, court-ready inspection reports with ease.

        **Features:**
        - Multi-language support (Hebrew → Arabic translation)
        - Instant Word document generation
        - Professional formatting
        """
    )
    st.divider()


def render_form():
    """
    Displays the main form for report generation.

    Returns:
        tuple: (client_name, translate_to_arabic, inspection_notes)
    """
    st.subheader("📝 Generate Your Report")

    # Client Name Input
    client_name = st.text_input(
        label="Client Name",
        placeholder="Enter the client/property name",
        help="The name that will appear in the report title"
    )

    # Translation Checkbox
    translate_to_arabic = st.checkbox(
        label="🌐 Translate to Arabic?",
        value=False,
        help="Check this box to automatically translate inspection notes from Hebrew to Arabic"
    )

    # Inspection Notes Text Area
    inspection_notes = st.text_area(
        label="Inspection Notes (Hebrew)",
        placeholder="Enter your inspection findings and observations here...",
        height=200,
        help="Paste your inspection notes. If translation is enabled, these will be translated to Arabic."
    )

    return client_name, translate_to_arabic, inspection_notes