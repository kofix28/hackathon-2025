"""
Backend Logic for FieldScribe
Handles translation, image compression, and Word document generation
"""

from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from deep_translator import GoogleTranslator
from datetime import datetime
from PIL import Image


def compress_image(image_file, max_width=800):
    """
    Takes a huge image file, resizes it, and returns a compressed byte stream.
    Handles PNG transparency to prevent crashes.
    """
    try:
        image = Image.open(image_file)

        # 1. FIX PNG CRASH: Convert RGBA (Transparent) to RGB (Solid)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # 2. Resize
        width_percent = (max_width / float(image.size[0]))
        new_height = int((float(image.size[1]) * float(width_percent)))
        image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # 3. Save
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=70, optimize=True)
        img_byte_arr.seek(0)
        return img_byte_arr
    except Exception as e:
        print(f"Image compression error: {e}")
        return None


def process_report(client_name, general_notes, defect_list, should_translate, report_mode='standard'):
    """
    Generates the Word Doc. Adapts headers based on 'report_mode'.
    """
    doc = Document()

    # --- HELPER: Translator ---
    def t(text):
        if should_translate and text:
            try:
                return GoogleTranslator(source='auto', target='ar').translate(text)
            except:
                return text
        return text

    # --- STYLE SETUP ---
    try:
        style = doc.styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(11)
    except:
        pass

    # --- HEADER ---
    header_section = doc.sections[0]
    header = header_section.header
    htable = header.add_table(1, 2, width=Inches(6))
    htable.autofit = False
    htable.columns[0].width = Inches(4)
    htable.columns[1].width = Inches(2)
    htable.cell(0, 0).text = "FIELDSCRIBE INSPECTION SYSTEM"
    htable.cell(0, 1).text = datetime.now().strftime("%Y-%m-%d")

    # --- TITLE PAGE ---
    title_text = f"DEFENSIVE OPINION: {client_name.upper()}" if report_mode == 'defensive' else f"INSPECTION REPORT: {client_name.upper()}"
    title = doc.add_heading(t(title_text), 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    meta_table = doc.add_table(rows=1, cols=2)
    meta_table.style = 'Table Grid'
    meta_table.rows[0].cells[0].text = t(f"Property: {client_name}")
    meta_table.rows[0].cells[1].text = t(f"Inspector: Field Engineer")
    doc.add_paragraph()

    # --- 1. EXECUTIVE SUMMARY ---
    doc.add_heading(t("1. EXECUTIVE SUMMARY"), level=1)
    if general_notes:
        doc.add_paragraph(t(general_notes))
    else:
        doc.add_paragraph(t("No specific general notes provided."))
    doc.add_paragraph()

    # --- 2. DETAILED FINDINGS ---
    # Dynamic Heading
    heading_text = "2. DEFENSIVE REBUTTAL & FINDINGS" if report_mode == 'defensive' else "2. FINDINGS & DEFECTS"
    doc.add_heading(t(heading_text), level=1)

    if defect_list:
        table = doc.add_table(rows=1, cols=5)
        try:
            table.style = 'Light Shading Accent 1'
        except:
            table.style = 'Table Grid'

        # --- DYNAMIC HEADERS ---
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = t("ID")
        hdr_cells[1].text = t("Category")

        if report_mode == 'defensive':
            hdr_cells[2].text = t("Claim vs. Finding")
        else:
            hdr_cells[2].text = t("Defect Description")

        hdr_cells[3].text = t("Standard")
        hdr_cells[4].text = t("Severity")

        # Fill Data
        for i, defect in enumerate(defect_list):
            row_cells = table.add_row().cells
            row_cells[0].text = str(i + 1).zfill(2)
            row_cells[1].text = t(defect.get('category', 'General'))

            # FORMATTING THE DESCRIPTION
            title = defect.get('title', '')
            desc = defect.get('desc', '')

            if report_mode == 'defensive':
                full_text = f"CLAIM: {title}\n\nFINDING: {desc}"
            else:
                full_text = f"{title}\n{desc}"

            row_cells[2].text = t(full_text)

            # --- INSERT PHOTOS (Robust Logic) ---

            # Case A: Multiple Photos (New System)
            if 'photos' in defect and defect['photos']:
                try:
                    paragraph = row_cells[2].paragraphs[0]
                    for photo_file in defect['photos']:
                        compressed = compress_image(photo_file)
                        if compressed:
                            run = paragraph.add_run()
                            run.add_break()
                            run.add_picture(compressed, width=Inches(1.5))
                            run.add_text("  ")  # Space between images
                except Exception as e:
                    print(f"Error adding photos: {e}")

            # Case B: Single Photo (Old System - Backwards Compatibility)
            elif 'photo' in defect and defect['photo']:
                try:
                    compressed = compress_image(defect['photo'])
                    if compressed:
                        p = row_cells[2].paragraphs[0]
                        r = p.add_run()
                        r.add_break()
                        r.add_picture(compressed, width=Inches(1.5))
                except Exception as e:
                    print(f"Error adding single photo: {e}")

            row_cells[3].text = defect.get('code', '-')
            row_cells[4].text = t("Medium")
    else:
        doc.add_paragraph(t("No items recorded."))

    # --- 3. DISCLAIMER ---
    doc.add_page_break()
    doc.add_heading(t("3. LIMITATIONS & DISCLAIMER"), level=1)
    disclaimer_text = "This report is a visual inspection only. Opinions are based on the condition at the time of inspection."
    p = doc.add_paragraph(t(disclaimer_text))

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer