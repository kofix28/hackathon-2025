import streamlit as st
import ui_components
import logic

# Page Config (Must be the first command)
st.set_page_config(page_title="FieldScribe", page_icon="🏗️", layout="wide")


def main():
    # --- SESSION STATE SETUP ---
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'report_mode' not in st.session_state:
        st.session_state.report_mode = 'standard'
    if 'selected_defects' not in st.session_state:
        st.session_state.selected_defects = []
    if 'client_name' not in st.session_state:
        st.session_state.client_name = ""
    # CRM State
    if 'crm_events' not in st.session_state:
        st.session_state.crm_events = {}
    if 'customer_count' not in st.session_state:
        st.session_state.customer_count = 150
    if 'monthly_revenue' not in st.session_state:
        st.session_state.monthly_revenue = 45000
    if 'demo_users' not in st.session_state:
        # Pre-fill some demo users for the UI
        st.session_state.demo_users = {
            'user1': {'name': 'John Smith', 'email': 'john@example.com', 'role': 'Engineer',
                      'files': [{'name': 'Report1.docx', 'date': '2024-01-01', 'size': '2MB'}]},
            'user2': {'name': 'Sarah Johnson', 'email': 'sarah@example.com', 'role': 'Inspector', 'files': []}
        }
    if 'selected_user' not in st.session_state:
        st.session_state.selected_user = None

    # --- NAVIGATION ---

    # PAGE 1: HOME
    if st.session_state.page == 'home':
        ui_components.render_home_screen()

    # PAGE 2: DECK
    elif st.session_state.page == 'deck':
        ui_components.render_inspection_deck()

    # PAGE 3: REVIEW
    elif st.session_state.page == 'review':
        client_name, notes, translate = ui_components.render_review_screen()

        if st.button("🚀 Generate Final Report", type="primary", use_container_width=True):
            if not client_name:
                st.error("Please enter a Client Name first.")
            else:
                with st.spinner("Generating Word Document..."):
                    try:
                        buffer = logic.process_report(
                            client_name,
                            notes,
                            st.session_state.selected_defects,
                            translate,
                            st.session_state.report_mode
                        )
                        st.success("Report Ready!")
                        st.download_button(
                            label="📥 Download .docx",
                            data=buffer,
                            file_name=f"FieldScribe_{client_name}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    except Exception as e:
                        st.error(f"Error generating report: {e}")

        if st.button("← Back to Deck"):
            st.session_state.page = 'deck'
            st.rerun()

    # PAGE 4: CRM DASHBOARD
    elif st.session_state.page == 'crm':
        ui_components.render_crm_dashboard()


if __name__ == "__main__":
    main()