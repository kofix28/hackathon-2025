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


if __name__ == "__main__":
    main()