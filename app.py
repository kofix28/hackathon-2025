import streamlit as st
import ui_components
import logic

# Page Config (Must be the first command)
st.set_page_config(page_title="FieldScribe", page_icon="🏗️", layout="wide")


def main():
    # --- SESSION STATE SETUP ---
    # We use this to remember data between pages
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'report_mode' not in st.session_state:
        st.session_state.report_mode = 'standard'  # Options: 'standard', 'defensive'
    if 'selected_defects' not in st.session_state:
        st.session_state.selected_defects = []
    if 'client_name' not in st.session_state:
        st.session_state.client_name = ""
    # CRM Dashboard state
    if 'crm_events' not in st.session_state:
        st.session_state.crm_events = {}
    if 'selected_calendar_date' not in st.session_state:
        st.session_state.selected_calendar_date = None
    if 'customer_count' not in st.session_state:
        st.session_state.customer_count = 150
    if 'monthly_revenue' not in st.session_state:
        st.session_state.monthly_revenue = 45000
    # Demo users and files state
    if 'demo_users' not in st.session_state:
        st.session_state.demo_users = {
            'user1': {
                'name': 'John Smith',
                'email': 'john.smith@example.com',
                'role': 'Engineer',
                'files': [
                    {'name': 'Inspection_Report_2024_01.docx', 'date': '2024-01-15', 'size': '2.3 MB'},
                    {'name': 'Site_Photos_Project_A.zip', 'date': '2024-01-10', 'size': '15.7 MB'},
                    {'name': 'Defensive_Opinion_Client_B.docx', 'date': '2024-01-05', 'size': '1.8 MB'},
                ]
            },
            'user2': {
                'name': 'Sarah Johnson',
                'email': 'sarah.j@example.com',
                'role': 'Senior Inspector',
                'files': [
                    {'name': 'Building_Inspection_2024_02.docx', 'date': '2024-02-20', 'size': '3.1 MB'},
                    {'name': 'Safety_Audit_Report.pdf', 'date': '2024-02-18', 'size': '4.5 MB'},
                    {'name': 'Structural_Analysis.xlsx', 'date': '2024-02-15', 'size': '892 KB'},
                    {'name': 'Photo_Documentation.zip', 'date': '2024-02-12', 'size': '22.3 MB'},
                ]
            },
            'user3': {
                'name': 'Michael Chen',
                'email': 'm.chen@example.com',
                'role': 'Field Engineer',
                'files': [
                    {'name': 'Property_Inspection_2024_03.docx', 'date': '2024-03-10', 'size': '2.9 MB'},
                    {'name': 'Defect_List_March.xlsx', 'date': '2024-03-08', 'size': '456 KB'},
                ]
            }
        }
    if 'selected_user' not in st.session_state:
        st.session_state.selected_user = None

    # --- NAVIGATION ---

    # PAGE 1: HOME SCREEN
    if st.session_state.page == 'home':
        ui_components.render_home_screen()

    # PAGE 2: INSPECTION DECK (Adapts to Mode)
    elif st.session_state.page == 'deck':
        ui_components.render_inspection_deck()

    # PAGE 3: REVIEW & GENERATE
    elif st.session_state.page == 'review':
        client_name, notes, translate = ui_components.render_review_screen()

        # The Generate Button
        if st.button("🚀 Generate Final Report", type="primary", use_container_width=True):
            if not client_name:
                st.error("Please enter a Client Name first.")
            else:
                with st.spinner("Generating Word Document..."):
                    try:
                        # Call Backend with all data including report_mode
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

        # Back Button
        if st.button("← Back to Deck"):
            st.session_state.page = 'deck'
            st.rerun()

    # PAGE 4: CRM DASHBOARD
    elif st.session_state.page == 'crm':
        ui_components.render_crm_dashboard()


if __name__ == "__main__":
    main()