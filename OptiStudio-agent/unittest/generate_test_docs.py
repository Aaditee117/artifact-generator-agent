"""
Test Documentation Generator

This script generates an Excel file documenting all unit and functional tests
for the OptiStudio Agent project.

Run: python generate_test_docs.py
Output: test_documentation.xlsx
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

# Styles
HEADER_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
ALT_ROW_FILL = PatternFill(start_color="D6DCE4", end_color="D6DCE4", fill_type="solid")
TITLE_FONT = Font(name="Calibri", size=14, bold=True)
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)

# Test data organized by category
UNIT_TESTS = [
    # Blob Storage Tests
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestSlugify",
        "test_name": "test_slugify_simple_text",
        "description": "Test slugify with simple text converts to lowercase hyphenated slug",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestSlugify",
        "test_name": "test_slugify_with_special_characters",
        "description": "Test slugify removes special characters from text",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestSlugify",
        "test_name": "test_slugify_with_multiple_spaces",
        "description": "Test slugify handles multiple spaces correctly",
        "test_type": "Unit",
        "priority": "Medium",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestSlugify",
        "test_name": "test_slugify_empty_string",
        "description": "Test slugify with empty string returns 'untitled'",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestSlugify",
        "test_name": "test_slugify_truncates_long_text",
        "description": "Test slugify truncates text longer than 80 characters",
        "test_type": "Unit",
        "priority": "Medium",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestBuildSessionFolder",
        "test_name": "test_build_session_folder_normal",
        "description": "Test build_session_folder creates correct folder name",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestBuildSessionFolder",
        "test_name": "test_build_session_folder_empty_title",
        "description": "Test build_session_folder handles empty title",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestUploadBytes",
        "test_name": "test_upload_bytes_with_session_folder",
        "description": "Test upload_bytes with session folder creates correct path",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestUploadBytes",
        "test_name": "test_upload_bytes_without_session_folder",
        "description": "Test upload_bytes without session folder uses UUID path",
        "test_type": "Unit",
        "priority": "Medium",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestDownloadBlob",
        "test_name": "test_download_blob_success",
        "description": "Test download_blob successfully downloads content",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestDownloadBlob",
        "test_name": "test_download_blob_with_encoded_path",
        "description": "Test download_blob handles URL-encoded paths",
        "test_type": "Unit",
        "priority": "Medium",
        "status": "Implemented"
    },
    {
        "module": "utils/blob_storage.py",
        "test_file": "tests/unit/test_blob_storage.py",
        "test_class": "TestDownloadBlob",
        "test_name": "test_download_blob_not_found_raises_exception",
        "description": "Test download_blob raises exception when blob not found",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    
    # Document Reader Tests
    {
        "module": "utils/document_reader.py",
        "test_file": "tests/unit/test_document_reader.py",
        "test_class": "TestExtractTextTxt",
        "test_name": "test_extract_text_txt_simple",
        "description": "Test extracting text from simple TXT file",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/document_reader.py",
        "test_file": "tests/unit/test_document_reader.py",
        "test_class": "TestExtractTextTxt",
        "test_name": "test_extract_text_txt_with_newlines",
        "description": "Test extracting text from TXT file with newlines",
        "test_type": "Unit",
        "priority": "Medium",
        "status": "Implemented"
    },
    {
        "module": "utils/document_reader.py",
        "test_file": "tests/unit/test_document_reader.py",
        "test_class": "TestExtractTextTxt",
        "test_name": "test_extract_text_txt_unicode",
        "description": "Test extracting text from TXT file with unicode",
        "test_type": "Unit",
        "priority": "Medium",
        "status": "Implemented"
    },
    {
        "module": "utils/document_reader.py",
        "test_file": "tests/unit/test_document_reader.py",
        "test_class": "TestExtractTextDocx",
        "test_name": "test_extract_text_docx_simple",
        "description": "Test extracting text from simple DOCX file",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/document_reader.py",
        "test_file": "tests/unit/test_document_reader.py",
        "test_class": "TestExtractTextPdf",
        "test_name": "test_extract_text_pdf_single_page",
        "description": "Test extracting text from single-page PDF",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/document_reader.py",
        "test_file": "tests/unit/test_document_reader.py",
        "test_class": "TestExtractTextPdf",
        "test_name": "test_extract_text_pdf_multiple_pages",
        "description": "Test extracting text from multi-page PDF",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/document_reader.py",
        "test_file": "tests/unit/test_document_reader.py",
        "test_class": "TestExtractTextPptx",
        "test_name": "test_extract_text_pptx_simple",
        "description": "Test extracting text from simple PPTX file",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "utils/document_reader.py",
        "test_file": "tests/unit/test_document_reader.py",
        "test_class": "TestExtractTextUnsupported",
        "test_name": "test_extract_text_unsupported_extension",
        "description": "Test extracting text from unsupported file type",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    
    # Agent Dispatcher Tests
    {
        "module": "tools/agent_dispatcher.py",
        "test_file": "tests/unit/test_agent_dispatcher.py",
        "test_class": "TestDispatchToolCallGetDatabaseSchema",
        "test_name": "test_dispatch_get_database_schema_success",
        "description": "Test dispatching get_database_schema tool successfully",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/agent_dispatcher.py",
        "test_file": "tests/unit/test_agent_dispatcher.py",
        "test_class": "TestDispatchToolCallExecuteAdminSql",
        "test_name": "test_dispatch_execute_admin_sql_success",
        "description": "Test dispatching execute_admin_sql tool successfully",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/agent_dispatcher.py",
        "test_file": "tests/unit/test_agent_dispatcher.py",
        "test_class": "TestDispatchToolCallExecuteAdminSql",
        "test_name": "test_dispatch_execute_admin_sql_error",
        "description": "Test dispatching execute_admin_sql with SQL error",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/agent_dispatcher.py",
        "test_file": "tests/unit/test_agent_dispatcher.py",
        "test_class": "TestDispatchToolCallQueryUnstructuredData",
        "test_name": "test_dispatch_query_unstructured_data_success",
        "description": "Test dispatching query_unstructured_data successfully",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/agent_dispatcher.py",
        "test_file": "tests/unit/test_agent_dispatcher.py",
        "test_class": "TestDispatchToolCallUnknownTool",
        "test_name": "test_dispatch_unknown_tool",
        "description": "Test dispatching unknown tool returns error",
        "test_type": "Unit",
        "priority": "Medium",
        "status": "Implemented"
    },
    
    # Cost Report Tool Tests
    {
        "module": "tools/cost_report_tool.py",
        "test_file": "tests/unit/test_cost_report_tool.py",
        "test_class": "TestParsePhaseSelection",
        "test_name": "test_parse_phase_selection_poc_lowercase",
        "description": "Test parsing 'poc' input returns poc",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/cost_report_tool.py",
        "test_file": "tests/unit/test_cost_report_tool.py",
        "test_class": "TestParsePhaseSelection",
        "test_name": "test_parse_phase_selection_mvp_lowercase",
        "description": "Test parsing 'mvp' input returns mvp",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/cost_report_tool.py",
        "test_file": "tests/unit/test_cost_report_tool.py",
        "test_class": "TestParsePhaseSelection",
        "test_name": "test_parse_phase_selection_both",
        "description": "Test parsing 'both' input returns both",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/cost_report_tool.py",
        "test_file": "tests/unit/test_cost_report_tool.py",
        "test_class": "TestGenerateCostReport",
        "test_name": "test_generate_cost_report_poc_success",
        "description": "Test generating POC cost report successfully",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/cost_report_tool.py",
        "test_file": "tests/unit/test_cost_report_tool.py",
        "test_class": "TestGenerateCostReport",
        "test_name": "test_generate_cost_report_mvp_success",
        "description": "Test generating MVP cost report successfully",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    
    # Architecture Tool Tests
    {
        "module": "tools/architecture_tool.py",
        "test_file": "tests/unit/test_architecture_tool.py",
        "test_class": "TestGenerateArchitectureDiagram",
        "test_name": "test_generate_architecture_diagram_poc",
        "description": "Test generating POC architecture diagram",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/architecture_tool.py",
        "test_file": "tests/unit/test_architecture_tool.py",
        "test_class": "TestGenerateArchitectureDiagram",
        "test_name": "test_generate_architecture_diagram_mvp",
        "description": "Test generating MVP architecture diagram",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/architecture_tool.py",
        "test_file": "tests/unit/test_architecture_tool.py",
        "test_class": "TestNormalizeGraph",
        "test_name": "test_normalize_graph_with_valid_input",
        "description": "Test normalizing valid graph structure",
        "test_type": "Unit",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "tools/architecture_tool.py",
        "test_file": "tests/unit/test_architecture_tool.py",
        "test_class": "TestNormalizeGraph",
        "test_name": "test_normalize_graph_with_empty_input",
        "description": "Test normalizing empty graph returns empty lists",
        "test_type": "Unit",
        "priority": "Medium",
        "status": "Implemented"
    },
]

FUNCTIONAL_TESTS = [
    # API Endpoint Tests
    {
        "module": "main.py",
        "test_file": "tests/functional/test_api_endpoints.py",
        "test_class": "TestClarifyEndpoint",
        "test_name": "test_clarify_architecture_returns_questions",
        "description": "Test /clarify endpoint returns clarification questions for architecture",
        "test_type": "Functional",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "main.py",
        "test_file": "tests/functional/test_api_endpoints.py",
        "test_class": "TestClarifyEndpoint",
        "test_name": "test_clarify_cost_report_returns_questions",
        "description": "Test /clarify endpoint returns questions for cost report",
        "test_type": "Functional",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "main.py",
        "test_file": "tests/functional/test_api_endpoints.py",
        "test_class": "TestGenerateEndpoint",
        "test_name": "test_generate_architecture_returns_graph",
        "description": "Test /generate endpoint returns architecture graph",
        "test_type": "Functional",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "main.py",
        "test_file": "tests/functional/test_api_endpoints.py",
        "test_class": "TestGenerateEndpoint",
        "test_name": "test_generate_ppt_returns_download_url",
        "description": "Test /generate endpoint returns PPT download URL",
        "test_type": "Functional",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "main.py",
        "test_file": "tests/functional/test_api_endpoints.py",
        "test_class": "TestGenerateEndpoint",
        "test_name": "test_generate_cost_report_returns_excel",
        "description": "Test /generate endpoint returns cost report Excel",
        "test_type": "Functional",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "main.py",
        "test_file": "tests/functional/test_api_endpoints.py",
        "test_class": "TestFeedbackEndpoint",
        "test_name": "test_feedback_approve_copies_to_approved",
        "description": "Test /feedback approve action copies artifact to approved container",
        "test_type": "Functional",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "main.py",
        "test_file": "tests/functional/test_api_endpoints.py",
        "test_class": "TestFullWorkflowScenarios",
        "test_name": "test_full_architecture_workflow",
        "description": "Test complete architecture diagram generation workflow",
        "test_type": "Functional",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "main.py",
        "test_file": "tests/functional/test_api_endpoints.py",
        "test_class": "TestFullWorkflowScenarios",
        "test_name": "test_full_cost_report_workflow",
        "description": "Test complete cost report generation workflow",
        "test_type": "Functional",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "main.py",
        "test_file": "tests/functional/test_api_endpoints.py",
        "test_class": "TestErrorHandling",
        "test_name": "test_clarify_with_blob_not_found",
        "description": "Test /clarify handles blob not found gracefully",
        "test_type": "Functional",
        "priority": "High",
        "status": "Implemented"
    },
    
    # Integration Tests
    {
        "module": "Integration",
        "test_file": "tests/functional/test_integration.py",
        "test_class": "TestDocumentProcessingPipeline",
        "test_name": "test_blob_to_text_extraction_pipeline",
        "description": "Test complete pipeline from blob download to text extraction",
        "test_type": "Integration",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "Integration",
        "test_file": "tests/functional/test_integration.py",
        "test_class": "TestDocumentProcessingPipeline",
        "test_name": "test_multiple_document_aggregation",
        "description": "Test processing and aggregating multiple documents",
        "test_type": "Integration",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "Integration",
        "test_file": "tests/functional/test_integration.py",
        "test_class": "TestCostReportGenerationPipeline",
        "test_name": "test_cost_report_excel_generation",
        "description": "Test cost data to Excel generation pipeline",
        "test_type": "Integration",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "Integration",
        "test_file": "tests/functional/test_integration.py",
        "test_class": "TestCostReportGenerationPipeline",
        "test_name": "test_cost_report_poc_mvp_comparison",
        "description": "Test POC vs MVP cost comparison report generation",
        "test_type": "Integration",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "Integration",
        "test_file": "tests/functional/test_integration.py",
        "test_class": "TestArchitectureGenerationPipeline",
        "test_name": "test_context_to_architecture_graph",
        "description": "Test context processing to architecture graph generation",
        "test_type": "Integration",
        "priority": "Critical",
        "status": "Implemented"
    },
    {
        "module": "Integration",
        "test_file": "tests/functional/test_integration.py",
        "test_class": "TestSessionWorkflowIntegration",
        "test_name": "test_session_folder_creation_and_artifact_upload",
        "description": "Test session folder creation and artifact upload",
        "test_type": "Integration",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "Integration",
        "test_file": "tests/functional/test_integration.py",
        "test_class": "TestPhaseBasedGeneration",
        "test_name": "test_poc_generates_minimal_architecture",
        "description": "Test POC phase generates minimal architecture",
        "test_type": "Integration",
        "priority": "High",
        "status": "Implemented"
    },
    {
        "module": "Integration",
        "test_file": "tests/functional/test_integration.py",
        "test_class": "TestPhaseBasedGeneration",
        "test_name": "test_mvp_generates_production_architecture",
        "description": "Test MVP phase generates production-ready architecture",
        "test_type": "Integration",
        "priority": "High",
        "status": "Implemented"
    },
]


def create_summary_sheet(wb):
    """Create summary sheet with test counts."""
    ws = wb.active
    ws.title = "Summary"
    
    # Title
    ws["A1"] = "OptiStudio Agent Test Documentation"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:E1")
    
    ws["A2"] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ws["A2"].font = Font(italic=True)
    
    # Summary table
    ws["A4"] = "Test Summary"
    ws["A4"].font = Font(bold=True, size=12)
    
    headers = ["Category", "Total Tests", "Critical", "High", "Medium"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
    
    # Calculate counts
    unit_critical = len([t for t in UNIT_TESTS if t["priority"] == "Critical"])
    unit_high = len([t for t in UNIT_TESTS if t["priority"] == "High"])
    unit_medium = len([t for t in UNIT_TESTS if t["priority"] == "Medium"])
    
    func_critical = len([t for t in FUNCTIONAL_TESTS if t["priority"] == "Critical"])
    func_high = len([t for t in FUNCTIONAL_TESTS if t["priority"] == "High"])
    func_medium = len([t for t in FUNCTIONAL_TESTS if t["priority"] == "Medium"])
    
    data = [
        ["Unit Tests", len(UNIT_TESTS), unit_critical, unit_high, unit_medium],
        ["Functional Tests", len(FUNCTIONAL_TESTS), func_critical, func_high, func_medium],
        ["Total", len(UNIT_TESTS) + len(FUNCTIONAL_TESTS), 
         unit_critical + func_critical, unit_high + func_high, unit_medium + func_medium]
    ]
    
    for row_idx, row_data in enumerate(data, 6):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = THIN_BORDER
            if row_idx == 8:  # Total row
                cell.font = Font(bold=True)
    
    # Adjust column widths
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 12


def create_tests_sheet(wb, sheet_name, tests):
    """Create a sheet with test details."""
    ws = wb.create_sheet(title=sheet_name)
    
    headers = ["Module", "Test File", "Test Class", "Test Name", "Description", "Type", "Priority", "Status"]
    col_widths = [25, 35, 35, 45, 60, 12, 10, 12]
    
    # Headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Data rows
    for row_idx, test in enumerate(tests, 2):
        row_data = [
            test["module"],
            test["test_file"],
            test["test_class"],
            test["test_name"],
            test["description"],
            test["test_type"],
            test["priority"],
            test["status"]
        ]
        
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            
            # Alternating row colors
            if row_idx % 2 == 0:
                cell.fill = ALT_ROW_FILL
    
    # Set column widths
    for col, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width


def create_aaa_pattern_sheet(wb):
    """Create a sheet explaining the AAA pattern."""
    ws = wb.create_sheet(title="AAA Pattern Guide")
    
    ws["A1"] = "AAA (Arrange-Act-Assert) Test Pattern"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:D1")
    
    content = [
        ("", ""),
        ("What is AAA?", ""),
        ("", "AAA is a pattern for structuring unit tests that makes them clear, readable, and maintainable."),
        ("", ""),
        ("ARRANGE", "Set up the test conditions and inputs"),
        ("", "- Create mock objects"),
        ("", "- Initialize test data"),
        ("", "- Configure dependencies"),
        ("", ""),
        ("ACT", "Execute the code being tested"),
        ("", "- Call the method/function under test"),
        ("", "- Capture the result"),
        ("", ""),
        ("ASSERT", "Verify the expected outcome"),
        ("", "- Check return values"),
        ("", "- Verify mock interactions"),
        ("", "- Validate state changes"),
        ("", ""),
        ("Example:", ""),
        ("", "def test_slugify_simple_text():"),
        ("", "    # Arrange"),
        ("", "    input_text = 'My Project Name'"),
        ("", ""),
        ("", "    # Act"),
        ("", "    result = slugify(input_text)"),
        ("", ""),
        ("", "    # Assert"),
        ("", "    assert result == 'my-project-name'"),
    ]
    
    for row_idx, (col_a, col_b) in enumerate(content, 2):
        ws.cell(row=row_idx, column=1, value=col_a).font = Font(bold=True) if col_a else Font()
        ws.cell(row=row_idx, column=2, value=col_b)
    
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 60


def generate_test_documentation():
    """Generate the test documentation Excel file."""
    wb = Workbook()
    
    # Create sheets
    create_summary_sheet(wb)
    create_tests_sheet(wb, "Unit Tests", UNIT_TESTS)
    create_tests_sheet(wb, "Functional Tests", FUNCTIONAL_TESTS)
    create_aaa_pattern_sheet(wb)
    
    # Save
    output_path = "test_documentation.xlsx"
    wb.save(output_path)
    print(f"✅ Test documentation generated: {output_path}")
    print(f"   - {len(UNIT_TESTS)} unit tests documented")
    print(f"   - {len(FUNCTIONAL_TESTS)} functional tests documented")
    return output_path


if __name__ == "__main__":
    generate_test_documentation()
