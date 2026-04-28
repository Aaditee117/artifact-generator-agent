"""Generate Azure Cost Report in Microsoft Azure Estimate format as Excel file.
Supports both POC (Proof of Concept) and MVP (Minimum Viable Product) phases.
Generates output matching the official Azure Pricing Calculator export format.
Reference: https://azure.microsoft.com/en-in/pricing/calculator/
"""

from io import BytesIO
from datetime import datetime, timezone

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    Workbook = None
    Font = None
    PatternFill = None
    Alignment = None
    Border = None
    Side = None
    get_column_letter = None

# Microsoft Azure Pricing Calculator exact color scheme
HEADER_GREEN_HEX = "217346"  # Dark green for header row (Azure standard)
ALT_ROW_GREEN_HEX = "E2EFDA"  # Light green for alternating rows
POC_BLUE_HEX = "1F4E79"      # Blue for POC header
MVP_ORANGE_HEX = "C65911"    # Orange for MVP header
ALT_ROW_BLUE_HEX = "D6DCE4"  # Light blue for POC alternating rows
ALT_ROW_ORANGE_HEX = "FCE4D6" # Light orange for MVP alternating rows
WHITE_HEX = "FFFFFF"
BLACK_HEX = "000000"
GRAY_HEX = "666666"
CURRENCY_FMT = '"$"#,##0.00'

# Azure Pricing Calculator reference URL
AZURE_PRICING_CALCULATOR_URL = "https://azure.microsoft.com/pricing/calculator/"


def _get_styles(phase_type: str = "default"):
    """Return style objects matching Microsoft Azure Estimate format.

    Args:
        phase_type: 'poc', 'mvp', or 'default' for different color schemes
    """
    # Select colors based on phase
    if phase_type.lower() == "poc":
        header_color = POC_BLUE_HEX
        alt_row_color = ALT_ROW_BLUE_HEX
    elif phase_type.lower() == "mvp":
        header_color = MVP_ORANGE_HEX
        alt_row_color = ALT_ROW_ORANGE_HEX
    else:
        header_color = HEADER_GREEN_HEX
        alt_row_color = ALT_ROW_GREEN_HEX

    return {
        "thin_border": Border(
            left=Side(style="thin", color="D9D9D9"),
            right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"),
            bottom=Side(style="thin", color="D9D9D9"),
        ),
        "header_font": Font(name="Segoe UI", size=10, bold=True, color=WHITE_HEX),
        "header_fill": PatternFill(start_color=header_color, end_color=header_color, fill_type="solid"),
        "title_font": Font(name="Segoe UI", size=14, bold=True, color=BLACK_HEX),
        "subtitle_font": Font(name="Segoe UI", size=11, bold=True, color=header_color),
        "normal_font": Font(name="Segoe UI", size=9, color=BLACK_HEX),
        "alt_row_fill": PatternFill(start_color=alt_row_color, end_color=alt_row_color, fill_type="solid"),
        "white_fill": PatternFill(start_color=WHITE_HEX, end_color=WHITE_HEX, fill_type="solid"),
    }


def _create_phase_sheet(wb, sheet_name: str, phase_data: dict, phase_type: str):
    """Create a worksheet for a specific phase (POC or MVP).

    Matches the exact format of Azure Pricing Calculator export.

    Args:
        wb: Workbook instance
        sheet_name: Name for the sheet
        phase_data: Dictionary containing phase-specific services and summary
        phase_type: 'poc' or 'mvp' for styling
    """
    styles = _get_styles(phase_type)
    THIN_BORDER = styles["thin_border"]
    HEADER_FONT = styles["header_font"]
    HEADER_FILL = styles["header_fill"]
    TITLE_FONT = styles["title_font"]
    SUBTITLE_FONT = styles["subtitle_font"]
    NORMAL_FONT = styles["normal_font"]
    ALT_ROW_FILL = styles["alt_row_fill"]
    WHITE_FILL = styles["white_fill"]

    ws = wb.create_sheet(title=sheet_name[:31])

    # Row 1: Title - "Microsoft Azure Estimate" (matches Azure Pricing Calculator)
    ws["A1"] = "Microsoft Azure Estimate"
    ws["A1"].font = TITLE_FONT

    # Row 2: Project/Client name (like "Opti-Studio" in the screenshot)
    client_name = phase_data.get("client", phase_data.get("phase_name", sheet_name))
    ws["A2"] = client_name
    ws["A2"].font = SUBTITLE_FONT

    # Row 3: Column Headers (exact Azure Pricing Calculator format)
    headers = [
        "Service category",
        "Service type", 
        "Custom name",
        "Region",
        "Description",
        "Estimated monthly cost",
        "Estimated upfront cost"
    ]

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER

    # Row 4+: Service data rows
    row = 4
    services = phase_data.get("services", [])

    for idx, svc in enumerate(services):
        row_fill = ALT_ROW_FILL if idx % 2 == 0 else WHITE_FILL

        # Column A: Service category
        cell_a = ws.cell(row=row, column=1, value=svc.get("service_category", svc.get("category", "")))
        cell_a.font = NORMAL_FONT
        cell_a.fill = row_fill
        cell_a.border = THIN_BORDER
        cell_a.alignment = Alignment(vertical="top", wrap_text=True)

        # Column B: Service type
        cell_b = ws.cell(row=row, column=2, value=svc.get("service_type", svc.get("service_name", "")))
        cell_b.font = NORMAL_FONT
        cell_b.fill = row_fill
        cell_b.border = THIN_BORDER
        cell_b.alignment = Alignment(vertical="top", wrap_text=True)

        # Column C: Custom name
        cell_c = ws.cell(row=row, column=3, value=svc.get("custom_name", ""))
        cell_c.font = NORMAL_FONT
        cell_c.fill = row_fill
        cell_c.border = THIN_BORDER
        cell_c.alignment = Alignment(vertical="top", wrap_text=True)

        # Column D: Region (default to East US 2 like Azure calculator)
        cell_d = ws.cell(row=row, column=4, value=svc.get("region", "East US 2"))
        cell_d.font = NORMAL_FONT
        cell_d.fill = row_fill
        cell_d.border = THIN_BORDER
        cell_d.alignment = Alignment(vertical="top", wrap_text=True)

        # Column E: Description (verbose Azure-style description)
        description = svc.get("description", "")
        if not description:
            parts = [p for p in [svc.get("sku_tier"), svc.get("notes"), svc.get("why_needed")] if p]
            description = ", ".join(parts)
        cell_e = ws.cell(row=row, column=5, value=description)
        cell_e.font = NORMAL_FONT
        cell_e.fill = row_fill
        cell_e.border = THIN_BORDER
        cell_e.alignment = Alignment(vertical="top", wrap_text=True)

        # Column F: Estimated monthly cost
        monthly_cost = svc.get("estimated_monthly_cost", svc.get("monthly_cost", 0))
        cell_f = ws.cell(row=row, column=6, value=monthly_cost)
        cell_f.font = NORMAL_FONT
        cell_f.fill = row_fill
        cell_f.border = THIN_BORDER
        cell_f.number_format = CURRENCY_FMT
        cell_f.alignment = Alignment(vertical="top")

        # Column G: Estimated upfront cost
        upfront_cost = svc.get("estimated_upfront_cost", svc.get("upfront_cost", 0))
        cell_g = ws.cell(row=row, column=7, value=upfront_cost)
        cell_g.font = NORMAL_FONT
        cell_g.fill = row_fill
        cell_g.border = THIN_BORDER
        cell_g.number_format = CURRENCY_FMT
        cell_g.alignment = Alignment(vertical="top")

        row += 1

    # Footer rows (matches Azure Pricing Calculator export format)
    footer = phase_data.get("footer", {})

    # Support row
    row += 1
    ws.cell(row=row, column=1, value="Support").font = NORMAL_FONT
    ws.cell(row=row, column=4, value="Support").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)
    support_cost = footer.get("support_monthly", 0.00)
    ws.cell(row=row, column=6, value=support_cost).number_format = CURRENCY_FMT
    ws.cell(row=row, column=6).font = NORMAL_FONT
    ws.cell(row=row, column=7, value=0.00).number_format = CURRENCY_FMT
    ws.cell(row=row, column=7).font = NORMAL_FONT

    # Licensing Program row
    row += 1
    ws.cell(row=row, column=4, value="Licensing Program").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)
    ws.cell(row=row, column=5, value=footer.get("licensing_program", "Microsoft Customer Agreement (MCA)")).font = NORMAL_FONT

    # Billing Account row
    row += 1
    ws.cell(row=row, column=4, value="Billing Account").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)
    ws.cell(row=row, column=5, value=footer.get("billing_account", "")).font = NORMAL_FONT

    # Billing Profile row
    row += 1
    ws.cell(row=row, column=4, value="Billing Profile").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)
    ws.cell(row=row, column=5, value=footer.get("billing_profile", "")).font = NORMAL_FONT

    # Total row
    row += 1
    ws.cell(row=row, column=4, value="Total").font = Font(name="Segoe UI", size=11, bold=True, color=BLACK_HEX)

    total_monthly = phase_data.get("summary", {}).get("total_monthly", 0)
    if not total_monthly:
        total_monthly = sum(s.get("estimated_monthly_cost", s.get("monthly_cost", 0)) for s in services)

    total_upfront = phase_data.get("summary", {}).get("upfront_cost", 0)
    if not total_upfront:
        total_upfront = sum(s.get("estimated_upfront_cost", s.get("upfront_cost", 0)) for s in services)

    grand_total_monthly = total_monthly + support_cost
    ws.cell(row=row, column=6, value=grand_total_monthly).number_format = CURRENCY_FMT
    ws.cell(row=row, column=6).font = Font(name="Segoe UI", size=10, bold=True, color=BLACK_HEX)
    ws.cell(row=row, column=7, value=total_upfront).number_format = CURRENCY_FMT
    ws.cell(row=row, column=7).font = Font(name="Segoe UI", size=10, bold=True, color=BLACK_HEX)

    # Empty row
    row += 2

    # Disclaimer row (like Azure Pricing Calculator)
    ws.cell(row=row, column=1, value="Disclaimer").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)

    row += 1
    disclaimer_text = "All prices shown are in United States – Dollar ($) USD. This is a summary estimate, not a quote. For up to date pricing information please visit https://azure.microsoft.com/pricing/calculator/"
    ws.cell(row=row, column=1, value=disclaimer_text).font = Font(name="Segoe UI", size=8, color=GRAY_HEX)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)

    row += 1
    timestamp = datetime.now(timezone.utc).strftime("%m/%d/%Y %I:%M:%S %p UTC")
    ws.cell(row=row, column=1, value=f"This estimate was created at {timestamp}").font = Font(name="Segoe UI", size=8, color=GRAY_HEX)

    # Set column widths (matching Azure Pricing Calculator export)
    column_widths = {"A": 18, "B": 22, "C": 15, "D": 15, "E": 55, "F": 22, "G": 22}
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    # Set row heights
    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 18
    ws.row_dimensions[3].height = 25

    # Freeze header row
    ws.freeze_panes = "A4"

    return ws


def _create_comparison_sheet(wb, poc_data: dict, mvp_data: dict):
    """Create a comparison sheet showing POC vs MVP costs side by side."""
    styles = _get_styles("default")
    THIN_BORDER = styles["thin_border"]
    HEADER_FONT = styles["header_font"]
    HEADER_FILL = styles["header_fill"]
    TITLE_FONT = styles["title_font"]
    NORMAL_FONT = styles["normal_font"]

    ws = wb.create_sheet(title="POC vs MVP Comparison")

    # Title
    ws["A1"] = "Azure Cost Comparison: POC vs MVP"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:F1")

    # Headers
    headers = ["Service Category", "Service Type", "POC Monthly", "MVP Monthly", "Difference", "% Change"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = THIN_BORDER

    # Combine services for comparison
    poc_services = {(s.get("service_category", s.get("category", "")), s.get("service_type", s.get("service_name", ""))): s 
                    for s in poc_data.get("services", [])}
    mvp_services = {(s.get("service_category", s.get("category", "")), s.get("service_type", s.get("service_name", ""))): s 
                    for s in mvp_data.get("services", [])}

    all_service_keys = set(poc_services.keys()) | set(mvp_services.keys())

    row = 4
    for (category, service_type) in sorted(all_service_keys):
        poc_svc = poc_services.get((category, service_type), {})
        mvp_svc = mvp_services.get((category, service_type), {})

        poc_cost = poc_svc.get("estimated_monthly_cost", poc_svc.get("monthly_cost", 0))
        mvp_cost = mvp_svc.get("estimated_monthly_cost", mvp_svc.get("monthly_cost", 0))
        difference = mvp_cost - poc_cost
        pct_change = ((mvp_cost - poc_cost) / poc_cost * 100) if poc_cost > 0 else (100 if mvp_cost > 0 else 0)

        ws.cell(row=row, column=1, value=category).font = NORMAL_FONT
        ws.cell(row=row, column=2, value=service_type).font = NORMAL_FONT
        ws.cell(row=row, column=3, value=poc_cost).number_format = CURRENCY_FMT
        ws.cell(row=row, column=4, value=mvp_cost).number_format = CURRENCY_FMT
        ws.cell(row=row, column=5, value=difference).number_format = CURRENCY_FMT
        ws.cell(row=row, column=6, value=pct_change).number_format = '0.0"%"'

        for col in range(1, 7):
            ws.cell(row=row, column=col).border = THIN_BORDER

        row += 1

    # Totals row
    row += 1
    ws.cell(row=row, column=2, value="TOTAL").font = Font(name="Segoe UI", size=10, bold=True)

    poc_total = poc_data.get("summary", {}).get("total_monthly", 0)
    if not poc_total:
        poc_total = sum(s.get("estimated_monthly_cost", s.get("monthly_cost", 0)) for s in poc_data.get("services", []))

    mvp_total = mvp_data.get("summary", {}).get("total_monthly", 0)
    if not mvp_total:
        mvp_total = sum(s.get("estimated_monthly_cost", s.get("monthly_cost", 0)) for s in mvp_data.get("services", []))

    total_diff = mvp_total - poc_total
    total_pct = ((mvp_total - poc_total) / poc_total * 100) if poc_total > 0 else 0

    ws.cell(row=row, column=3, value=poc_total).number_format = CURRENCY_FMT
    ws.cell(row=row, column=3).font = Font(name="Segoe UI", size=10, bold=True)
    ws.cell(row=row, column=3).fill = PatternFill(start_color=POC_BLUE_HEX, end_color=POC_BLUE_HEX, fill_type="solid")
    ws.cell(row=row, column=3).font = Font(name="Segoe UI", size=10, bold=True, color=WHITE_HEX)

    ws.cell(row=row, column=4, value=mvp_total).number_format = CURRENCY_FMT
    ws.cell(row=row, column=4).fill = PatternFill(start_color=MVP_ORANGE_HEX, end_color=MVP_ORANGE_HEX, fill_type="solid")
    ws.cell(row=row, column=4).font = Font(name="Segoe UI", size=10, bold=True, color=WHITE_HEX)

    ws.cell(row=row, column=5, value=total_diff).number_format = CURRENCY_FMT
    ws.cell(row=row, column=5).font = Font(name="Segoe UI", size=10, bold=True)

    ws.cell(row=row, column=6, value=total_pct).number_format = '0.0"%"'
    ws.cell(row=row, column=6).font = Font(name="Segoe UI", size=10, bold=True)

    # Column widths
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 15
    ws.column_dimensions["F"].width = 12

    ws.freeze_panes = "A4"

    return ws


def _create_summary_sheet(ws, poc_data: dict, mvp_data: dict):
    """Create the summary sheet as the first sheet."""
    styles = _get_styles("default")
    TITLE_FONT = styles["title_font"]
    SUBTITLE_FONT = styles["subtitle_font"]
    NORMAL_FONT = styles["normal_font"]
    HEADER_FILL = styles["header_fill"]
    HEADER_FONT = styles["header_font"]
    THIN_BORDER = styles["thin_border"]

    ws.title = "Summary"

    # Title
    ws["A1"] = "Microsoft Azure Cost Estimate"
    ws["A1"].font = TITLE_FONT

    ws["A2"] = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
    ws["A2"].font = Font(name="Segoe UI", size=10, color="666666")

    # Summary table
    row = 4
    ws.cell(row=row, column=1, value="Phase").font = HEADER_FONT
    ws.cell(row=row, column=1).fill = HEADER_FILL
    ws.cell(row=row, column=2, value="Monthly Cost").font = HEADER_FONT
    ws.cell(row=row, column=2).fill = HEADER_FILL
    ws.cell(row=row, column=3, value="Annual Cost").font = HEADER_FONT
    ws.cell(row=row, column=3).fill = HEADER_FILL
    ws.cell(row=row, column=4, value="Services Count").font = HEADER_FONT
    ws.cell(row=row, column=4).fill = HEADER_FILL

    for col in range(1, 5):
        ws.cell(row=row, column=col).border = THIN_BORDER
        ws.cell(row=row, column=col).alignment = Alignment(horizontal="center")

    # POC row
    row += 1
    poc_monthly = poc_data.get("summary", {}).get("total_monthly", 0)
    if not poc_monthly:
        poc_monthly = sum(s.get("estimated_monthly_cost", s.get("monthly_cost", 0)) for s in poc_data.get("services", []))
    poc_services_count = len(poc_data.get("services", []))

    ws.cell(row=row, column=1, value="POC (Proof of Concept)").font = Font(name="Segoe UI", size=10, bold=True, color=POC_BLUE_HEX)
    ws.cell(row=row, column=2, value=poc_monthly).number_format = CURRENCY_FMT
    ws.cell(row=row, column=3, value=poc_monthly * 12).number_format = CURRENCY_FMT
    ws.cell(row=row, column=4, value=poc_services_count)
    for col in range(1, 5):
        ws.cell(row=row, column=col).border = THIN_BORDER

    # MVP row
    row += 1
    mvp_monthly = mvp_data.get("summary", {}).get("total_monthly", 0)
    if not mvp_monthly:
        mvp_monthly = sum(s.get("estimated_monthly_cost", s.get("monthly_cost", 0)) for s in mvp_data.get("services", []))
    mvp_services_count = len(mvp_data.get("services", []))

    ws.cell(row=row, column=1, value="MVP (Minimum Viable Product)").font = Font(name="Segoe UI", size=10, bold=True, color=MVP_ORANGE_HEX)
    ws.cell(row=row, column=2, value=mvp_monthly).number_format = CURRENCY_FMT
    ws.cell(row=row, column=3, value=mvp_monthly * 12).number_format = CURRENCY_FMT
    ws.cell(row=row, column=4, value=mvp_services_count)
    for col in range(1, 5):
        ws.cell(row=row, column=col).border = THIN_BORDER

    # Cost difference info
    row += 2
    diff = mvp_monthly - poc_monthly
    ws.cell(row=row, column=1, value="MVP vs POC Difference:").font = Font(name="Segoe UI", size=10, bold=True)
    ws.cell(row=row, column=2, value=diff).number_format = CURRENCY_FMT
    ws.cell(row=row, column=2).font = Font(name="Segoe UI", size=10, bold=True, color="C65911" if diff > 0 else "217346")

    # Column widths
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 15


def generate_cost_excel(data: dict) -> bytes:
    """Generate Excel cost report with POC or MVP phase.

    Generates output matching the official Azure Pricing Calculator export format.
    Reference: https://azure.microsoft.com/en-in/pricing/calculator/

    Single-phase behavior:
    - POC selected → Single sheet with POC estimate only
    - MVP selected → Single sheet with MVP estimate only

    Multi-phase behavior (when both poc and mvp keys exist):
    - Creates Summary, POC, MVP, and Comparison sheets

    The data structure should contain:
    - For single phase: services array at top level with phase_name
    - For multi-phase: poc and mvp keys with services arrays
    """
    if not HAS_OPENPYXL:
        raise ImportError("openpyxl is required. Install with: pip install openpyxl")

    wb = Workbook()

    # Check if we have POC and MVP data (multi-phase report)
    poc_data = data.get("poc", {})
    mvp_data = data.get("mvp", {})

    if poc_data and mvp_data:
        # Create multi-phase report with SEPARATE sheets for POC and MVP
        ws_summary = wb.active
        _create_summary_sheet(ws_summary, poc_data, mvp_data)
        _create_phase_sheet(wb, "POC", poc_data, "poc")
        _create_phase_sheet(wb, "MVP", mvp_data, "mvp")
        _create_comparison_sheet(wb, poc_data, mvp_data)

    else:
        # SINGLE PHASE REPORT - Only one sheet
        # Determine phase type from phase_name
        phase_name = data.get("phase_name", data.get("environment_type", ""))

        if "poc" in phase_name.lower() or poc_data:
            phase_type = "poc"
            sheet_title = "POC"
            phase_data = poc_data if poc_data else data
        elif "mvp" in phase_name.lower() or mvp_data:
            phase_type = "mvp"
            sheet_title = "MVP"
            phase_data = mvp_data if mvp_data else data
        else:
            phase_type = "default"
            sheet_title = "Azure Estimate"
            phase_data = data

        # Remove default sheet and create single phase sheet
        wb.remove(wb.active)
        _create_single_sheet(wb, sheet_title, phase_data, phase_type)

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _create_single_sheet(wb, sheet_name: str, data: dict, phase_type: str):
    """Create a single worksheet for POC or MVP estimate.

    This creates exactly one sheet matching Azure Pricing Calculator export format.
    """
    styles = _get_styles(phase_type)
    THIN_BORDER = styles["thin_border"]
    HEADER_FONT = styles["header_font"]
    HEADER_FILL = styles["header_fill"]
    TITLE_FONT = styles["title_font"]
    SUBTITLE_FONT = styles["subtitle_font"]
    NORMAL_FONT = styles["normal_font"]
    ALT_ROW_FILL = styles["alt_row_fill"]
    WHITE_FILL = styles["white_fill"]

    ws = wb.create_sheet(title=sheet_name[:31])

    # Row 1: Title - "Microsoft Azure Estimate"
    ws["A1"] = "Microsoft Azure Estimate"
    ws["A1"].font = TITLE_FONT

    # Row 2: Client/Project name
    client_name = data.get("client", data.get("phase_name", sheet_name))
    ws["A2"] = client_name
    ws["A2"].font = SUBTITLE_FONT

    # Row 3: Headers (exact Azure Pricing Calculator format)
    headers = ["Service category", "Service type", "Custom name", "Region", 
               "Description", "Estimated monthly cost", "Estimated upfront cost"]

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER

    # Row 4+: Service data rows
    row = 4
    services = data.get("services", [])
    if not services and data.get("environments"):
        for env in data.get("environments", []):
            services.extend(env.get("services", []))

    for idx, svc in enumerate(services):
        row_fill = ALT_ROW_FILL if idx % 2 == 0 else WHITE_FILL

        values = [
            svc.get("service_category", svc.get("category", "")),
            svc.get("service_type", svc.get("service_name", "")),
            svc.get("custom_name", ""),
            svc.get("region", "East US 2"),
            svc.get("description", ""),
            svc.get("estimated_monthly_cost", svc.get("monthly_cost", 0)),
            svc.get("estimated_upfront_cost", svc.get("upfront_cost", 0))
        ]

        for col, val in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.font = NORMAL_FONT
            cell.fill = row_fill
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if col in (6, 7):
                cell.number_format = CURRENCY_FMT
        row += 1

    # Footer section (matching Azure Calculator)
    footer = data.get("footer", {})

    # Support row
    row += 1
    ws.cell(row=row, column=1, value="Support").font = NORMAL_FONT
    ws.cell(row=row, column=4, value="Support").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)
    support_cost = footer.get("support_monthly", 0.00)
    ws.cell(row=row, column=6, value=support_cost).number_format = CURRENCY_FMT
    ws.cell(row=row, column=6).font = NORMAL_FONT
    ws.cell(row=row, column=7, value=0.00).number_format = CURRENCY_FMT
    ws.cell(row=row, column=7).font = NORMAL_FONT

    # Licensing Program
    row += 1
    ws.cell(row=row, column=4, value="Licensing Program").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)
    ws.cell(row=row, column=5, value=footer.get("licensing_program", "Microsoft Customer Agreement (MCA)")).font = NORMAL_FONT

    # Billing Account
    row += 1
    ws.cell(row=row, column=4, value="Billing Account").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)
    ws.cell(row=row, column=5, value=footer.get("billing_account", "")).font = NORMAL_FONT

    # Billing Profile
    row += 1
    ws.cell(row=row, column=4, value="Billing Profile").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)
    ws.cell(row=row, column=5, value=footer.get("billing_profile", "")).font = NORMAL_FONT

    # Total row
    row += 1
    ws.cell(row=row, column=4, value="Total").font = Font(name="Segoe UI", size=11, bold=True, color=BLACK_HEX)
    total_monthly = data.get("summary", {}).get("total_monthly", 0)
    if not total_monthly:
        total_monthly = sum(s.get("estimated_monthly_cost", s.get("monthly_cost", 0)) for s in services)
    total_monthly += support_cost

    total_upfront = data.get("summary", {}).get("upfront_cost", 0)
    if not total_upfront:
        total_upfront = sum(s.get("estimated_upfront_cost", s.get("upfront_cost", 0)) for s in services)

    ws.cell(row=row, column=6, value=total_monthly).number_format = CURRENCY_FMT
    ws.cell(row=row, column=6).font = Font(name="Segoe UI", size=10, bold=True, color=BLACK_HEX)
    ws.cell(row=row, column=7, value=total_upfront).number_format = CURRENCY_FMT
    ws.cell(row=row, column=7).font = Font(name="Segoe UI", size=10, bold=True, color=BLACK_HEX)

    # Disclaimer
    row += 2
    ws.cell(row=row, column=1, value="Disclaimer").font = Font(name="Segoe UI", size=9, bold=True, color=BLACK_HEX)

    row += 1
    disclaimer_text = "All prices shown are in United States – Dollar ($) USD. This is a summary estimate, not a quote. For up to date pricing information please visit https://azure.microsoft.com/pricing/calculator/"
    ws.cell(row=row, column=1, value=disclaimer_text).font = Font(name="Segoe UI", size=8, color=GRAY_HEX)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)

    row += 1
    timestamp = datetime.now(timezone.utc).strftime("%m/%d/%Y %I:%M:%S %p UTC")
    ws.cell(row=row, column=1, value=f"This estimate was created at {timestamp}").font = Font(name="Segoe UI", size=8, color=GRAY_HEX)

    # Column widths
    column_widths = {"A": 18, "B": 22, "C": 15, "D": 15, "E": 55, "F": 22, "G": 22}
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 18
    ws.row_dimensions[3].height = 25
    ws.freeze_panes = "A4"

    return ws
