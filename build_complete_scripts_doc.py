"""
build_complete_scripts_doc.py
Generates a comprehensive, professionally styled Microsoft Word document (.docx)
containing all 32 Python scripts in the Analysis Tool project.
"""

import os
import sys
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from scripts.scenario_registry import SCENARIO_CATALOG

OUTPUT_FILENAME = "Analysis_Tool_Complete_Scripts.docx"


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, m_val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(m_val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_page_number_to_run(run):
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def setup_document():
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
        # Header
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Regulatory Analysis & Portfolio Audit Suite — Complete Source Scripts")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(148, 163, 184)
        
        # Footer
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun1 = fp.add_run("Confidential & Proprietary  |  Page ")
        frun1.font.name = "Calibri"
        frun1.font.size = Pt(8.5)
        frun1.font.color.rgb = RGBColor(148, 163, 184)
        frun2 = fp.add_run()
        add_page_number_to_run(frun2)
        frun2.font.name = "Calibri"
        frun2.font.size = Pt(8.5)
        frun2.font.color.rgb = RGBColor(148, 163, 184)

    return doc


def add_cover_page(doc):
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(36)
    title_p.paragraph_format.space_after = Pt(8)
    trun = title_p.add_run("Regulatory Analysis & Portfolio Audit Suite")
    trun.font.name = "Calibri"
    trun.font.size = Pt(28)
    trun.font.bold = True
    trun.font.color.rgb = RGBColor(30, 58, 138)  # Navy Blue

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(24)
    srun = sub_p.add_run("Complete Source Code & Analytical Routines Compilation (32 Python Scripts)")
    srun.font.name = "Calibri"
    srun.font.size = Pt(14)
    srun.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Metadata Card Table
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    meta_items = [
        ("Application Name", "Analysis Tool — Portfolio & Regulatory Audit Portal"),
        ("Architecture", "Dual-Engine: Streamlit Web Dashboard + Standalone High-Speed Batch CLI"),
        ("Script Inventory", "32 Total Python Scripts (Web UI, Scenario Registry, 23 Audit Routines, Tests)"),
        ("File Format Support", "Excel Binary (.xlsb via calamine/pyxlsb), OpenXML (.xlsx), Legacy (.xls)"),
        ("Authentication & DB", "Supabase PostgreSQL Auth with Guest / Demo Mode fallback"),
        ("Environment / Python", "Python 3.14 | Streamlit 1.63 | Pandas 3.0 | python-calamine 0.8"),
    ]

    col_widths = [Inches(2.2), Inches(4.8)]
    for row_idx, (k, v) in enumerate(meta_items):
        row = table.rows[row_idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = col_widths[0]
        c1.width = col_widths[1]
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, top=120, bottom=120, left=150, right=150)
        set_cell_margins(c1, top=120, bottom=120, left=150, right=150)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = "Calibri"
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = RGBColor(15, 23, 42)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_page_break()


def add_table_of_contents(doc, script_catalog):
    h = doc.add_heading("Table of Contents / Script Directory", level=1)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(12)
    for run in h.runs:
        run.font.name = "Calibri"
        run.font.color.rgb = RGBColor(30, 58, 138)

    desc_p = doc.add_paragraph("This document compiles the complete, unabridged source code for all 32 Python files comprising the Analysis Tool platform, categorized by system tier.")
    desc_p.paragraph_format.space_after = Pt(14)
    desc_p.runs[0].font.name = "Calibri"
    desc_p.runs[0].font.size = Pt(10)
    desc_p.runs[0].font.color.rgb = RGBColor(71, 85, 105)

    table = doc.add_table(rows=1 + len(script_catalog), cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Inches(0.5), Inches(2.2), Inches(1.8), Inches(2.5)]

    # Header row
    headers = ["#", "File Path", "Module / Scenario Title", "Category / Function"]
    hdr_row = table.rows[0]
    for idx, text in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.width = col_widths[idx]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=120, bottom=120, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(255, 255, 255)

    # Data rows
    for row_idx, item in enumerate(script_catalog, start=1):
        row = table.rows[row_idx]
        bg = "FFFFFF" if row_idx % 2 != 0 else "F8FAFC"
        vals = [str(row_idx), item["rel_path"], item["title"], item["category"]]
        for col_idx, val in enumerate(vals):
            cell = row.cells[col_idx]
            cell.width = col_widths[col_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(val)
            run.font.name = "Calibri"
            run.font.size = Pt(8.5)
            if col_idx == 0:
                run.font.bold = True
                run.font.color.rgb = RGBColor(100, 116, 139)
            elif col_idx == 1:
                run.font.bold = True
                run.font.color.rgb = RGBColor(15, 23, 42)
            else:
                run.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_page_break()


def render_code_block(doc, code_text):
    """Renders formatted monospace code lines with subtle indentation and compact spacing."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.left_indent = Inches(0.2)

    # Shading and left border
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>'))
    pPr.append(parse_xml(f'<w:pBdr {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="10" w:color="3B82F6"/></w:pBdr>'))

    lines = code_text.splitlines()
    for i, line in enumerate(lines):
        run = p.add_run(line if line else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(8.0)
        run.font.color.rgb = RGBColor(30, 41, 59)
        if i < len(lines) - 1:
            p.add_run().add_break()


def add_script_section(doc, script_meta):
    """Adds a single script with title, metadata callout card, and full source code."""
    h = doc.add_heading(f"{script_meta['index']}. {script_meta['title']}", level=2)
    h.paragraph_format.space_before = Pt(18)
    h.paragraph_format.space_after = Pt(6)
    for run in h.runs:
        run.font.name = "Calibri"
        run.font.color.rgb = RGBColor(37, 99, 235)

    meta_rows = [
        ("File Path", script_meta["rel_path"]),
        ("Category & Purpose", f"{script_meta['category']} — {script_meta['description']}"),
    ]
    if script_meta.get("output_name"):
        meta_rows.append(("Target Output File", script_meta["output_name"]))

    table = doc.add_table(rows=len(meta_rows), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    col_w = [Inches(1.8), Inches(5.2)]

    for row_idx, (k, v) in enumerate(meta_rows):
        row = table.rows[row_idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = col_w[0]
        c1.width = col_w[1]
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = "Calibri"
        r0.font.bold = True
        r0.font.size = Pt(8.5)
        r0.font.color.rgb = RGBColor(15, 23, 42)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = "Calibri"
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Render source code
    with open(script_meta["abs_path"], "r", encoding="utf-8") as f:
        code_content = f.read()

    render_code_block(doc, code_content)


def build_catalog():
    catalog = []

    # 1. Root application scripts
    catalog.append({
        "rel_path": "Analysis tool.py",
        "title": "Main Web Application Dashboard (Streamlit SaaS Portal)",
        "category": "Web Dashboard",
        "description": "Interactive web dashboard featuring Supabase Auth, guest mode, high-speed multi-engine file upload (.xlsb/.xlsx/.xls), 3 quick action audit buttons, and a 23-scenario registry runner with Excel export.",
        "output_name": "Interactive browser session + Excel download"
    })
    catalog.append({
        "rel_path": "app.py",
        "title": "Streamlit Launcher Script",
        "category": "Application Entry Point",
        "description": "Standardized entry point allowing execution via 'streamlit run app.py' avoiding spaces in filename.",
        "output_name": "Starts Streamlit server on app.py"
    })
    catalog.append({
        "rel_path": "main.py",
        "title": "CLI Application Orchestrator",
        "category": "Application Launcher",
        "description": "Cross-platform UTF-8 terminal launcher that spawns Streamlit in a managed subprocess.",
        "output_name": "Subprocess execution"
    })

    # 2. Scenario Registry & Core analytical modules
    catalog.append({
        "rel_path": "scripts/scenario_registry.py",
        "title": "Scenario Registry & Runtime Engine",
        "category": "Core Architecture",
        "description": "Central catalog defining metadata, categories, target outputs, and dynamic run(df) execution dispatch for all 23 audit scenarios.",
        "output_name": "Scenario metadata dictionary & execution router"
    })
    catalog.append({
        "rel_path": "scripts/script_CRE_kyc.py",
        "title": "CRE KYC Analysis Module",
        "category": "Core Analysis",
        "description": "Identifies Commercial Real Estate repeated accounts (>=3) across multiple unique dwellings or assets.",
        "output_name": "CRE_cases_pan.xlsx"
    })
    catalog.append({
        "rel_path": "scripts/script_UCIC_cases.py",
        "title": "UCIC Discrepancy Module",
        "category": "Core Analysis",
        "description": "Detects one-to-many mismatches between Unique Customer Identification Codes (UCIC) and KYC/PAN records.",
        "output_name": "UCIC_cases.xlsx"
    })
    catalog.append({
        "rel_path": "scripts/script_NPA_valuation.py",
        "title": "NPA Property Valuation Module",
        "category": "Core Analysis",
        "description": "Audits overdue property valuations based on Non-Performing Asset (NPA) classification date rules.",
        "output_name": "NPA_valuation.xlsx"
    })
    catalog.append({
        "rel_path": "scripts/__init__.py",
        "title": "Scripts Package Initialization",
        "category": "Package Module",
        "description": "Exports core analytical modules (script_CRE_kyc, script_UCIC_cases, script_NPA_valuation, scenario_registry).",
        "output_name": "Python package exports"
    })

    # 3. Numbered 23-scenario analytical routines
    # Map from scenario catalog
    sc_dict = SCENARIO_CATALOG

    for i in range(1, 24):
        num_str = f"{i:02d}"
        # Find file matching scripts/XX_*.py
        matches = [f for f in os.listdir(PROJECT_ROOT / "scripts") if f.startswith(f"{num_str}_") and f.endswith(".py")]
        if matches:
            filename = matches[0]
            script_key = filename[:-3]
            meta = sc_dict.get(script_key, {})
            catalog.append({
                "rel_path": f"scripts/{filename}",
                "title": meta.get("title", filename),
                "category": meta.get("category", "Regulatory Audit"),
                "description": meta.get("description", "Dedicated analytical audit routine with dual in-memory run(df) and standalone CLI execution."),
                "output_name": meta.get("output_name", f"output_{filename[:-3]}.xlsx")
            })

    # 4. Verification Suite
    catalog.append({
        "rel_path": "test_suite.py",
        "title": "Automated Verification & Test Suite",
        "category": "Testing & QA",
        "description": "Automated test suite executing integration tests across CRE KYC, UCIC, NPA Valuation, edge cases, and all 23 scenario routines.",
        "output_name": "Terminal verification results"
    })

    # Assign 1-based index and absolute path
    for idx, item in enumerate(catalog, start=1):
        item["index"] = idx
        item["abs_path"] = str(PROJECT_ROOT / item["rel_path"].replace("/", os.sep))

    return catalog


def main():
    print("⚡ Building Complete Scripts Word Document...")
    catalog = build_catalog()
    print(f"Loaded catalog with {len(catalog)} scripts.")

    doc = setup_document()

    # 1. Cover Page
    add_cover_page(doc)

    # 2. Table of Contents
    add_table_of_contents(doc, catalog)

    # Group scripts into logical sections with Major Headings
    sections = [
        ("Section 1: Main Application & Web Dashboard", [1, 2, 3]),
        ("Section 2: Scenario Registry & Core Analytical Engines", [4, 5, 6, 7, 8]),
        ("Section 3: Complete 23-Scenario Regulatory Audit Suite", list(range(9, 32))),
        ("Section 4: Automated Verification & Test Suite", [32]),
    ]

    for sec_title, script_indices in sections:
        sec_h = doc.add_heading(sec_title, level=1)
        sec_h.paragraph_format.space_before = Pt(24)
        sec_h.paragraph_format.space_after = Pt(12)
        for run in sec_h.runs:
            run.font.name = "Calibri"
            run.font.color.rgb = RGBColor(30, 58, 138)

        for s_idx in script_indices:
            script_meta = catalog[s_idx - 1]
            print(f"  Adding [{script_meta['index']}/32]: {script_meta['rel_path']}")
            add_script_section(doc, script_meta)

    out_path = PROJECT_ROOT / OUTPUT_FILENAME
    doc.save(str(out_path))
    file_size_kb = round(os.path.getsize(str(out_path)) / 1024, 1)
    print(f"🎉 Successfully generated: {out_path} ({file_size_kb} KB)")


if __name__ == "__main__":
    main()
