"""
UI Components for FieldScribe
Handles all frontend interface elements and user input collection
"""

import streamlit as st


def render_home_screen():
    """Renders the landing page with the two big options."""
    st.title("FieldScribe")
    st.write("Select your report type:")
    st.divider()

    col1, col2 = st.columns(2)

    # Card 1: Standard Inspection
    with col1:
        with st.container(border=True):
            st.subheader("📄 New Inspection")
            st.write("Start from scratch. Inspect a property and list defects.")
            st.write("")  # Spacer
            if st.button("Start Inspection →", type="primary"):
                st.session_state.page = 'deck'
                st.session_state.report_mode = 'standard'
                st.rerun()

    # Card 2: Defensive Report
    with col2:
        with st.container(border=True):
            st.subheader("🛡️ Defensive Opinion")
            st.write("Review an existing report (Claim vs. Finding).")
            st.write("")  # Spacer
            if st.button("Start Defensive Report →"):
                st.session_state.page = 'deck'
                st.session_state.report_mode = 'defensive'
                st.rerun()


def render_inspection_deck():
    # Detect Mode
    mode = st.session_state.report_mode
    is_defensive = (mode == 'defensive')

    # Set Titles dynamically
    page_title = "Defensive Rebuttal Deck" if is_defensive else "The Inspection Deck"
    st.title(page_title)

    # Navigation Buttons
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("← Home"):
            st.session_state.page = 'home'
            st.rerun()
    with col_nav2:
        count = len(st.session_state.selected_defects)
        if st.button(f"Review Checklist ({count} items) →", type="primary"):
            st.session_state.page = 'review'
            st.rerun()

    st.divider()

    # --- DYNAMIC FORM LABELS ---
    lbl_title = "Opposing Party's Claim" if is_defensive else "Defect Title"
    lbl_desc = "Engineer's Rebuttal / Finding" if is_defensive else "Description"
    lbl_ph_title = "e.g. 'Contractor claims wall is straight'" if is_defensive else "e.g. Balcony Rail Height"

    if is_defensive:
        st.info("🛡️ **Defensive Mode:** Enter the claim you are rebutting, then your actual finding.")

    # --- CUSTOM DEFECT CREATOR ---
    with st.expander("➕ Add Item", expanded=True):
        with st.form("custom_defect_form"):
            # 1. Text Inputs
            c_title = st.text_input(lbl_title, placeholder=lbl_ph_title)
            c_desc = st.text_area(lbl_desc)

            # 2. Category & Photo
            c_cat = st.selectbox("Category", ["Structural", "Electrical", "Plumbing", "Finishing", "Safety", "General"])
            c_photo = st.file_uploader("Attach Photo (Proof)", type=['png', 'jpg', 'jpeg'])

            # 3. Standard Code (Tekken) Dropdown
            common_codes = [
                "Other (Manual Input)",
                "SI-1142 (Guardrails)",
                "SI-1205 (Plumbing)",
                "SI-1555 (Tiling)",
                "SI-1752 (Partition Walls)",
                "SI-1928 (Painting)",
                "SI-900 (Electrical)"
            ]
            c_code_selection = st.selectbox("Standard (Tekken)", common_codes)

            # Logic for 'Other' code
            if "Other" in c_code_selection:
                c_code_input = st.text_input("Enter Manual Code")
                c_code = c_code_input if c_code_input else "-"
            else:
                c_code = c_code_selection.split(" ")[0]

            # 4. Submit Button
            btn_text = "Add Rebuttal" if is_defensive else "Add Defect"
            submitted = st.form_submit_button(btn_text)

            if submitted and c_title:
                st.session_state.selected_defects.append({
                    "title": c_title,
                    "desc": c_desc,
                    "code": c_code,
                    "category": c_cat,
                    "photo": c_photo,
                    "mode": mode
                })
                st.success(f"Added: {c_title}")

    # --- STANDARD DEFECT CARDS (Only show in Standard Mode usually, but keeping for demo) ---
    if not is_defensive:
        st.subheader("Common Defects")
        standard_defects = [
            {"title": "Dampness", "cat": "Structural", "icon": "💧", "code": "SI-1752",
             "desc": "Moisture detected above permitted levels (>13%)."},
            {"title": "Cracked Tiles", "cat": "Finishing", "icon": "🧱", "code": "SI-1555",
             "desc": "Cracked or hollow sounding floor tiles."},
            {"title": "Exposed Wiring", "cat": "Electrical", "icon": "⚡", "code": "SI-900",
             "desc": "Cables not enclosed in conduit."},
            {"title": "Low Railing", "cat": "Safety", "icon": "🚧", "code": "SI-1142",
             "desc": "Guardrail height is below 105cm."},
            {"title": "Water Leak", "cat": "Plumbing", "icon": "🚿", "code": "SI-1205",
             "desc": "Active leakage in pipe fittings."},
            {"title": "Peeling Paint", "cat": "Finishing", "icon": "🎨", "code": "SI-1928",
             "desc": "Paint adhesion failure."}
        ]

        cols = st.columns(3)
        for i, defect in enumerate(standard_defects):
            col = cols[i % 3]
            with col:
                with st.container(border=True):
                    st.caption(f"{defect['cat']} | {defect['code']}")
                    st.subheader(f"{defect['icon']} {defect['title']}")
                    st.write(defect["desc"])
                    if st.button("Add", key=f"btn_{i}"):
                        st.session_state.selected_defects.append(defect)
                        st.rerun()


def render_review_screen():
    """Renders the final list for review."""
    st.title("Review Checklist")

    # Client Details Form
    with st.container(border=True):
        st.subheader("Project Details")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.client_name = st.text_input("Client / Property Name", value=st.session_state.client_name)
        with col2:
            translate = st.checkbox("Translate Report to Arabic?", value=False)
        notes = st.text_area("Additional General Notes", height=100)

    st.subheader("Items to Report")

    if not st.session_state.selected_defects:
        st.info("No items selected. Go back to add some!")
    else:
        for i, item in enumerate(st.session_state.selected_defects):
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 4, 1])
                with c1:
                    st.write(f"**#{i + 1}**")
                    if 'photo' in item and item['photo']:
                        st.caption("📸 Photo")
                with c2:
                    # Dynamic Label based on mode
                    lbl = "Claim:" if st.session_state.report_mode == 'defensive' else "Defect:"
                    st.write(f"**{lbl} {item['title']}** ({item['category']})")
                    st.caption(item['desc'])
                    st.caption(f"Code: {item.get('code', '-')}")
                with c3:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.selected_defects.pop(i)
                        st.rerun()

    return st.session_state.client_name, notes, translate