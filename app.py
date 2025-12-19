import streamlit as st
from ui_components import draw_header, render_form
from logic import process_report

# Page Config (Make it look like a real app)
st.set_page_config(page_title="Sabaza Optimizer", page_icon="🚀", layout="centered")

def main():
    # Initialize session state (Memory)
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
        st.session_state.report_buffer = None
        st.session_state.client_name = ""

    # 1. Draw UI
    draw_header()
    client_name, translate_to_arabic, inspection_notes = render_form()

    # 2. Buttons Layout
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🚀 Generate Report", use_container_width=True, type="primary"):
            if not client_name.strip():
                st.error("❌ Please enter a Client Name")
            elif not inspection_notes.strip():
                st.error("❌ Please enter Inspection Notes")
            else:
                with st.spinner("⏳ Processing..."):
                    # Call the Logic File
                    report_buffer = process_report(
                        client_name=client_name,
                        notes=inspection_notes,
                        should_translate=translate_to_arabic
                    )
                    
                    # Save to Memory
                    st.session_state.report_generated = True
                    st.session_state.report_buffer = report_buffer
                    st.session_state.client_name = client_name
                    st.success("✅ Report Ready!")

    # 3. The Download Button (Only shows after generation)
    with col2:
        if st.session_state.report_generated:
            st.download_button(
                label="📥 Download Word Doc",
                data=st.session_state.report_buffer,
                file_name=f"Report_{st.session_state.client_name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

if __name__ == "__main__":
    main()