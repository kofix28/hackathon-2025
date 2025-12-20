"""
UI Components for FieldScribe
Handles all frontend interface elements and user input collection
"""

import streamlit as st
import logic
import streamlit.components.v1 as components
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont
import io
import requests
try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False

def edit_image(image_file, canvas_data=None):
    """
    Edit image with canvas drawings.
    """
    try:
        image = Image.open(image_file)

        if canvas_data is not None and canvas_data.image_data is not None:
            # Get the drawing as PIL image
            drawing = Image.fromarray(canvas_data.image_data.astype('uint8'), 'RGBA')

            # Composite the drawing onto the original image
            if drawing.size != image.size:
                drawing = drawing.resize(image.size, Image.Resampling.LANCZOS)

            # Create a mask from the alpha channel
            mask = drawing.split()[-1]  # Alpha channel

            # Composite
            image = Image.composite(drawing, image, mask)

        # Save to bytes
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)
        return buf
    except Exception as e:
        st.error(f"Error editing image: {e}")
        return image_file

# Sample Tekun standards (placeholder - replace with actual PDF extraction)
TEKUN_STANDARDS = [
    "SI-1142 (Guardrails) - Height requirements for guardrails",
    "SI-1205 (Plumbing) - Pipe fitting leakage standards",
    "SI-1555 (Tiling) - Cracked tile detection",
    "SI-1752 (Partition Walls) - Moisture levels",
    "SI-1928 (Painting) - Paint adhesion standards",
    "SI-900 (Electrical) - Exposed wiring regulations",
    "SI-2100 (Structural) - Load bearing requirements",
    "SI-3050 (Safety) - Emergency exit standards",
    "SI-4100 (Finishing) - Surface finish quality",
    "SI-5200 (HVAC) - Ventilation requirements"
]


def render_home_screen():
    """Renders the landing page with the two big options."""
    st.title("Civil+")
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
    # --- INTERNAL HELPER: Wikimedia image search ---
    # (Integrated from teammate's update)
    import requests
    def search_wikimedia_images(query: str, limit: int = 8):
        if not query or not query.strip():
            return []
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": query, "gsrlimit": str(limit), "gsrnamespace": "6",
            "prop": "imageinfo", "iiprop": "url", "iiurlwidth": "400"
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
        except Exception:
            return []
        pages = data.get("query", {}).get("pages", {})
        results = []
        for _, p in pages.items():
            infos = p.get("imageinfo", [])
            if not infos: continue
            info = infos[0]
            thumb = info.get("thumburl")
            full = info.get("url")
            if thumb and full: results.append({"thumb": thumb, "full": full})
        return results

    # --- SETUP SESSION STATE ---
    # Standard Fields
    if 'temp_title' not in st.session_state: st.session_state.temp_title = ""
    if 'temp_desc' not in st.session_state: st.session_state.temp_desc = ""
    if 'temp_photos' not in st.session_state: st.session_state.temp_photos = []
    if 'cam_id' not in st.session_state: st.session_state.cam_id = 0

    # NEW: Map (House Plan) State
    if 'temp_map_photos' not in st.session_state: st.session_state.temp_map_photos = []
    if 'map_cam_id' not in st.session_state: st.session_state.map_cam_id = 0

    # NEW: Tool (Repair Tool) State
    if 'tool_results' not in st.session_state: st.session_state.tool_results = []
    if 'selected_tool_url' not in st.session_state: st.session_state.selected_tool_url = ""
    if 'temp_tool_photos' not in st.session_state: st.session_state.temp_tool_photos = []
    if 'tool_cam_id' not in st.session_state: st.session_state.tool_cam_id = 0
    if 'tool_name' not in st.session_state: st.session_state.tool_name = ""
    if 'tool_desc' not in st.session_state: st.session_state.tool_desc = ""

    # Detect Mode
    mode = st.session_state.report_mode
    is_defensive = (mode == 'defensive')

    # Titles & Navigation
    page_title = "Defensive Rebuttal Deck" if is_defensive else "The Inspection Deck"
    st.title(page_title)

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

    # Dynamic Labels
    lbl_title = "Opposing Party's Claim" if is_defensive else "Defect Title"
    lbl_desc = "Engineer's Rebuttal / Finding" if is_defensive else "Description"
    lbl_ph_title = "e.g. 'Contractor claims wall is straight'" if is_defensive else "e.g. Balcony Rail Height"

    if is_defensive:
        st.info("🛡️ **Defensive Mode:** Enter the claim you are rebutting, then your actual finding.")

    # --- INPUT FORM ---
    with st.expander("➕ Add Item", expanded=True):
        st.write("#### New Entry")

        # 1. Basic Inputs
        st.session_state.temp_title = st.text_input(lbl_title, value=st.session_state.temp_title,
                                                    placeholder=lbl_ph_title)
        st.session_state.temp_desc = st.text_area(lbl_desc, value=st.session_state.temp_desc)

        c_cat = st.selectbox("Category", ["Structural", "Electrical", "Plumbing", "Finishing", "Safety", "General"],
                             key="category_select")

        # 2. EVIDENCE PHOTOS (Your Drawing Feature Preserved)
        st.write("Attach Evidence ")
        tab_upload, tab_cam = st.tabs(["📂 Gallery Upload", "📸 Multi-Shot Camera"])

        with tab_upload:
            uploaded_photos = st.file_uploader("Select files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True,
                                               key="evidence_gallery")

        with tab_cam:
            st.caption("Taking a photo auto-saves it to the list below.")
            cam_key = f"camera_{st.session_state.cam_id}"
            camera_photo = st.camera_input("Take Photo", key=cam_key)
            if camera_photo:
                st.session_state.temp_photos.append(camera_photo)
                st.session_state.cam_id += 1
                st.rerun()

        # Display Evidence & Drawing Canvas
        if st.session_state.temp_photos or uploaded_photos:
            st.write("---")
            st.write("**Attached Photos:**")
            if st.session_state.temp_photos:
                cols = st.columns(4)
                for i, pic in enumerate(st.session_state.temp_photos):
                    with cols[i % 4]:
                        st.image(pic, width=100)
                        # YOUR DRAWING FEATURE
                        with st.expander(f"Edit Photo {i + 1}"):
                            try:
                                if CANVAS_AVAILABLE:
                                    st.write("Draw on image:")
                                    img = Image.open(pic)
                                    canvas_result = st_canvas(
                                        fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color="red",
                                        background_image=img, update_streamlit=True, height=300, width=300,
                                        drawing_mode="freedraw", key=f"canvas_{i}"
                                    )
                                    if canvas_result.image_data is not None:
                                        if st.button(f"Save Edit {i + 1}", key=f"edit_{i}"):
                                            edited = edit_image(pic, canvas_result)
                                            st.session_state.temp_photos[i] = edited
                                            st.success("Saved!")
                                            st.rerun()
                                else:
                                    st.warning("Canvas not installed.")
                            except Exception as e:
                                st.error(f"Error: {e}")

                if st.button("🗑️ Clear Camera Photos", key="clear_evidence_cam"):
                    st.session_state.temp_photos = []
                    st.rerun()

            # (Optional: Add editing for uploaded photos here if desired, kept simple for now)

        # 3. Standard Code (Your Search Feature Preserved)
        st.write("**Standard (Tekken) Selection**")
        search_term = st.text_input("Search Tekun Standards", placeholder="Type keyword to search...",
                                    key="tekken_search")
        if st.button("🔍 Search Standards", key="tekken_search_btn"):
            if search_term:
                matching_standards = [std for std in TEKUN_STANDARDS if search_term.lower() in std.lower()]
                if matching_standards:
                    st.success(f"Found {len(matching_standards)} matching standards:")
                    selected_from_search = st.selectbox("Select from search results:", matching_standards,
                                                        key="search_select")
                    c_code = selected_from_search.split(" ")[0]
                else:
                    st.warning("No standards found.")
                    c_code = st.text_input("Enter Manual Code", value="-", key="manual_code_search")
            else:
                st.warning("Enter a search term.")
                c_code = st.text_input("Enter Manual Code", value="-", key="manual_code_empty")
        else:
            common_codes = ["Other (Manual Input)", "SI-1142 (Guardrails)", "SI-1205 (Plumbing)", "SI-1555 (Tiling)",
                            "SI-1752 (Partition Walls)", "SI-1928 (Painting)", "SI-900 (Electrical)"]
            c_code_selection = st.selectbox("Quick Select Standard", common_codes, key="tekken_select")
            if "Other" in c_code_selection:
                c_code = st.text_input("Enter Manual Code", value="-", key="manual_code")
            else:
                c_code = c_code_selection.split(" ")[0]

        # 4. REPAIR TOOL (Teammate's New Feature)
        st.write("Attach Repair Tool (optional)")
        tab_tool_search, tab_tool_cam = st.tabs(["🔎 Web Search", "📸 Camera"])

        with tab_tool_search:
            tool_query = st.text_input("Search tool name (e.g., saw, drill)", key="tool_query")
            if st.button("Search Tool", key="tool_search_btn"):
                st.session_state.selected_tool_url = ""
                st.session_state.tool_results = search_wikimedia_images(tool_query, limit=8)
                if not st.session_state.tool_results: st.warning("No images found.")

            if st.session_state.tool_results:
                st.write("**Choose an image:**")
                cols = st.columns(4)
                for idx, item in enumerate(st.session_state.tool_results):
                    with cols[idx % 4]:
                        st.image(item["thumb"], use_container_width=True)
                        if st.button("Select", key=f"select_tool_{idx}"):
                            st.session_state.selected_tool_url = item["full"]
                            st.rerun()

            if st.session_state.selected_tool_url:
                st.write("---")
                st.image(st.session_state.selected_tool_url, caption="Selected Tool", width=200)

            st.text_input("Tool name", key="tool_name")
            st.text_area("What does it do?", key="tool_desc", height=80)

        with tab_tool_cam:
            st.caption("Taking a photo auto-saves it to the list below.")
            tool_cam_key = f"tool_camera_{st.session_state.tool_cam_id}"
            tool_camera_photo = st.camera_input("Take Tool Photo", key=tool_cam_key)
            if tool_camera_photo:
                st.session_state.temp_tool_photos.append(tool_camera_photo)
                st.session_state.tool_cam_id += 1
                st.rerun()

        if st.session_state.temp_tool_photos:
            st.write("---")
            st.write("**Attached Tool Photos:**")
            cols = st.columns(4)
            for i, pic in enumerate(st.session_state.temp_tool_photos):
                with cols[i % 4]: st.image(pic, width=100)
            if st.button("🗑️ Clear Tool Photos", key="clear_tool_photos"):
                st.session_state.temp_tool_photos = []
                st.rerun()

        # 5. FLOOR PLAN (Teammate's New Feature)
        st.write("Attach Floor Plan / House Map")
        tab_map_upload, tab_map_cam = st.tabs(["📂 Gallery Upload", "📸 Multi-Shot Camera"])

        with tab_map_upload:
            uploaded_map_photos = st.file_uploader("Select map files", type=['png', 'jpg', 'jpeg'],
                                                   accept_multiple_files=True, key="map_gallery_uploader")

        with tab_map_cam:
            st.caption("Taking a photo auto-saves it to the list below.")
            map_cam_key = f"map_camera_{st.session_state.map_cam_id}"
            map_camera_photo = st.camera_input("Take Map Photo", key=map_cam_key)
            if map_camera_photo:
                st.session_state.temp_map_photos.append(map_camera_photo)
                st.session_state.map_cam_id += 1
                st.rerun()

        if st.session_state.temp_map_photos or uploaded_map_photos:
            st.write("---")
            st.write("**Attached Map Photos:**")
            if st.session_state.temp_map_photos:
                cols = st.columns(4)
                for i, pic in enumerate(st.session_state.temp_map_photos):
                    with cols[i % 4]: st.image(pic, width=100)
                if st.button("🗑️ Clear Map Photos", key="clear_map_photos"):
                    st.session_state.temp_map_photos = []
                    st.rerun()

        st.write("")  # Spacer

        # 6. SUBMIT BUTTON (Merged Logic)
        btn_text = "Add Rebuttal to Report" if is_defensive else "Add Defect to Report"
        if st.button(btn_text, type="primary"):
            if st.session_state.temp_title:
                # Aggregate Photos
                final_photos = []
                if uploaded_photos: final_photos.extend(uploaded_photos)
                if st.session_state.temp_photos: final_photos.extend(st.session_state.temp_photos)

                final_map_photos = []
                if uploaded_map_photos: final_map_photos.extend(uploaded_map_photos)
                if st.session_state.temp_map_photos: final_map_photos.extend(st.session_state.temp_map_photos)

                final_tool_photos = []
                if st.session_state.temp_tool_photos: final_tool_photos.extend(st.session_state.temp_tool_photos)

                # CRITICAL: Handle Web Tool URL -> Bytes conversion to prevent crash
                if st.session_state.selected_tool_url:
                    try:
                        response = requests.get(st.session_state.selected_tool_url, timeout=5)
                        if response.status_code == 200:
                            url_image = io.BytesIO(response.content)
                            final_tool_photos.append(url_image)
                    except Exception as e:
                        st.error(f"Failed to download tool image: {e}")

                # Save Data
                st.session_state.selected_defects.append({
                    "title": st.session_state.temp_title,
                    "desc": st.session_state.temp_desc,
                    "code": c_code,
                    "category": c_cat,
                    "photos": final_photos,
                    "map_photos": final_map_photos,
                    "tool_photos": final_tool_photos,
                    "tool_name": st.session_state.tool_name,
                    "tool_desc": st.session_state.tool_desc,
                    "mode": mode
                })

                # Reset
                st.session_state.temp_title = ""
                st.session_state.temp_desc = ""
                st.session_state.temp_photos = []
                st.session_state.temp_map_photos = []
                st.session_state.temp_tool_photos = []
                st.session_state.selected_tool_url = ""
                st.session_state.tool_results = []
                #st.session_state.tool_name = ""
                #st.session_state.tool_desc = ""

                st.success("Item Added!")
                st.rerun()
            else:
                st.error("Please provide a Title.")

    # --- STANDARD DEFECT CARDS (Kept from your version) ---
    if not is_defensive:
        st.subheader("Common Defects")
        standard_defects = [
            {"title": "Dampness", "cat": "Structural", "icon": "💧", "code": "SI-1752", "desc": "Moisture >13%."},
            {"title": "Cracked Tiles", "cat": "Finishing", "icon": "🧱", "code": "SI-1555", "desc": "Hollow tiles."},
            {"title": "Exposed Wiring", "cat": "Electrical", "icon": "⚡", "code": "SI-900", "desc": "No conduit."},
            {"title": "Low Railing", "cat": "Safety", "icon": "🚧", "code": "SI-1142", "desc": "Height <105cm."},
            {"title": "Water Leak", "cat": "Plumbing", "icon": "🚿", "code": "SI-1205", "desc": "Active leak."},
            {"title": "Peeling Paint", "cat": "Finishing", "icon": "🎨", "code": "SI-1928", "desc": "Adhesion failure."}
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
            translate = st.checkbox("Translate Report to Arabic? ", value=False)
        notes = st.text_area("Additional General Notes", height=100)

    # Company Logo Section
    with st.container(border=True):
        st.subheader("Company Logo")
        st.write("Upload your company logo to include it in the report header.")
        logo_file = st.file_uploader("Select Logo Image", type=['png', 'jpg', 'jpeg'], help="Recommended: PNG or JPG format, will be compressed automatically")
        if logo_file:
            st.image(logo_file, width=200, caption="Logo Preview")

    st.subheader("Items to Report")

    if not st.session_state.selected_defects:
        st.info("No items selected. Go back to add some!")
    else:
        for i, item in enumerate(st.session_state.selected_defects):
            with st.container(border=True):
                c_img, c_txt, c_del = st.columns([2, 6, 1])

                with c_img:
                    st.write(f"**#{i + 1}**")

                    photos = []
                    if 'photos' in item and item['photos']:
                        photos = item['photos']
                    elif 'photo' in item and item['photo']:
                        photos = [item['photo']]

                    if photos:
                        if len(photos) > 1:
                            # FIX IS HERE: use_container_width instead of use_column_width
                            st.image(photos[0], use_container_width=True, caption=f"+{len(photos) - 1} more")
                        else:
                            # FIX IS HERE: use_container_width instead of use_column_width
                            st.image(photos[0], use_container_width=True)

                with c_txt:
                    lbl = "Claim:" if st.session_state.report_mode == 'defensive' else "Defect:"
                    st.write(f"**{lbl} {item['title']}** ({item['category']})")
                    st.caption(item['desc'])
                    st.caption(f"Code: {item.get('code', '-')}")

                with c_del:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.selected_defects.pop(i)
                        st.rerun()

    return st.session_state.client_name, notes, translate, logo_file


# --- CRM DASHBOARD SECTION (Same as before) ---
def render_crm_dashboard():
    with st.sidebar:
        st.markdown("""
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
        .sidebar-icon-btn {
            width: 100%;
            padding: 0.5rem 1rem;
            margin: 0.25rem 0;
            border-radius: 0.25rem;
            border: 1px solid rgba(250, 250, 250, 0.2);
            background-color: rgba(250, 250, 250, 0.1);
            color: rgb(49, 51, 63);
            font-size: 0.875rem;
            font-weight: 400;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: left;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .sidebar-icon-btn:hover {
            background-color: rgba(250, 250, 250, 0.2);
            border-color: rgba(250, 250, 250, 0.3);
        }
        .sidebar-icon-btn.active {
            background-color: #EF4444;
            color: white;
            border-color: #EF4444;
        }
        .sidebar-icon-btn i {
            font-size: 1rem;
            width: 1.2rem;
            text-align: center;
        }
        .sidebar-section-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .sidebar-section-title i {
            font-size: 1.2rem;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("### <div class='sidebar-section-title'><i class='bi bi-building'></i> SAAS Sections</div>", unsafe_allow_html=True)
        st.divider()

        saas_sections = [
            {"icon": "bi-graph-up", "name": "Dashboard", "key": "dashboard"},
            {"icon": "bi-people", "name": "Users", "key": "users"},
            {"icon": "bi-folder", "name": "Files", "key": "files"},
            {"icon": "bi-bar-chart", "name": "Analytics", "key": "analytics"},
            {"icon": "bi-gear", "name": "Settings", "key": "settings"},
            {"icon": "bi-credit-card", "name": "Billing", "key": "billing"},
            {"icon": "bi-bell", "name": "Notifications", "key": "notifications"},
            {"icon": "bi-shield-check", "name": "Security", "key": "security"},
        ]

        # Create HTML buttons with Bootstrap Icons that scroll to sections
        buttons_html_parts = []
        for section in saas_sections:
            buttons_html_parts.append(f"""
            <button class="sidebar-icon-btn" 
                    onclick="scrollToSection('{section['key']}')">
                <i class="bi {section['icon']}"></i>
                <span>{section['name']}</span>
            </button>
            """)

        sidebar_html = f"""
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
        .sidebar-icon-btn {{
            width: 100%;
            padding: 0.5rem 1rem;
            margin: 0.25rem 0;
            border-radius: 0.25rem;
            border: 1px solid rgba(250, 250, 250, 0.2);
            background-color: rgba(250, 250, 250, 0.1);
            color: rgb(49, 51, 63);
            font-size: 0.875rem;
            font-weight: 400;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: left;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .sidebar-icon-btn:hover {{
            background-color: rgba(250, 250, 250, 0.2);
            border-color: rgba(250, 250, 250, 0.3);
        }}
        .sidebar-icon-btn i {{
            font-size: 1rem;
            width: 1.2rem;
            text-align: center;
        }}
        </style>
        <script>
        function scrollToSection(sectionId) {{
            // Find the section element in the parent window (Streamlit's main content area)
            try {{
                // Try to find in parent window
                const parentDoc = window.parent.document;
                const sectionElement = parentDoc.getElementById('section-' + sectionId);
                if (sectionElement) {{
                    sectionElement.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    return;
                }}
                // If not found, try in current window (fallback)
                const currentElement = document.getElementById('section-' + sectionId);
                if (currentElement) {{
                    currentElement.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }} catch (e) {{
                console.log('Scroll error:', e);
            }}
        }}
        </script>
        <div>
            {''.join(buttons_html_parts)}
        </div>
        """
        components.html(sidebar_html, height=len(saas_sections) * 50, scrolling=False)

        st.divider()
        st.markdown("### <div class='sidebar-section-title'><i class='bi bi-lightning-charge'></i> Quick Actions</div>", unsafe_allow_html=True)

        # Quick action buttons - removed since they shouldn't trigger actions

    st.markdown("""
    <style>
    .crm-header { font-size: 2.5rem; font-weight: 600; color: #1d1d1f; }
    .metric-card { background: #fff; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.06); }
    .metric-value { font-size: 2rem; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div id="section-dashboard" class="crm-header">CRM Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div>Total Customers</div>
            <div class="metric-value">{st.session_state.customer_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div>Revenue This Month</div>
            <div class="metric-value">${st.session_state.monthly_revenue:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height: 2.5rem;"></div>', unsafe_allow_html=True)

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
        section[data-testid="stSidebar"] ~ div,
        .main .block-container,
        div[data-testid="stAppViewContainer"] {
            max-width: 100vw !important;
            overflow-x: hidden !important;
        }
        .metric-card * {
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
    }
    .metric-label {
        font-size: 0.875rem;
        color: #86868b;
        font-weight: 500;
        letter-spacing: 0.01em;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
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
    .event-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(0,0,0,0.06);
        transition: all 0.2s ease;
    }
    .event-card:hover {
        background: #f5f5f7;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    </style>
    """, unsafe_allow_html=True)

    def _get_query_param(name: str):
        try:
            values = st.query_params.get(name)
            if not values:
                return None
            return values[0] if isinstance(values, list) else values
        except Exception:
            return None

    # Header with navigation
    col_header1, col_header2 = st.columns([1, 20])
    with col_header1:
        if st.button("←", help="Back to Home", use_container_width=True):
            st.session_state.page = 'home'
            if 'selected_calendar_date' in st.session_state:
                st.session_state.selected_calendar_date = None
            st.rerun()

    # --- CALENDAR SECTION ---
    st.markdown('<div id="section-files" class="section-title">📅 Calendar</div>', unsafe_allow_html=True)

    # Sync selection from query param
    qp_cal = _get_query_param("cal")
    if qp_cal is not None:
        st.session_state.selected_calendar_date = qp_cal or None

    # Get current month calendar data
    today = date.today()
    calendar_data = logic.get_calendar_month_data(today.year, today.month)

    # Calendar container - compact design
    with st.container():
        # Build calendar HTML
        first_date = date(calendar_data['year'], calendar_data['month'], 1)
        first_weekday = first_date.weekday()  # Monday=0, Sunday=6
        first_weekday_sunday = (first_weekday + 1) % 7  # Sunday=0, Monday=1, ..., Saturday=6

        today_str = today.strftime('%Y-%m-%d')

        # Use native Streamlit date picker to update session state
        selected_date = st.session_state.get('selected_calendar_date')
        try:
            picker_default = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else today
        except Exception:
            picker_default = today

        new_picker = st.date_input("", value=picker_default, key='crm_date_input', label_visibility="collapsed")
        new_picker_str = new_picker.strftime('%Y-%m-%d') if new_picker else None
        if new_picker_str != selected_date:
            st.session_state.selected_calendar_date = new_picker_str
            try:
                st.query_params["cal"] = new_picker_str
            except Exception:
                pass
            st.rerun()

        month_name_upper = calendar_data['month_name'].upper()
        day_headers = ['S', 'M', 'T', 'W', 'T', 'F', 'S']

        # Build visual grid
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
        """

        components.html(calendar_component_html, height=360, scrolling=False)

    # Event info panel - appears when day is selected
    if st.session_state.get('selected_calendar_date'):
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

        # Add new event form
        with st.expander("➕ Add New Event", expanded=False):
            with st.form(f"add_event_{selected_date}"):
                event_title = st.text_input("Event Title", placeholder="e.g., Client Meeting", key=f"title_{selected_date}")
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
            👆 Select a day to view or add events
        </div>
        """, unsafe_allow_html=True)

    # --- DEMO USERS SECTION ---
    st.markdown('<div style="height: 3rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div id="section-users" class="section-title">👥 Demo Users</div>', unsafe_allow_html=True)

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
                if st.button(f"{'Hide Files' if is_selected else 'Show Files'}",
                           key=f"toggle_{user_id}", use_container_width=True):
                    if st.session_state.selected_user == user_id:
                        st.session_state.selected_user = None
                    else:
                        st.session_state.selected_user = user_id
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)