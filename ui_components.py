"""
UI Components for FieldScribe
Handles all frontend interface elements and user input collection
"""

import streamlit as st
import logic
import streamlit.components.v1 as components
from datetime import date, datetime


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

    st.divider()

    # CRM Dashboard Button
    with st.container(border=True):
        st.subheader("📊 CRM Dashboard")
        st.write("View customer metrics, revenue, and manage calendar events.")
        st.write("")  # Spacer
        if st.button("Open CRM Dashboard →", type="primary", use_container_width=True):
            st.session_state.page = 'crm'
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


def render_crm_dashboard():
    """Renders the CRM dashboard with metrics, calendar, and event management."""
    
    # --- SIDEBAR: SAAS SECTIONS PANEL ---
    with st.sidebar:
        st.markdown("""
        <style>
        .saas-section {
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }
        .saas-section:hover {
            background-color: #f5f5f7;
            border-left-color: #EF4444;
        }
        .saas-section.active {
            background-color: #f5f5f7;
            border-left-color: #EF4444;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🏢 SAAS Sections")
        st.divider()
        
        saas_sections = [
            {"icon": "📊", "name": "Dashboard", "key": "dashboard"},
            {"icon": "👥", "name": "Users", "key": "users"},
            {"icon": "📁", "name": "Files", "key": "files"},
            {"icon": "📈", "name": "Analytics", "key": "analytics"},
            {"icon": "⚙️", "name": "Settings", "key": "settings"},
            {"icon": "💳", "name": "Billing", "key": "billing"},
            {"icon": "🔔", "name": "Notifications", "key": "notifications"},
            {"icon": "🛡️", "name": "Security", "key": "security"},
        ]
        
        if 'active_saas_section' not in st.session_state:
            st.session_state.active_saas_section = 'dashboard'
        
        for section in saas_sections:
            is_active = st.session_state.active_saas_section == section['key']
            button_label = f"{section['icon']} {section['name']}"
            if st.button(button_label, key=f"saas_{section['key']}", use_container_width=True, 
                        type="primary" if is_active else "secondary"):
                st.session_state.active_saas_section = section['key']
                st.rerun()
        
        st.divider()
        st.markdown("### 📋 Quick Actions")
        if st.button("➕ New User", use_container_width=True):
            st.info("New user creation feature coming soon!")
        if st.button("📤 Upload File", use_container_width=True):
            st.info("File upload feature coming soon!")
    
    # Apple-like custom CSS with mobile optimization
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .crm-header { font-size: 1.75rem !important; }
        .metric-value { 
            font-size: 1.5rem !important; 
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            max-width: 100% !important;
            line-height: 1.2 !important;
        }
        .metric-label {
            font-size: 0.75rem !important;
        }
        .metric-card { 
            padding: 1rem !important; 
            margin-bottom: 1rem !important;
            width: 100% !important;
            box-sizing: border-box !important;
            min-width: 0 !important;
            max-width: 100% !important;
            overflow: hidden !important;
        }
        /* Force columns to stack on mobile - more specific targeting */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            width: 100% !important;
            max-width: 100% !important;
            overflow: hidden !important;
        }
        div[data-testid="stHorizontalBlock"] > div {
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
            flex: 0 0 auto !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
        /* Ensure no horizontal overflow in main container */
        section[data-testid="stSidebar"] ~ div,
        .main .block-container,
        div[data-testid="stAppViewContainer"] {
            max-width: 100vw !important;
            overflow-x: hidden !important;
        }
        /* Prevent text overflow in metric cards */
        .metric-card * {
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
    }
    .crm-header {
        font-size: 2.5rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
        color: #1d1d1f;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f5f7 0%, #ffffff 100%);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.06);
        transition: transform 0.2s ease;
        width: 100%;
        box-sizing: border-box;
        overflow: hidden;
        word-wrap: break-word;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #86868b;
        font-weight: 500;
        letter-spacing: 0.01em;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #1d1d1f;
        letter-spacing: -0.02em;
        word-wrap: break-word;
        overflow-wrap: break-word;
        max-width: 100%;
    }
    .calendar-container {
        background: #ffffff;
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.08);
        width: 100%;
        max-width: 100%;
    }
    /* Desktop: keep calendar compact */
    @media (min-width: 1024px) {
        .calendar-container {
            max-width: 320px;
            margin-left: auto;
            margin-right: auto;
        }
    }
    @media (max-width: 768px) {
        .calendar-container { 
            padding: 0.75rem !important; 
            border-radius: 16px !important;
        }
    }
    /* Calendar Grid - 7 columns, all screen sizes */
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 0.5rem;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    @media (max-width: 768px) {
        .calendar-grid { 
            gap: 0.375rem !important; 
        }
    }
    .calendar-day-label {
        text-align: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: #86868b;
        padding: 0.5rem 0;
    }
    @media (max-width: 768px) {
        .calendar-day-label {
            font-size: 0.7rem !important;
            padding: 0.375rem 0 !important;
        }
    }
    /* Calendar day cell styling */
    .calendar-day-cell {
        display: flex;
        align-items: center;
        justify-content: center;
        aspect-ratio: 1;
        min-height: 2rem;
        font-weight: 700;
        font-size: 0.875rem;
        color: #1d1d1f;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    @media (max-width: 768px) {
        .calendar-day-cell {
            min-height: 2rem !important;
            font-size: 0.75rem !important;
        }
    }
    /* Weekend styling - gray text */
    .calendar-day-cell.weekend button {
        color: #86868b !important;
        font-weight: 500 !important;
    }
    /* Active/Selected date - circular red background */
    .calendar-day-cell.active button {
        background-color: #EF4444 !important;
        color: white !important;
        border-radius: 50% !important;
        width: 2rem !important;
        height: 2rem !important;
        min-width: 2rem !important;
        min-height: 2rem !important;
        max-width: 2rem !important;
        max-height: 2rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 700 !important;
        border: none !important;
    }
    @media (max-width: 768px) {
        .calendar-day-cell.active button {
            width: 1.75rem !important;
            height: 1.75rem !important;
            min-width: 1.75rem !important;
            min-height: 1.75rem !important;
            max-width: 1.75rem !important;
            max-height: 1.75rem !important;
        }
    }
    /* Weekday buttons - black/charcoal, bold */
    .calendar-day-cell:not(.weekend):not(.active) button {
        color: #1d1d1f !important;
        font-weight: 700 !important;
        background: transparent !important;
        border: none !important;
    }
    .calendar-day-cell button:hover:not(.active) {
        background-color: #f5f5f7 !important;
        border-radius: 50% !important;
    }
    .calendar-day-empty {
        aspect-ratio: 1;
    }

    .event-card {
        background: #f5f5f7;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(0,0,0,0.06);
        transition: all 0.2s ease;
    }
    .event-card:hover {
        background: #e8e8ed;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: #1d1d1f;
        margin-bottom: 1rem;
    }
    @media (max-width: 768px) {
        .section-title { font-size: 1.25rem !important; margin-bottom: 0.75rem !important; }
    }
    /* Calendar month header - reddish-coral, uppercase, bold */
    .calendar-month-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #EF4444;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
    @media (max-width: 768px) {
        .calendar-month-header {
            font-size: 1.25rem;
            margin-bottom: 0.75rem;
        }
    }
    /* Event info panel below calendar */
    .event-panel {
        background: #f5f5f7;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        border: 1px solid rgba(0,0,0,0.06);
        animation: slideDown 0.3s ease;
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @media (max-width: 768px) {
        .event-panel { padding: 1rem !important; margin-top: 1rem !important; }
    }
    /* Style form inputs */
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid rgba(0,0,0,0.1);
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #007aff;
        box-shadow: 0 0 0 3px rgba(0,122,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    def _get_query_param(name: str):
        # Use the experimental query param API consistently (do not mix with st.query_params)
        try:
            qp = st.experimental_get_query_params()
            values = qp.get(name)
            if not values:
                return None
            # values may be a list
            return values[0] if isinstance(values, list) else values
        except Exception:
            return None
    
    # Header with navigation
    col_header1, col_header2 = st.columns([1, 20])
    with col_header1:
        if st.button("←", help="Back to Home", use_container_width=True):
            st.session_state.page = 'home'
            st.session_state.selected_calendar_date = None
            st.rerun()
    
    st.markdown('<div class="crm-header">CRM Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
    
    # --- METRICS SECTION ---
    # Use responsive columns - stack on mobile
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Customers</div>
            <div class="metric-value">{:,}</div>
        </div>
        """.format(st.session_state.customer_count), unsafe_allow_html=True)
    
    with col2:
        revenue_formatted = f"${st.session_state.monthly_revenue:,.2f}"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Revenue This Month</div>
            <div class="metric-value">{revenue_formatted}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div style="height: 2.5rem;"></div>', unsafe_allow_html=True)
    
    # --- CALENDAR SECTION ---
    st.markdown('<div class="section-title">Calendar</div>', unsafe_allow_html=True)

    # Sync selection from query param (HTML calendar uses links)
    qp_cal = _get_query_param("cal")
    if qp_cal is not None:
        st.session_state.selected_calendar_date = qp_cal or None
    
    # Get current month calendar data
    today = date.today()
    calendar_data = logic.get_calendar_month_data(today.year, today.month)
    
    # Calendar container - compact design
    with st.container():
        # Build calendar HTML as a Streamlit component so clicks update selection
        # without opening a new tab (Streamlit markdown links are forced to _blank).
        first_date = date(calendar_data['year'], calendar_data['month'], 1)
        first_weekday = first_date.weekday()  # Monday=0, Sunday=6
        # Convert to Sunday=0 format
        first_weekday_sunday = (first_weekday + 1) % 7  # Sunday=0, Monday=1, ..., Saturday=6
        
        today_str = today.strftime('%Y-%m-%d')
        
        # Use a native Streamlit date picker to reliably update session state.
        selected_date = st.session_state.get('selected_calendar_date')
        try:
            picker_default = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else today
        except Exception:
            picker_default = today

        new_picker = st.date_input("", value=picker_default, key='crm_date_input')
        new_picker_str = new_picker.strftime('%Y-%m-%d') if new_picker else None
        if new_picker_str != selected_date:
            st.session_state.selected_calendar_date = new_picker_str
            try:
                st.experimental_set_query_params(cal=new_picker_str)
            except Exception:
                pass
            st.rerun()

        month_name_upper = calendar_data['month_name'].upper()
        day_headers = ['S', 'M', 'T', 'W', 'T', 'F', 'S']

        # Build a visual grid (non-interactive) that reflects the selected date from the picker.
        cells_html = []
        for _ in range(first_weekday_sunday):
            cells_html.append('<div class="cal-day"></div>')

        for day_info in calendar_data['days']:
            day_num = day_info['day']
            day_date = day_info['date']
            day_obj = datetime.strptime(day_date, '%Y-%m-%d').date()
            weekday = day_obj.weekday()  # Monday=0, Sunday=6
            is_weekend = weekday == 5 or weekday == 6
            is_today = day_date == today_str
            is_selected = selected_date == day_date
            is_active = is_today or is_selected

            btn_classes = ['cal-btn']
            if is_weekend and not is_active:
                btn_classes.append('weekend')
            if is_active:
                btn_classes.append('active')

            # Visual-only cell; use the native picker (above) to change selection.
            classes = " ".join(btn_classes)
            cells_html.append(f'<div class="cal-day"><div class="{classes}">{day_num}</div></div>')

        header_html = ''.join([f'<div class="calendar-day-label">{h}</div>' for h in day_headers])

        calendar_component_html = f"""
        <div class="calendar-container">
            <div class="calendar-month-header">{month_name_upper}</div>
            <div class="calendar-grid">{header_html}</div>
            <div class="cal-grid">{''.join(cells_html)}</div>
        </div>

        <style>
            .calendar-container {{
                background: #ffffff;
                border-radius: 20px;
                padding: 1rem;
                box-shadow: 0 4px 16px rgba(0,0,0,0.06);
                border: 1px solid rgba(0,0,0,0.08);
                width: 100%;
                max-width: 100%;
                box-sizing: border-box;
            }}
            @media (min-width: 1024px) {{
                .calendar-container {{
                    max-width: 320px;
                    margin-left: auto;
                    margin-right: auto;
                }}
            }}
            @media (max-width: 768px) {{
                .calendar-container {{
                    padding: 0.75rem;
                    border-radius: 16px;
                }}
            }}
            .calendar-month-header {{
                font-size: 1.5rem;
                font-weight: 700;
                color: #EF4444;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 1rem;
            }}
            @media (min-width: 1024px) {{
                .calendar-month-header {{
                    font-size: 1.15rem;
                    margin-bottom: 0.75rem;
                }}
            }}
            @media (max-width: 768px) {{
                .calendar-month-header {{
                    font-size: 1.25rem;
                    margin-bottom: 0.75rem;
                }}
            }}
            .calendar-grid {{
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 0.5rem;
                width: 100%;
                margin-bottom: 0.5rem;
            }}
            @media (min-width: 1024px) {{
                .calendar-grid {{ gap: 0.25rem; }}
            }}
            @media (max-width: 768px) {{
                .calendar-grid {{ gap: 0.375rem; }}
            }}
            .calendar-day-label {{
                text-align: center;
                font-size: 0.75rem;
                font-weight: 700;
                color: #86868b;
                padding: 0.5rem 0;
            }}
            @media (min-width: 1024px) {{
                .calendar-day-label {{
                    font-size: 0.65rem;
                    padding: 0.35rem 0;
                }}
            }}
            @media (max-width: 768px) {{
                .calendar-day-label {{
                    font-size: 0.7rem;
                    padding: 0.375rem 0;
                }}
            }}
            .cal-grid {{
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 0.5rem;
                width: 100%;
            }}
            @media (min-width: 1024px) {{
                .cal-grid {{ gap: 0.25rem; }}
            }}
            @media (max-width: 768px) {{
                .cal-grid {{ gap: 0.375rem; }}
            }}
            .cal-day {{
                display: flex;
                align-items: center;
                justify-content: center;
                aspect-ratio: 1;
                min-height: 2rem;
            }}
            @media (min-width: 1024px) {{
                .cal-day {{ min-height: 1.7rem; }}
            }}
            .cal-btn {{
                width: 2rem;
                height: 2rem;
                min-width: 2rem;
                min-height: 2rem;
                max-width: 2rem;
                max-height: 2rem;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                border: none;
                background: transparent;
                color: #1d1d1f;
                font-weight: 700;
                font-size: 0.875rem;
                cursor: pointer;
                -webkit-tap-highlight-color: transparent;
            }}
            @media (min-width: 1024px) {{
                .cal-btn {{
                    width: 1.6rem;
                    height: 1.6rem;
                    min-width: 1.6rem;
                    min-height: 1.6rem;
                    max-width: 1.6rem;
                    max-height: 1.6rem;
                    font-size: 0.75rem;
                }}
            }}
            @media (max-width: 768px) {{
                .cal-btn {{
                    width: 1.75rem;
                    height: 1.75rem;
                    min-width: 1.75rem;
                    min-height: 1.75rem;
                    max-width: 1.75rem;
                    max-height: 1.75rem;
                    font-size: 0.75rem;
                }}
            }}
            .cal-btn:hover {{
                background-color: #f5f5f7;
            }}
            .cal-btn.weekend {{
                color: #86868b;
                font-weight: 500;
            }}
            .cal-btn.active {{
                background-color: #EF4444;
                color: #ffffff;
            }}
        </style>

        <script>
            function selectDate(dateStr) {{
                try {{
                    const trySet = (win) => {{
                        try {{
                            const url = new URL(win.location.href);
                            if (!dateStr) {{
                                url.searchParams.delete('cal');
                            }} else {{
                                url.searchParams.set('cal', dateStr);
                            }}
                            // use replace first to avoid history spam
                            win.location.replace(url.toString());
                            return true;
                        }} catch (err) {{
                            return false;
                        }}
                    }};

                    // Try top then parent then self
                    if (window.top && trySet(window.top)) return;
                    if (window.parent && trySet(window.parent)) return;
                    if (trySet(window)) return;

                    // As a last resort, postMessage to parent with a clear shape;
                    // Streamlit may pick this up in some environments or future versions.
                    try {{
                        window.parent.postMessage({{streamlit_calendar: true, date: dateStr}}, '*');
                    }} catch (e) {{
                        // no-op
                    }}
                }} catch (e) {{
                    // final noop
                }}
            }}
        </script>
        """

        # Height is fixed to prevent scrollbars; adjust if you change sizes.
        components.html(calendar_component_html, height=360, scrolling=False)
    
    # Event info panel - appears directly below calendar when day is selected
    if st.session_state.selected_calendar_date:
        selected_date = st.session_state.selected_calendar_date
        date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%B %d, %Y')
        
        st.markdown(f"""
        <div class="event-panel">
            <div style="font-size: 1.125rem; font-weight: 600; color: #1d1d1f; margin-bottom: 1rem; letter-spacing: -0.01em;">
                {formatted_date}
            </div>
        """, unsafe_allow_html=True)
        
        # Display existing events
        if selected_date in st.session_state.crm_events and st.session_state.crm_events[selected_date]:
            for i, event in enumerate(st.session_state.crm_events[selected_date]):
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.markdown(f"""
                    <div class="event-card">
                        <div style="font-size: 1rem; font-weight: 600; color: #1d1d1f; margin-bottom: 0.5rem; letter-spacing: -0.01em;">
                            {event['title']}
                        </div>
                        <div style="font-size: 0.875rem; color: #86868b; margin-bottom: 0.5rem; font-weight: 500;">
                            {logic.format_event_time(event['time'])}
                        </div>
                        {f'<div style="font-size: 0.875rem; color: #515154; line-height: 1.5;">{event.get("description", "")}</div>' if event.get('description') else ''}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown('<div style="padding-top: 0.75rem;"></div>', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"delete_{selected_date}_{i}", help="Delete event"):
                        st.session_state.crm_events[selected_date].pop(i)
                        if not st.session_state.crm_events[selected_date]:
                            del st.session_state.crm_events[selected_date]
                        st.rerun()
        else:
            st.markdown("""
            <div style="text-align: center; color: #86868b; font-size: 0.875rem; padding: 1rem 0;">
                No events scheduled for this day.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
        
        # Add new event form - compact
        with st.expander("➕ Add New Event", expanded=False):
            with st.form(f"add_event_{selected_date}"):
                event_title = st.text_input("Event Title", placeholder="e.g., Client Meeting", key=f"title_{selected_date}")
                col_time1, col_time2 = st.columns([1, 1])
                with col_time1:
                    event_time = st.time_input("Time", key=f"time_{selected_date}")
                event_description = st.text_area("Description (optional)", height=80, placeholder="Add notes...", key=f"desc_{selected_date}")
                
                submitted = st.form_submit_button("Add Event", type="primary", use_container_width=True)
                
                if submitted and event_title:
                    if selected_date not in st.session_state.crm_events:
                        st.session_state.crm_events[selected_date] = []
                    
                    time_str = event_time.strftime('%H:%M')
                    new_event = {
                        'title': event_title,
                        'time': time_str,
                        'description': event_description
                    }
                    st.session_state.crm_events[selected_date].append(new_event)
                    st.success(f"✓ Event '{event_title}' added!")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; color: #86868b; font-size: 0.875rem; padding: 1rem 0; margin-top: 1rem;">
            👆 Tap a day to view or add events
        </div>
        """, unsafe_allow_html=True)
    
    # --- DEMO USERS SECTION ---
    st.markdown('<div style="height: 3rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👥 Demo Users</div>', unsafe_allow_html=True)
    
    # Add CSS for user cards
    st.markdown("""
    <style>
    .user-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.06);
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .user-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #EF4444;
    }
    .user-card.active {
        border-color: #EF4444;
        border-width: 2px;
        background: #fff5f5;
    }
    .user-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .user-info h3 {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1d1d1f;
        margin: 0 0 0.25rem 0;
    }
    .user-info p {
        font-size: 0.875rem;
        color: #86868b;
        margin: 0;
    }
    .user-role {
        background: #f5f5f7;
        padding: 0.375rem 0.75rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #515154;
    }
    .file-list {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(0,0,0,0.06);
    }
    .file-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        background: #f5f5f7;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    .file-item:hover {
        background: #e8e8ed;
    }
    .file-info {
        flex: 1;
    }
    .file-name {
        font-size: 0.875rem;
        font-weight: 600;
        color: #1d1d1f;
        margin-bottom: 0.25rem;
    }
    .file-meta {
        font-size: 0.75rem;
        color: #86868b;
    }
    .file-size {
        font-size: 0.75rem;
        color: #86868b;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display users
    demo_users = st.session_state.demo_users
    
    for user_id, user_data in demo_users.items():
        is_selected = st.session_state.selected_user == user_id
        
        with st.container():
            user_card_html = f"""
            <div class="user-card {'active' if is_selected else ''}" id="user_{user_id}">
                <div class="user-header">
                    <div class="user-info">
                        <h3>{user_data['name']}</h3>
                        <p>{user_data['email']}</p>
                    </div>
                    <div class="user-role">{user_data['role']}</div>
                </div>
            """
            st.markdown(user_card_html, unsafe_allow_html=True)
            
            # Show files if user is selected
            if is_selected:
                st.markdown('<div class="file-list">', unsafe_allow_html=True)
                st.markdown('<div style="font-size: 0.875rem; font-weight: 600; color: #1d1d1f; margin-bottom: 0.75rem;">📁 Files:</div>', unsafe_allow_html=True)
                
                for file in user_data['files']:
                    file_html = f"""
                    <div class="file-item">
                        <div class="file-info">
                            <div class="file-name">{file['name']}</div>
                            <div class="file-meta">📅 {file['date']}</div>
                        </div>
                        <div class="file-size">{file['size']}</div>
                    </div>
                    """
                    st.markdown(file_html, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Button to toggle user selection
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"{'👁️ Hide Files' if is_selected else '👁️ Show Files'}", 
                           key=f"toggle_{user_id}", use_container_width=True):
                    if st.session_state.selected_user == user_id:
                        st.session_state.selected_user = None
                    else:
                        st.session_state.selected_user = user_id
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)