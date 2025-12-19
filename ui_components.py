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
    # --- SETUP SESSION STATE FOR THE FORM ---
    # We need persistent memory for the inputs so they don't vanish when you take a photo
    if 'temp_title' not in st.session_state: st.session_state.temp_title = ""
    if 'temp_desc' not in st.session_state: st.session_state.temp_desc = ""
    if 'temp_photos' not in st.session_state: st.session_state.temp_photos = []
    if 'cam_id' not in st.session_state: st.session_state.cam_id = 0

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

    # --- CUSTOM DEFECT CREATOR (No 'st.form' to allow camera interactions) ---
    with st.expander("➕ Add Item", expanded=True):
        st.write("#### New Entry")

        # 1. Inputs (Linked to Session State)
        st.session_state.temp_title = st.text_input(lbl_title, value=st.session_state.temp_title,
                                                    placeholder=lbl_ph_title)
        st.session_state.temp_desc = st.text_area(lbl_desc, value=st.session_state.temp_desc)

        # 2. Category
        c_cat = st.selectbox("Category", ["Structural", "Electrical", "Plumbing", "Finishing", "Safety", "General"])

        # 3. MULTI-PHOTO SYSTEM
        st.write("Attach Evidence")
        tab_upload, tab_cam = st.tabs(["📂 Gallery Upload", "📸 Multi-Shot Camera"])

        # TAB A: Gallery
        with tab_upload:
            uploaded_photos = st.file_uploader("Select files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

        # TAB B: Camera (The "Burst Mode" Logic)
        with tab_cam:
            st.caption("Taking a photo auto-saves it to the list below.")

            # We change the key every time a photo is taken to reset the camera
            cam_key = f"camera_{st.session_state.cam_id}"
            camera_photo = st.camera_input("Take Photo", key=cam_key)

            if camera_photo:
                # Save to our temp list
                st.session_state.temp_photos.append(camera_photo)
                # Increment ID to force a fresh camera input next time
                st.session_state.cam_id += 1
                st.rerun()

        # Display Collected Photos (Thumbnails)
        if st.session_state.temp_photos or uploaded_photos:
            st.write("---")
            st.write("**Attached Photos:**")

            # Show Camera Shots
            if st.session_state.temp_photos:
                cols = st.columns(4)
                for i, pic in enumerate(st.session_state.temp_photos):
                    with cols[i % 4]:
                        st.image(pic, width=100)
                        # Optional: Button to delete specific photo could go here

                if st.button("🗑️ Clear Camera Photos"):
                    st.session_state.temp_photos = []
                    st.rerun()

        # 4. Standard Code (Tekken)
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

        if "Other" in c_code_selection:
            c_code = st.text_input("Enter Manual Code", value="-")
        else:
            c_code = c_code_selection.split(" ")[0]

        st.write("")  # Spacer

        # 5. FINAL ADD BUTTON
        btn_text = "Add Rebuttal to Report" if is_defensive else "Add Defect to Report"

        if st.button(btn_text, type="primary"):
            if st.session_state.temp_title:
                # Combine Gallery + Camera photos
                final_photos = []
                if uploaded_photos:
                    final_photos.extend(uploaded_photos)
                if st.session_state.temp_photos:
                    final_photos.extend(st.session_state.temp_photos)

                # Save
                st.session_state.selected_defects.append({
                    "title": st.session_state.temp_title,
                    "desc": st.session_state.temp_desc,
                    "code": c_code,
                    "category": c_cat,
                    "photos": final_photos,
                    "mode": mode
                })

                # RESET FORM
                st.session_state.temp_title = ""
                st.session_state.temp_desc = ""
                st.session_state.temp_photos = []
                st.success("Item Added!")
                st.rerun()
            else:
                st.error("Please provide a Title.")

    # --- STANDARD DEFECT CARDS ---
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
                    # Check for photos
                    has_photos = ('photos' in item and item['photos']) or ('photo' in item and item['photo'])
                    if has_photos:
                        st.caption("📸 Evidence Attached")
                with c2:
                    lbl = "Claim:" if st.session_state.report_mode == 'defensive' else "Defect:"
                    st.write(f"**{lbl} {item['title']}** ({item['category']})")
                    st.caption(item['desc'])
                    st.caption(f"Code: {item.get('code', '-')}")
                with c3:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.selected_defects.pop(i)
                        st.rerun()

    return st.session_state.client_name, notes, translate