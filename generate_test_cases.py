"""Generate Functional Test Cases Excel for OptiStudio."""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = openpyxl.Workbook()

# Styles
header_font = Font(bold=True, color="FFFFFF", size=11)
header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
module_fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
wrap_align = Alignment(wrap_text=True, vertical="top")
center_align = Alignment(horizontal="center", vertical="top", wrap_text=True)
thin_border = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)

HEADERS = ["Test ID", "Module", "Sub-Module", "Test Case Title", "Preconditions",
           "Test Steps", "Expected Result", "Priority", "Status"]

COL_WIDTHS = [12, 18, 22, 40, 35, 55, 45, 12, 12]

# Priority colors
priority_colors = {
    "High": PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid"),
    "Medium": PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid"),
    "Low": PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid"),
}


def write_sheet(ws, test_cases):
    """Write test cases to a worksheet."""
    # Header row
    for col_idx, header in enumerate(HEADERS, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border

    # Set column widths
    for col_idx, width in enumerate(COL_WIDTHS, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = width

    # Data rows
    for row_idx, tc in enumerate(test_cases, 2):
        for col_idx, value in enumerate(tc, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = wrap_align
            cell.border = thin_border
        # Priority coloring
        priority = tc[7] if len(tc) > 7 else ""
        if priority in priority_colors:
            ws.cell(row=row_idx, column=8).fill = priority_colors[priority]

    # Freeze header
    ws.freeze_panes = "A2"
    # Auto-filter
    ws.auto_filter.ref = f"A1:{openpyxl.utils.get_column_letter(len(HEADERS))}1"


# ============================================================
# 1. AUTHENTICATION MODULE
# ============================================================
auth_tests = [
    # Positive
    ["AUTH-001", "Authentication", "Login", "Successful login via Azure AD (MSAL)",
     "User has valid Azure AD credentials; App registered in Azure AD",
     "1. Navigate to /login\n2. Click 'Sign In with Microsoft'\n3. Enter valid Azure AD credentials\n4. Complete MFA if prompted\n5. Consent to permissions",
     "User is redirected to /dashboard with valid JWT token stored in HttpOnly cookie; User info displayed correctly",
     "High", "Not Executed"],

    ["AUTH-002", "Authentication", "Login", "Auto-create user on first Azure AD login",
     "User exists in Azure AD but not in OptiStudio DB",
     "1. Login via Azure AD for the first time\n2. System processes ID token",
     "New User record created in DB with email from token; Default role assigned; User lands on dashboard",
     "High", "Not Executed"],

    ["AUTH-003", "Authentication", "Registration", "Successful user registration",
     "User has valid email not already registered",
     "1. Navigate to /register\n2. Enter valid email, name, and details\n3. Submit registration form",
     "Registration successful; OTP sent to email; User redirected to /verify-otp",
     "High", "Not Executed"],

    ["AUTH-004", "Authentication", "OTP Verification", "Verify OTP successfully",
     "User has registered and received OTP email",
     "1. Navigate to /verify-otp\n2. Enter correct OTP code\n3. Submit",
     "OTP verified successfully; User account activated; Redirect to /login or /dashboard",
     "High", "Not Executed"],

    ["AUTH-005", "Authentication", "Token Refresh", "Refresh expired access token",
     "User is logged in; Access token is about to expire; Valid refresh token exists",
     "1. Access token expires\n2. Frontend auto-calls POST /api/auth/refresh-token\n3. Send valid refresh token",
     "New access token issued; Session continues without interruption; New HttpOnly cookie set",
     "High", "Not Executed"],

    ["AUTH-006", "Authentication", "Logout", "Successful logout",
     "User is authenticated",
     "1. Click Logout button\n2. POST /api/auth/logout",
     "JWT cookie cleared; Refresh token invalidated in DB; User redirected to /login",
     "High", "Not Executed"],

    # Negative
    ["AUTH-007", "Authentication", "Login", "Login with invalid Azure AD credentials",
     "User has invalid or non-existent Azure AD credentials",
     "1. Navigate to /login\n2. Click 'Sign In with Microsoft'\n3. Enter invalid credentials",
     "Azure AD returns error; User shown appropriate error message; No token issued",
     "High", "Not Executed"],

    ["AUTH-008", "Authentication", "Registration", "Register with already registered email",
     "Email already exists in the system",
     "1. Navigate to /register\n2. Enter email that is already registered\n3. Submit",
     "Error message: 'Email already registered'; Form not submitted",
     "Medium", "Not Executed"],

    ["AUTH-009", "Authentication", "OTP Verification", "Verify with incorrect OTP",
     "User has registered and received OTP",
     "1. Navigate to /verify-otp\n2. Enter incorrect OTP\n3. Submit",
     "Error: 'Invalid OTP'; Account remains unverified",
     "High", "Not Executed"],

    ["AUTH-010", "Authentication", "OTP Verification", "Verify with expired OTP",
     "User registered but OTP has expired (beyond expiry time)",
     "1. Wait for OTP to expire\n2. Enter the expired OTP\n3. Submit",
     "Error: 'OTP expired'; User prompted to request new OTP",
     "Medium", "Not Executed"],

    ["AUTH-011", "Authentication", "Token Refresh", "Refresh with invalid/expired refresh token",
     "User's refresh token is expired or tampered",
     "1. POST /api/auth/refresh-token with invalid token",
     "401 Unauthorized; User forced to re-login",
     "High", "Not Executed"],

    ["AUTH-012", "Authentication", "Login", "Access protected page without authentication",
     "User is not logged in",
     "1. Directly navigate to /dashboard or /chat without logging in",
     "User redirected to /login; Protected content not accessible",
     "High", "Not Executed"],

    # Edge
    ["AUTH-013", "Authentication", "Login", "Concurrent login from multiple devices",
     "User has valid credentials",
     "1. Login from Device A\n2. Login from Device B with same credentials",
     "Both sessions should be valid (or policy-based: older session invalidated); No data corruption",
     "Medium", "Not Executed"],

    ["AUTH-014", "Authentication", "OTP Verification", "Multiple OTP requests in quick succession",
     "User registered and requests OTP multiple times",
     "1. Request OTP\n2. Immediately request OTP again 3 times",
     "Rate limiting applied; Only latest OTP is valid; Previous OTPs invalidated",
     "Low", "Not Executed"],

    ["AUTH-015", "Authentication", "Registration", "Register with special characters in name",
     "Valid email; Name contains special chars (e.g., O'Brien, José)",
     "1. Navigate to /register\n2. Enter name with special characters\n3. Submit",
     "Registration succeeds; Name stored and displayed correctly with special characters",
     "Low", "Not Executed"],
]

# ============================================================
# 2. RBAC MODULE
# ============================================================
rbac_tests = [
    # Admin role
    ["RBAC-001", "RBAC", "Admin Access", "Admin can access admin user management",
     "User logged in with Admin role",
     "1. Login as Admin\n2. Navigate to /admin/users",
     "Admin Users page loads; List of all users displayed with role management options",
     "High", "Not Executed"],

    ["RBAC-002", "RBAC", "Admin Access", "Admin can update user roles",
     "User logged in as Admin; Target user exists",
     "1. Navigate to /admin/users\n2. Select a user\n3. Change role from Developer to Architect\n4. Submit",
     "Role updated successfully; Change reflected in user list; Target user's permissions updated",
     "High", "Not Executed"],

    ["RBAC-003", "RBAC", "Admin Access", "Admin can access dashboard stats",
     "User logged in as Admin",
     "1. GET /api/dashboard/stats",
     "Dashboard statistics returned: user count, pending approvals, token usage",
     "High", "Not Executed"],

    ["RBAC-004", "RBAC", "Admin Access", "Admin can access chat features",
     "User logged in as Admin",
     "1. Navigate to /chat\n2. Create session\n3. Upload artifacts\n4. Generate deliverables",
     "All chat features accessible; Generation works correctly",
     "High", "Not Executed"],

    ["RBAC-005", "RBAC", "Admin Access", "Admin can approve/reject presales decks",
     "User logged in as Admin; Pending presales deck exists",
     "1. Navigate to /admin/approve\n2. Review pending deck\n3. Approve or Reject",
     "Deck status updated to Approved/Rejected; Status change reflected in approved-decks page",
     "High", "Not Executed"],

    # Architect role
    ["RBAC-006", "RBAC", "Architect Access", "Architect can access chat features",
     "User logged in as Architect",
     "1. Navigate to /chat\n2. Create session\n3. Upload artifacts\n4. Generate deliverables",
     "Chat page loads; All generation features available",
     "High", "Not Executed"],

    ["RBAC-007", "RBAC", "Architect Access", "Architect cannot access admin panel",
     "User logged in as Architect",
     "1. Navigate to /admin/users",
     "Access denied; Redirect to dashboard or 403 error displayed",
     "High", "Not Executed"],

    ["RBAC-008", "RBAC", "Architect Access", "Architect cannot access dashboard stats API",
     "User logged in as Architect",
     "1. GET /api/dashboard/stats",
     "403 Forbidden response",
     "High", "Not Executed"],

    ["RBAC-009", "RBAC", "Architect Access", "Architect can view approved decks",
     "User logged in as Architect; Approved decks exist",
     "1. Navigate to /approved-decks",
     "Approved decks page loads; Approved presentations listed",
     "Medium", "Not Executed"],

    # Developer role
    ["RBAC-010", "RBAC", "Developer Access", "Developer cannot access chat features",
     "User logged in as Developer",
     "1. Navigate to /chat",
     "Access denied; Redirect to dashboard or 403 error; Chat features not available",
     "High", "Not Executed"],

    ["RBAC-011", "RBAC", "Developer Access", "Developer cannot access admin panel",
     "User logged in as Developer",
     "1. Navigate to /admin/users\n2. Try GET /api/admin/users",
     "Access denied; 403 Forbidden on API call",
     "High", "Not Executed"],

    ["RBAC-012", "RBAC", "Developer Access", "Developer can view approved decks",
     "User logged in as Developer; Approved decks exist",
     "1. Navigate to /approved-decks",
     "Page loads; Approved decks visible (read-only)",
     "Medium", "Not Executed"],

    ["RBAC-013", "RBAC", "Developer Access", "Developer can view dashboard",
     "User logged in as Developer",
     "1. Navigate to /dashboard",
     "Dashboard page loads with developer-appropriate view (no admin stats)",
     "Medium", "Not Executed"],

    # Edge/Negative
    ["RBAC-014", "RBAC", "Role Change", "User permissions update after role change",
     "Admin changes a Developer's role to Architect",
     "1. Admin updates Developer to Architect\n2. Developer refreshes page\n3. Developer navigates to /chat",
     "Chat page now accessible; Previous role restrictions lifted; New permissions effective",
     "High", "Not Executed"],

    ["RBAC-015", "RBAC", "Token Tampering", "Tampered JWT with elevated role",
     "User logged in as Developer; JWT modified to claim Admin role",
     "1. Intercept JWT\n2. Modify role claim to Admin\n3. Send request to /api/admin/users",
     "Server validates token signature; 401/403 returned; Tampered token rejected",
     "High", "Not Executed"],

    ["RBAC-016", "RBAC", "API Direct Access", "Bypass frontend role guards via direct API call",
     "User logged in as Developer; Knows chat API endpoint",
     "1. Directly call POST /api/chat/sessions with Developer token",
     "403 Forbidden; Backend enforces role check regardless of frontend",
     "High", "Not Executed"],
]

# ============================================================
# 3. CHAT MODULE
# ============================================================
chat_tests = [
    # Sessions - Positive
    ["CHAT-001", "Chat", "Sessions", "Create a new chat session",
     "User logged in as Architect or Admin",
     "1. Navigate to /chat\n2. Click 'New Session'\n3. Enter session name\n4. Submit",
     "New session created; Session appears in sidebar; Session ID returned",
     "High", "Not Executed"],

    ["CHAT-002", "Chat", "Sessions", "Retrieve all user chat sessions",
     "User has existing chat sessions",
     "1. Navigate to /chat\n2. GET /api/chat/sessions",
     "All user's sessions listed in sidebar; Sessions ordered by recent activity",
     "High", "Not Executed"],

    ["CHAT-003", "Chat", "Sessions", "Rename a chat session",
     "User has an existing session",
     "1. Right-click/edit session name\n2. Enter new name\n3. Confirm",
     "Session name updated; New name displayed in sidebar",
     "Medium", "Not Executed"],

    ["CHAT-004", "Chat", "Sessions", "Delete a chat session",
     "User has an existing session with messages",
     "1. Select session\n2. Click delete\n3. Confirm deletion",
     "Session and all its messages deleted; Session removed from sidebar",
     "High", "Not Executed"],

    # Groups - Positive
    ["CHAT-005", "Chat", "Groups", "Create a new chat group",
     "User logged in as Architect or Admin",
     "1. Click 'New Group'\n2. Enter group name\n3. Submit",
     "Group created; Displayed in sidebar as collapsible folder",
     "Medium", "Not Executed"],

    ["CHAT-006", "Chat", "Groups", "Rename a chat group",
     "User has an existing group",
     "1. Right-click group\n2. Select rename\n3. Enter new name\n4. Confirm",
     "Group name updated successfully",
     "Low", "Not Executed"],

    ["CHAT-007", "Chat", "Groups", "Delete a chat group",
     "User has an existing group (with or without sessions)",
     "1. Right-click group\n2. Select delete\n3. Confirm",
     "Group deleted; Sessions within group handled (moved to ungrouped or deleted)",
     "Medium", "Not Executed"],

    ["CHAT-008", "Chat", "Groups", "Move session to a group",
     "User has a session and a group",
     "1. Select session\n2. Move to group via PUT /api/chat/sessions/{id}/move\n3. Specify target group",
     "Session appears under target group in sidebar",
     "Medium", "Not Executed"],

    # Messages - Positive
    ["CHAT-009", "Chat", "Messages", "Send a text message in session",
     "User has an active chat session",
     "1. Select session\n2. Type message in input\n3. Send",
     "Message sent; User message appears in chat; Agent responds with relevant answer",
     "High", "Not Executed"],

    ["CHAT-010", "Chat", "Messages", "Retrieve chat history for a session",
     "Session has existing messages",
     "1. Click on existing session\n2. GET /api/chat/messages/{sessionId}",
     "All previous messages loaded in correct order; Both user and agent messages displayed",
     "High", "Not Executed"],

    ["CHAT-011", "Chat", "Messages", "Send message with artifact attachment",
     "User has an active session; File ready for upload",
     "1. Click attachment icon\n2. Select file (PDF/DOCX/PPTX/IMG)\n3. Type message\n4. Send",
     "File uploaded; Message sent with artifact reference; Artifact stored in blob storage",
     "High", "Not Executed"],

    # Negative
    ["CHAT-012", "Chat", "Sessions", "Create session with empty name",
     "User logged in as Architect",
     "1. Click 'New Session'\n2. Leave name empty\n3. Submit",
     "Validation error; Session not created; Error message displayed",
     "Medium", "Not Executed"],

    ["CHAT-013", "Chat", "Sessions", "Delete non-existent session",
     "Session ID does not exist in DB",
     "1. DELETE /api/chat/sessions/{nonExistentId}",
     "404 Not Found response",
     "Low", "Not Executed"],

    ["CHAT-014", "Chat", "Sessions", "Access another user's session",
     "User A has a session; User B logged in",
     "1. User B attempts GET /api/chat/messages/{userA_sessionId}",
     "403 Forbidden or 404; User cannot access other's sessions",
     "High", "Not Executed"],

    ["CHAT-015", "Chat", "Messages", "Send empty message",
     "User has active session",
     "1. Leave message input empty\n2. Click send",
     "Send button disabled or validation error; Empty message not sent",
     "Medium", "Not Executed"],

    # Edge
    ["CHAT-016", "Chat", "Messages", "Send very long message (>5000 chars)",
     "User has active session",
     "1. Type message exceeding 5000 characters\n2. Send",
     "Message handled gracefully; Either accepted with truncation notice or rejected with size limit error",
     "Low", "Not Executed"],

    ["CHAT-017", "Chat", "Sessions", "Create maximum number of sessions",
     "User logged in; At or near session limit (if any)",
     "1. Continuously create new sessions",
     "System handles gracefully; Either allows unlimited or shows limit message",
     "Low", "Not Executed"],
]

# ============================================================
# 4. ARTIFACT MANAGEMENT
# ============================================================
artifact_tests = [
    ["ART-001", "Artifacts", "Upload", "Upload PDF artifact successfully",
     "User in active chat session; Valid PDF file (<10MB)",
     "1. Click upload in chat\n2. Select PDF file\n3. Upload",
     "PDF uploaded to Azure Blob Storage; Artifact record created with URL; File accessible",
     "High", "Not Executed"],

    ["ART-002", "Artifacts", "Upload", "Upload DOCX artifact successfully",
     "User in active chat session; Valid DOCX file",
     "1. Click upload\n2. Select DOCX file\n3. Upload",
     "DOCX uploaded; Text extracted and stored in Cosmos DB for RAG",
     "High", "Not Executed"],

    ["ART-003", "Artifacts", "Upload", "Upload PPTX artifact successfully",
     "User in active chat session; Valid PPTX file",
     "1. Click upload\n2. Select PPTX file\n3. Upload",
     "PPTX uploaded; Text extracted from slides; Stored for analysis",
     "High", "Not Executed"],

    ["ART-004", "Artifacts", "Upload", "Upload image artifact (JPG/PNG)",
     "User in active chat session; Valid image file",
     "1. Click upload\n2. Select image file\n3. Upload",
     "Image uploaded to blob storage; Artifact record created",
     "Medium", "Not Executed"],

    ["ART-005", "Artifacts", "Processing", "Process uploaded artifacts - text extraction",
     "Artifacts uploaded in session",
     "1. POST /api/agent/process-artifacts with artifact IDs\n2. Agent extracts text from PDFs/DOCX/PPTX",
     "Text extracted from all artifacts; Stored in Cosmos DB; Confirmation returned",
     "High", "Not Executed"],

    ["ART-006", "Artifacts", "Upload", "Upload unsupported file type (e.g., .exe, .zip)",
     "User in active chat session",
     "1. Attempt to upload .exe file",
     "Upload rejected; Error: 'Unsupported file type'; Only PDF/DOCX/PPTX/IMG allowed",
     "High", "Not Executed"],

    ["ART-007", "Artifacts", "Upload", "Upload file exceeding size limit",
     "User in active chat session; File > max allowed size",
     "1. Select oversized file\n2. Attempt upload",
     "Upload rejected; Error: 'File too large'; Size limit displayed",
     "Medium", "Not Executed"],

    ["ART-008", "Artifacts", "Upload", "Upload corrupted PDF file",
     "User has a corrupted/invalid PDF",
     "1. Upload corrupted PDF\n2. Process artifacts",
     "Upload succeeds; Text extraction fails gracefully; Error logged; User notified",
     "Medium", "Not Executed"],

    ["ART-009", "Artifacts", "Upload", "Upload multiple artifacts simultaneously",
     "User in active session; Multiple files ready",
     "1. Select multiple files (PDF + DOCX + IMG)\n2. Upload all",
     "All files uploaded; Each gets artifact record; All processed for text extraction",
     "Medium", "Not Executed"],

    ["ART-010", "Artifacts", "Upload", "Upload artifact with special characters in filename",
     "File name contains spaces, unicode, special chars",
     "1. Upload file named 'Résumé (Final) v2.0.pdf'",
     "File uploaded successfully; Filename sanitized for blob storage; Display name preserved",
     "Low", "Not Executed"],
]

# ============================================================
# 5. AGENT - CLARIFICATION
# ============================================================
clarification_tests = [
    ["CLR-001", "Agent", "Clarification", "Generate clarification questions from artifacts",
     "Artifacts uploaded and processed; Text extracted in Cosmos DB",
     "1. POST /api/agent/clarify\n2. Agent analyzes extracted text\n3. LLM generates relevant questions",
     "List of clarification questions returned; Questions relevant to uploaded documents; Displayed in chat",
     "High", "Not Executed"],

    ["CLR-002", "Agent", "Clarification", "Answer clarification questions",
     "Clarification questions displayed in chat",
     "1. Read questions\n2. Type answers\n3. Submit responses",
     "Answers recorded; Agent processes answers to refine understanding; Ready for generation",
     "High", "Not Executed"],

    ["CLR-003", "Agent", "Clarification", "Clarify with no artifacts uploaded",
     "No artifacts in current session",
     "1. POST /api/agent/clarify with empty session",
     "Error or generic questions; User prompted to upload artifacts first",
     "Medium", "Not Executed"],

    ["CLR-004", "Agent", "Clarification", "Clarify with minimal artifact content",
     "Single artifact with very little text (e.g., 1-sentence document)",
     "1. Upload minimal document\n2. Process\n3. Request clarification",
     "Agent generates questions; May request more information; Handles gracefully",
     "Medium", "Not Executed"],
]

# ============================================================
# 6. AGENT - ARCHITECTURE DIAGRAM
# ============================================================
arch_tests = [
    ["ARCH-001", "Agent", "Architecture Diagram", "Generate architecture diagram for POC phase",
     "Artifacts uploaded and processed; Clarification answered; POC phase selected",
     "1. POST /api/agent/generate with type=architecture, phase=POC\n2. Agent analyzes requirements\n3. GPT-4o generates React Flow graph",
     "Architecture diagram JSON returned; Contains nodes, edges, groups; Minimal POC components; Rendered in React Flow on frontend",
     "High", "Not Executed"],

    ["ARCH-002", "Agent", "Architecture Diagram", "Generate architecture diagram for MVP phase",
     "Artifacts and clarification complete; MVP phase selected",
     "1. POST /api/agent/generate with type=architecture, phase=MVP\n2. Agent generates production-ready architecture",
     "Full production architecture with monitoring, scaling, security; More components than POC; Valid React Flow JSON",
     "High", "Not Executed"],

    ["ARCH-003", "Agent", "Architecture Diagram", "Architecture diagram includes correct Azure services",
     "Project uses Azure services (as inferred from artifacts)",
     "1. Generate architecture diagram\n2. Review nodes",
     "Diagram includes relevant Azure services (App Service, SQL, Blob, etc.); Services match project requirements",
     "High", "Not Executed"],

    ["ARCH-004", "Agent", "Architecture Diagram", "Architecture diagram renders correctly in React Flow",
     "Architecture JSON generated",
     "1. Frontend receives React Flow JSON\n2. Renders diagram",
     "Diagram displayed without overlapping nodes; Edges connected correctly; Groups visible; Zoom/pan works",
     "High", "Not Executed"],

    ["ARCH-005", "Agent", "Architecture Diagram", "Provide feedback on architecture diagram",
     "Architecture diagram generated and displayed",
     "1. Click 'Need Changes'\n2. Type feedback: 'Add Redis cache layer'\n3. Submit",
     "Agent regenerates diagram with Redis cache added; Updated diagram displayed",
     "High", "Not Executed"],

    ["ARCH-006", "Agent", "Architecture Diagram", "Approve architecture diagram",
     "Architecture diagram generated",
     "1. Review diagram\n2. Click 'Good' / Approve",
     "Diagram marked as approved; Feedback recorded; Can proceed to next generation step",
     "Medium", "Not Executed"],

    # Negative/Edge
    ["ARCH-007", "Agent", "Architecture Diagram", "Generate architecture with contradictory requirements",
     "Artifacts contain conflicting requirements",
     "1. Upload docs with contradictory tech stack requirements\n2. Generate architecture",
     "Agent either asks for clarification or makes reasonable assumption; No crash; Result documented",
     "Medium", "Not Executed"],

    ["ARCH-008", "Agent", "Architecture Diagram", "Generate architecture with empty/insufficient data",
     "Minimal or no meaningful content in artifacts",
     "1. Upload near-empty document\n2. Request architecture generation",
     "Agent returns error or generic architecture; User prompted to provide more information",
     "Medium", "Not Executed"],
]

# ============================================================
# 7. AGENT - DFD
# ============================================================
dfd_tests = [
    ["DFD-001", "Agent", "DFD", "Generate Level 0 DFD",
     "Artifacts uploaded and processed; Clarification complete",
     "1. POST /api/agent/generate with type=dfd\n2. Agent generates Level 0 DFD",
     "Level 0 DFD returned in React Flow format; Shows main processes, data stores, external entities",
     "High", "Not Executed"],

    ["DFD-002", "Agent", "DFD", "Generate Level 1 DFD",
     "Level 0 DFD generated",
     "1. Agent generates Level 1 DFD with detailed subprocesses",
     "Level 1 DFD shows expanded process details; Data flows clearly labeled; Valid Mermaid syntax used",
     "High", "Not Executed"],

    ["DFD-003", "Agent", "DFD", "DFD renders correctly in frontend",
     "DFD JSON generated",
     "1. Frontend receives DFD React Flow data\n2. Renders diagram",
     "DFD displayed with correct node types (process, data store, entity); Arrows show data flow direction",
     "High", "Not Executed"],

    ["DFD-004", "Agent", "DFD", "Provide feedback on DFD",
     "DFD generated and displayed",
     "1. Click 'Need Changes'\n2. Enter feedback: 'Add payment gateway data flow'\n3. Submit",
     "DFD regenerated with payment gateway flow; Updated diagram displayed",
     "Medium", "Not Executed"],

    ["DFD-005", "Agent", "DFD", "DFD with DALL-E 3 visualization",
     "DFD generated in Mermaid syntax",
     "1. Agent converts Mermaid to DALL-E 3 visualization\n2. Image generated",
     "Visual DFD image created; Image embedded in PPT if generating presentation",
     "Medium", "Not Executed"],

    # Negative
    ["DFD-006", "Agent", "DFD", "Generate DFD with insufficient data",
     "Very minimal artifact content",
     "1. Request DFD generation",
     "Agent handles gracefully; Returns partial DFD or requests more info",
     "Medium", "Not Executed"],
]

# ============================================================
# 8. AGENT - POWERPOINT GENERATION
# ============================================================
ppt_tests = [
    ["PPT-001", "Agent", "PowerPoint", "Generate POC presales presentation",
     "Architecture + DFD generated; POC phase selected; All approvals done",
     "1. POST /api/agent/generate with type=ppt, phase=POC\n2. Agent creates PPTX",
     "PowerPoint file generated with: Executive Summary, Architecture slide, DFD slide, Timeline, Budget, Next Steps; Uploaded to Azure Blob Storage; Download URL returned",
     "High", "Not Executed"],

    ["PPT-002", "Agent", "PowerPoint", "Generate MVP presales presentation",
     "Architecture + DFD generated; MVP phase selected",
     "1. POST /api/agent/generate with type=ppt, phase=MVP",
     "MVP-specific PPT with production-ready architecture; More detailed timeline and budget; Blob URL returned",
     "High", "Not Executed"],

    ["PPT-003", "Agent", "PowerPoint", "PPT embeds architecture diagram image",
     "Architecture diagram generated",
     "1. Generate PPT\n2. Open downloaded PPTX",
     "Architecture diagram correctly embedded as image in relevant slide; Image clear and readable",
     "High", "Not Executed"],

    ["PPT-004", "Agent", "PowerPoint", "PPT embeds DFD diagram image",
     "DFD generated",
     "1. Generate PPT\n2. Open downloaded PPTX",
     "DFD image embedded in DFD slide; Correct labeling",
     "High", "Not Executed"],

    ["PPT-005", "Agent", "PowerPoint", "Download generated PPT from blob storage",
     "PPT generated and uploaded to blob storage",
     "1. Click download link in chat\n2. File downloads",
     "Valid .pptx file downloaded; Opens correctly in PowerPoint; All slides present",
     "High", "Not Executed"],

    ["PPT-006", "Agent", "PowerPoint", "PPT contains correct project-specific content",
     "Artifacts describe a specific project (e.g., e-commerce platform)",
     "1. Generate PPT\n2. Review slide content",
     "Content is project-specific (not generic); Executive summary matches project; Tech stack accurate",
     "High", "Not Executed"],

    ["PPT-007", "Agent", "PowerPoint", "Provide feedback on generated PPT",
     "PPT generated",
     "1. Review PPT\n2. Click 'Need Changes'\n3. Provide feedback\n4. Submit",
     "Agent regenerates PPT with changes; New version uploaded to blob; Updated URL returned",
     "Medium", "Not Executed"],

    # Negative/Edge
    ["PPT-008", "Agent", "PowerPoint", "Generate PPT without architecture diagram",
     "No architecture diagram generated yet",
     "1. Request PPT generation without prior diagram generation",
     "Either auto-generates architecture first or returns error prompting diagram generation",
     "Medium", "Not Executed"],

    ["PPT-009", "Agent", "PowerPoint", "Generate PPT with Azure Blob Storage unavailable",
     "Blob storage connection failing",
     "1. Generate PPT when blob storage is down",
     "Graceful error handling; User notified of storage issue; Retry option available",
     "Medium", "Not Executed"],
]

# ============================================================
# 9. AGENT - COST REPORT
# ============================================================
cost_tests = [
    ["COST-001", "Agent", "Cost Report", "Generate POC cost report",
     "Project requirements analyzed; POC phase",
     "1. POST /api/agent/generate with type=cost_report, phase=POC\n2. Agent generates Excel",
     "Excel file generated with Azure service pricing for POC (free/basic tiers); Uploaded to blob; Download URL returned",
     "High", "Not Executed"],

    ["COST-002", "Agent", "Cost Report", "Generate MVP cost report",
     "Project requirements analyzed; MVP phase",
     "1. POST /api/agent/generate with type=cost_report, phase=MVP",
     "Excel with production-ready Azure pricing; Standard/Premium tiers; Higher cost estimates",
     "High", "Not Executed"],

    ["COST-003", "Agent", "Cost Report", "Generate BOTH (POC + MVP) cost comparison",
     "Project requirements analyzed",
     "1. POST /api/agent/generate with type=cost_report, phase=BOTH",
     "Excel with side-by-side POC vs MVP comparison; Clear pricing differences; Both sheets present",
     "High", "Not Executed"],

    ["COST-004", "Agent", "Cost Report", "Cost report includes relevant Azure services",
     "Project uses specific Azure services",
     "1. Generate cost report\n2. Review services listed",
     "Only relevant services included (e.g., App Service, SQL DB, Blob Storage); No irrelevant services",
     "High", "Not Executed"],

    ["COST-005", "Agent", "Cost Report", "Download cost report from blob storage",
     "Cost report generated",
     "1. Click download link\n2. File downloads",
     "Valid .xlsx file; Opens in Excel; Data formatted correctly; Formulas work",
     "High", "Not Executed"],

    ["COST-006", "Agent", "Cost Report", "Cost report with minimal project info",
     "Very basic project description, few services",
     "1. Generate cost report",
     "Report generated with available info; May include common/assumed services; User can refine",
     "Medium", "Not Executed"],

    ["COST-007", "Agent", "Cost Report", "Provide feedback on cost report",
     "Cost report generated",
     "1. Review report\n2. Feedback: 'Add Kubernetes cluster pricing'\n3. Submit",
     "Report regenerated with AKS pricing included; Updated Excel uploaded",
     "Medium", "Not Executed"],
]

# ============================================================
# 10. AGENT - RAG (Chat with Documents)
# ============================================================
rag_tests = [
    ["RAG-001", "Agent", "RAG", "Ask question about uploaded documents",
     "Artifacts uploaded and text extracted to Cosmos DB",
     "1. Type question related to document content\n2. Send message",
     "Agent queries Cosmos DB; LLM synthesizes answer from documents; Relevant answer displayed",
     "High", "Not Executed"],

    ["RAG-002", "Agent", "RAG", "Ask question with no relevant documents",
     "No artifacts uploaded or documents not related to question",
     "1. Ask question unrelated to any uploaded content",
     "Agent indicates no relevant information found; Suggests uploading relevant documents",
     "Medium", "Not Executed"],

    ["RAG-003", "Agent", "RAG", "Ask question spanning multiple documents",
     "Multiple artifacts uploaded covering different aspects",
     "1. Ask question that requires info from multiple documents\n2. Send",
     "Agent synthesizes answer from multiple document sources; Comprehensive response",
     "High", "Not Executed"],

    ["RAG-004", "Agent", "RAG", "RAG response accuracy for specific facts",
     "Document contains specific numbers/dates/names",
     "1. Ask about specific fact (e.g., 'What is the project budget?')",
     "Answer matches document content accurately; No hallucinated facts",
     "High", "Not Executed"],

    ["RAG-005", "Agent", "RAG", "Ask follow-up questions in same session",
     "Previous Q&A in session; Documents extracted",
     "1. Ask initial question\n2. Ask follow-up referencing previous answer",
     "Agent maintains context; Follow-up answer builds on previous conversation",
     "Medium", "Not Executed"],

    # Edge
    ["RAG-006", "Agent", "RAG", "RAG with very large documents",
     "Large document (50+ pages) uploaded and processed",
     "1. Ask specific question\n2. Send",
     "Agent handles large text; Returns relevant answer without timeout; Response within acceptable time",
     "Medium", "Not Executed"],
]

# ============================================================
# 11. DASHBOARD
# ============================================================
dashboard_tests = [
    ["DASH-001", "Dashboard", "Stats", "Admin views dashboard statistics",
     "Admin logged in; System has users, sessions, token usage",
     "1. Navigate to /dashboard\n2. GET /api/dashboard/stats",
     "Dashboard displays: total users, pending approvals, token usage; Data accurate and up-to-date",
     "High", "Not Executed"],

    ["DASH-002", "Dashboard", "Stats", "Dashboard reflects real-time user count",
     "Admin logged in; New user just registered",
     "1. New user registers\n2. Admin refreshes dashboard",
     "User count incremented; New user visible in stats",
     "Medium", "Not Executed"],

    ["DASH-003", "Dashboard", "Stats", "Dashboard shows token usage tracking",
     "Multiple agent generations completed consuming tokens",
     "1. View dashboard\n2. Check token usage section",
     "Token usage displayed; Breakdown by operation type; Accurate counts",
     "Medium", "Not Executed"],

    ["DASH-004", "Dashboard", "Navigation", "Dashboard role-aware display",
     "Users with different roles",
     "1. Login as Admin → view dashboard\n2. Login as Architect → view dashboard\n3. Login as Developer → view dashboard",
     "Each role sees appropriate dashboard view; Admin sees full stats; Others see limited view",
     "Medium", "Not Executed"],

    # Negative
    ["DASH-005", "Dashboard", "Stats", "Non-admin access to dashboard stats API",
     "User logged in as Developer",
     "1. GET /api/dashboard/stats",
     "403 Forbidden; Stats not returned",
     "High", "Not Executed"],
]

# ============================================================
# 12. PRESALES DECK APPROVAL
# ============================================================
approval_tests = [
    ["APR-001", "Approval", "Submit", "Submit presales deck for approval",
     "PPT generated; User is Architect",
     "1. Generate PPT\n2. Submit for approval",
     "Deck status changes to PendingApproval; Admin notified; Deck visible in admin approve page",
     "High", "Not Executed"],

    ["APR-002", "Approval", "Approve", "Admin approves presales deck",
     "Admin logged in; Pending deck exists",
     "1. Navigate to /admin/approve\n2. Select pending deck\n3. Click Approve",
     "Deck status → Approved; Visible in /approved-decks; Creator notified",
     "High", "Not Executed"],

    ["APR-003", "Approval", "Reject", "Admin rejects presales deck",
     "Admin logged in; Pending deck exists",
     "1. Navigate to /admin/approve\n2. Select deck\n3. Click Reject\n4. Add rejection reason",
     "Deck status → Rejected; Reason recorded; Creator notified to revise",
     "High", "Not Executed"],

    ["APR-004", "Approval", "View", "View approved decks across roles",
     "Approved decks exist; Various roles logged in",
     "1. Navigate to /approved-decks",
     "All approved decks listed; Download links functional; Metadata (project, date, author) displayed",
     "Medium", "Not Executed"],

    ["APR-005", "Approval", "Workflow", "Resubmit rejected deck after changes",
     "Deck was rejected; User made changes",
     "1. Modify rejected deck content\n2. Regenerate\n3. Resubmit for approval",
     "New version submitted; Status back to PendingApproval; Previous rejection history preserved",
     "Medium", "Not Executed"],

    # Negative
    ["APR-006", "Approval", "Approve", "Non-admin attempts to approve deck",
     "Architect logged in; Pending deck exists",
     "1. Try to access approve API endpoint\n2. Submit approval",
     "403 Forbidden; Only admin can approve/reject",
     "High", "Not Executed"],
]

# ============================================================
# 13. END-TO-END FLOWS
# ============================================================
e2e_tests = [
    ["E2E-001", "End-to-End", "Full Flow", "Complete presales deck generation workflow",
     "User registered and logged in as Architect; Project documents available",
     "1. Login as Architect\n2. Create new chat session\n3. Upload artifacts (PDF, DOCX)\n4. Process artifacts\n5. Answer clarification questions\n6. Generate Architecture Diagram (POC)\n7. Review and approve diagram\n8. Generate DFD\n9. Review and approve DFD\n10. Generate PPT\n11. Download PPT\n12. Generate Cost Report\n13. Download Cost Report\n14. Submit for admin approval",
     "All deliverables generated successfully; PPT contains architecture + DFD images; Cost report accurate; Deck submitted for approval",
     "High", "Not Executed"],

    ["E2E-002", "End-to-End", "Full Flow", "End-to-end with feedback iterations",
     "User as Architect; Documents uploaded",
     "1. Upload and process artifacts\n2. Generate architecture\n3. Provide feedback 'Add caching layer'\n4. Architecture regenerated\n5. Approve\n6. Generate DFD\n7. Provide feedback 'Add payment flow'\n8. DFD regenerated\n9. Approve\n10. Generate PPT\n11. Download final",
     "Each feedback iteration produces updated deliverable; Final outputs incorporate all feedback; History preserved in chat",
     "High", "Not Executed"],

    ["E2E-003", "End-to-End", "Full Flow", "Admin approval and distribution workflow",
     "Architect submitted deck; Admin logged in",
     "1. Architect submits deck\n2. Admin logs in\n3. Reviews pending deck\n4. Approves\n5. Developer logs in\n6. Views approved deck\n7. Downloads PPT",
     "Full approval chain works; All roles can view approved deck; Download functional",
     "High", "Not Executed"],

    ["E2E-004", "End-to-End", "Full Flow", "MVP vs POC generation comparison",
     "Artifacts uploaded; Both phases needed",
     "1. Generate POC architecture\n2. Generate MVP architecture\n3. Generate POC cost report\n4. Generate MVP cost report\n5. Generate BOTH cost comparison\n6. Compare outputs",
     "POC has minimal components; MVP has full production setup; Cost report BOTH shows side-by-side; Clear differences visible",
     "High", "Not Executed"],

    ["E2E-005", "End-to-End", "RAG + Generation", "Chat with docs then generate deliverables",
     "Artifacts uploaded",
     "1. Upload artifacts\n2. Ask RAG questions about project\n3. Use insights to guide generation\n4. Generate all deliverables",
     "RAG answers inform generation; Deliverables reflect document content accurately",
     "Medium", "Not Executed"],

    ["E2E-006", "End-to-End", "Multi-Session", "Work across multiple chat sessions",
     "User has multiple projects",
     "1. Create Session A for Project A\n2. Upload Project A artifacts\n3. Generate deliverables\n4. Create Session B for Project B\n5. Upload different artifacts\n6. Generate deliverables",
     "Sessions isolated; Project A deliverables not mixed with Project B; Each session has correct context",
     "Medium", "Not Executed"],

    # Negative E2E
    ["E2E-007", "End-to-End", "Error Recovery", "Network interruption during generation",
     "User generating PPT; Network drops mid-generation",
     "1. Start PPT generation\n2. Simulate network interruption\n3. Reconnect",
     "Partial generation handled; User can retry; No corrupt files; Session state preserved",
     "Medium", "Not Executed"],

    ["E2E-008", "End-to-End", "Error Recovery", "Session timeout during long workflow",
     "User in middle of generation workflow; Session times out",
     "1. Start generation flow\n2. Wait for session timeout\n3. Re-authenticate\n4. Return to chat",
     "Token refresh attempted; If expired, re-login required; Previous session and messages preserved",
     "Medium", "Not Executed"],
]

# ============================================================
# 14. API & AGENT HEALTH
# ============================================================
health_tests = [
    ["HLT-001", "Health", "API Health", "Agent health check endpoint",
     "Agent service running",
     "1. GET /health",
     "200 OK; Health status returned; Service operational",
     "High", "Not Executed"],

    ["HLT-002", "Health", "API Health", ".NET API health check",
     ".NET API running",
     "1. Send request to API base URL",
     "API responds; Endpoints accessible",
     "High", "Not Executed"],

    ["HLT-003", "Health", "Dependencies", "Azure OpenAI connectivity",
     "Agent service running; Azure OpenAI configured",
     "1. Send generation request that requires Azure OpenAI",
     "LLM responds; Generation produces output; No timeout",
     "High", "Not Executed"],

    ["HLT-004", "Health", "Dependencies", "Cosmos DB connectivity",
     "Agent running; Cosmos DB configured",
     "1. Upload and process artifact (text stored in Cosmos DB)\n2. RAG query",
     "Text stored and retrieved successfully from Cosmos DB",
     "High", "Not Executed"],

    ["HLT-005", "Health", "Dependencies", "Azure Blob Storage connectivity",
     "Agent running; Blob storage configured",
     "1. Generate PPT (uploaded to blob)\n2. Download via URL",
     "File uploaded and downloadable; Blob URLs functional",
     "High", "Not Executed"],
]

# ============================================================
# CREATE WORKSHEETS
# ============================================================
sheets_data = [
    ("Authentication", auth_tests),
    ("RBAC", rbac_tests),
    ("Chat", chat_tests),
    ("Artifacts", artifact_tests),
    ("Clarification", clarification_tests),
    ("Architecture Diagram", arch_tests),
    ("DFD", dfd_tests),
    ("PowerPoint", ppt_tests),
    ("Cost Report", cost_tests),
    ("RAG", rag_tests),
    ("Dashboard", dashboard_tests),
    ("Approval Workflow", approval_tests),
    ("End-to-End", e2e_tests),
    ("Health & Dependencies", health_tests),
]

# Remove default sheet
wb.remove(wb.active)

# Summary sheet
summary_ws = wb.create_sheet("Summary", 0)
summary_headers = ["#", "Module", "Total Test Cases", "High Priority", "Medium Priority", "Low Priority"]
for col_idx, h in enumerate(summary_headers, 1):
    cell = summary_ws.cell(row=1, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = thin_border

summary_ws.column_dimensions["A"].width = 6
summary_ws.column_dimensions["B"].width = 28
summary_ws.column_dimensions["C"].width = 18
summary_ws.column_dimensions["D"].width = 15
summary_ws.column_dimensions["E"].width = 15
summary_ws.column_dimensions["F"].width = 15

grand_total = 0
grand_high = 0
grand_med = 0
grand_low = 0

for idx, (name, tests) in enumerate(sheets_data, 1):
    ws = wb.create_sheet(name)
    write_sheet(ws, tests)

    total = len(tests)
    high = sum(1 for t in tests if t[7] == "High")
    med = sum(1 for t in tests if t[7] == "Medium")
    low = sum(1 for t in tests if t[7] == "Low")

    grand_total += total
    grand_high += high
    grand_med += med
    grand_low += low

    row_data = [idx, name, total, high, med, low]
    for col_idx, val in enumerate(row_data, 1):
        cell = summary_ws.cell(row=idx + 1, column=col_idx, value=val)
        cell.alignment = center_align
        cell.border = thin_border

# Grand total row
total_row = len(sheets_data) + 2
for col_idx, val in enumerate(["", "TOTAL", grand_total, grand_high, grand_med, grand_low], 1):
    cell = summary_ws.cell(row=total_row, column=col_idx, value=val)
    cell.font = Font(bold=True, size=11)
    cell.fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    cell.alignment = center_align
    cell.border = thin_border

summary_ws.freeze_panes = "A2"

# Save
output_path = r"c:\Users\AaditeeAgrawal\source\repos\optimus-Presales-Agent\OptiStudio_Functional_Test_Cases.xlsx"
wb.save(output_path)
print(f"Excel file saved to: {output_path}")
print(f"Total test cases: {grand_total}")
print(f"  High: {grand_high}, Medium: {grand_med}, Low: {grand_low}")
print(f"Sheets: {len(sheets_data) + 1} (Summary + {len(sheets_data)} module sheets)")
