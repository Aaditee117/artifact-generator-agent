# 🚀 OptiStudio

An integrated AI-enabled platform designed to accelerate and standardize the entire project lifecycle — from pre-sales engagement to project delivery.

> **Branch:** `feature/rbac-authorization`
> **Tech Stack:** .NET 10 (Backend) · React + TypeScript (Frontend) · SQL Server (Database)

---

## 📖 Table of Contents

1. [What is OptiStudio?](#-what-is-optistudio)
2. [Architecture Patterns Explained](#-architecture-patterns-explained-for-beginners)
   - [Clean Architecture](#1-clean-architecture)
   - [CQRS Pattern](#2-cqrs-command-query-responsibility-segregation)
   - [Repository Pattern](#3-repository-pattern)
   - [How They Work Together](#4-how-all-three-work-together)
3. [Project Structure](#-project-structure)
4. [Application Flow](#-application-flow)
5. [API Endpoints](#-api-endpoints)
6. [Database Schema](#-database-schema)
7. [Packages & Why They Are Used](#-packages--why-they-are-used)
8. [Prerequisites](#-prerequisites)
9. [Setup Instructions](#-setup-instructions)
10. [How to Build This From Scratch](#-how-to-build-this-from-scratch)
11. [Role-Based Access Control](#-role-based-access-control)
12. [Security Features](#-security-features)

---

## 🎯 What is OptiStudio?

Modern project teams spend significant time transforming unstructured information (meetings, emails, documents) into formal deliverables such as pre-sales decks.

OptiStudio solves this by providing:
- **Pre-Sales Deck Generation** — Architecture diagrams, DFDs, presentations, Azure cost reports
- **AI Chatbot** — Query structured (SQL) and unstructured (documents) data
- **Role-Based Access** — Admin, Architect, and Developer roles with different permissions
- **Secure Authentication** — JWT tokens stored in HttpOnly cookies with OTP-based registration

**Current Implementation Status:**
- ✅ Authentication (Register, Login, OTP Verification, Refresh Tokens, Logout)
- ✅ Role-Based Access Control (Admin, Architect, Developer)
- ✅ Admin Panel (User Management with role assignment)
- ✅ React Frontend with role-aware dashboard
- 🔜 Pre-Sales Deck Generation (upcoming)
- 🔜 AI Chatbot with MCP Client/Server (upcoming)

---

## 🧠 Architecture Patterns Explained (For Beginners)

### 1. Clean Architecture

**What is it?**

Clean Architecture is a way of organizing your code into **layers**, like an onion. Each layer has a specific job, and there are strict rules about which layer can talk to which.

**Why do we use it?**

Imagine you build a house where the plumbing is mixed into the walls, the electrical wires run through the furniture, and the paint is mixed into the foundation. If you want to change the paint color, you'd have to tear down the whole house! Clean Architecture prevents this by keeping things separated.

**The Layers (from innermost to outermost):**

```
┌──────────────────────────────────────────────┐
│                   API Layer                  │  ← Outermost: Receives HTTP requests
│  (Controllers, Middleware, Program.cs)       │
├──────────────────────────────────────────────┤
│          Infrastructure Layer                │  ← External services (email, JWT)
│  (JwtService, EmailService, PasswordHasher) │
├──────────────────────────────────────────────┤
│           Persistence Layer                  │  ← Database access (EF Core, Repos)
│  (DbContext, Repositories, Migrations)       │
├──────────────────────────────────────────────┤
│           Application Layer                  │  ← Business logic (what the app does)
│  (Commands, Queries, DTOs, Interfaces)       │
├──────────────────────────────────────────────┤
│             Domain Layer                     │  ← Innermost: Pure business objects
│  (Entities like User, OtpRecord, Enums)      │
└──────────────────────────────────────────────┘
```

**The Golden Rule:** Inner layers **NEVER** know about outer layers.

- `Domain` knows about nothing — it's just plain C# classes
- `Application` knows about `Domain` — it uses User, OtpRecord, etc.
- `Infrastructure` and `Persistence` know about `Application` — they implement its interfaces
- `API` knows about everything — it wires all layers together

**Real-world analogy:** Think of it like a restaurant:
- **Domain** = The recipes (pure knowledge, doesn't depend on anything)
- **Application** = The head chef (decides what to cook, gives instructions)
- **Infrastructure** = The delivery service, payment system (external services)
- **Persistence** = The pantry/storage (where ingredients are kept)
- **API** = The waiter (takes customer orders and delivers food)

The recipe doesn't care whether you store ingredients in a fridge or a cupboard. The chef doesn't care how the waiter talks to customers. Each layer does its own job.

---

### 2. CQRS (Command Query Responsibility Segregation)

**What is it?**

CQRS means: **separate the code that changes data (Commands) from the code that reads data (Queries).**

**Why do we use it?**

Without CQRS, you might have one big `UserService` class with methods like `Register()`, `Login()`, `GetUser()`, `UpdateRole()` — all mixed together. As the app grows, this class becomes a 1000-line monster that's hard to understand and modify.

With CQRS, each action gets its own folder with its own files:

```
Features/
├── Auth/
│   ├── Commands/              ← Things that CHANGE data
│   │   ├── Register/
│   │   │   ├── RegisterCommand.cs           ← "What data do I need?"
│   │   │   ├── RegisterCommandHandler.cs    ← "How do I process it?"
│   │   │   └── RegisterCommandValidator.cs  ← "Is the data valid?"
│   │   ├── Login/
│   │   ├── VerifyOtp/
│   │   ├── Logout/
│   │   ├── RefreshAccessToken/
│   │   └── ResendOtp/
│   │
│   └── Queries/               ← Things that READ data
│       └── GetCurrentUser/
│           ├── GetCurrentUserQuery.cs
│           └── GetCurrentUserQueryHandler.cs
│
└── Admin/
    ├── Commands/
    │   └── UpdateUserRole/
    └── Queries/
        └── GetAllUsers/
```

**How does it work in our app?**

1. The **Controller** receives an HTTP request
2. It creates a **Command** or **Query** object (just a data container)
3. It sends it via **MediatR** (a library that routes commands to handlers)
4. The correct **Handler** picks it up and does the work
5. The handler returns a **DTO** (response object) back to the controller

```
HTTP Request → Controller → Command/Query → MediatR → Handler → Response
```

**Example — Login Flow:**

```csharp
// Step 1: Controller creates the command
var command = new LoginCommand { Email = "user@test.com", Password = "Pass@123" };

// Step 2: MediatR routes it to LoginCommandHandler automatically
var result = await _mediator.Send(command);

// Step 3: Handler does the work (check password, generate JWT, etc.)
// Step 4: Returns AuthResponseDto with token and user info
```

**Benefits:**
- Each feature is in its own folder — easy to find
- You can modify "Register" without touching "Login"
- Easy to add new features — just create a new Command folder
- Validation is automatic via the pipeline

---

### 3. Repository Pattern

**What is it?**

The Repository Pattern puts a **layer between your business logic and the database**. Instead of writing database queries directly in your handlers, you call simple methods like `GetByEmailAsync()` or `AddAsync()`.

**Why do we use it?**

Without repositories:
```csharp
// ❌ Database code mixed into business logic
var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == email);
```

With repositories:
```csharp
// ✅ Clean — handler doesn't know about Entity Framework
var user = await _unitOfWork.Users.GetByEmailAsync(email);
```

**Benefits:**
- If you switch from SQL Server to MongoDB tomorrow, you only change the repository — not every handler
- Business logic stays clean and readable
- Easy to test — you can mock repositories in unit tests

**Unit of Work Pattern (bonus):**

We also use the **Unit of Work** pattern. Think of it as a shopping cart:
- You add items to the cart (make changes via repositories)
- Nothing is purchased until you click "Checkout" (`SaveChangesAsync()`)
- If something fails, nothing is saved — all-or-nothing

```csharp
// Make multiple changes
_unitOfWork.Users.Update(user);
_unitOfWork.Otps.AddAsync(otp);

// Save everything at once (like clicking "Checkout")
await _unitOfWork.SaveChangesAsync();
```

---

### 4. How All Three Work Together

Here's what happens when a user clicks **"Register"** on the website:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐     ┌────────────────┐     ┌──────────────┐
│   React UI  │────▶│  API Layer   │────▶│  Application Layer  │────▶│ Persistence    │────▶│  SQL Server  │
│  (Browser)  │     │ (Controller) │     │  (Command Handler)  │     │ (Repository)   │     │  (Database)  │
└─────────────┘     └──────────────┘     └─────────────────────┘     └────────────────┘     └──────────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │ Infrastructure  │
                                          │ (Email Service) │
                                          └─────────────────┘
```

1. **React** sends `POST /api/auth/register` with email and password
2. **AuthController** (API Layer) creates a `RegisterCommand` and sends it via MediatR
3. **ValidationBehavior** (Application Layer) automatically validates the request using `RegisterCommandValidator`
   - Is email valid? Is password strong enough? Do passwords match?
   - If validation fails → returns error immediately (never reaches the handler)
4. **RegisterCommandHandler** (Application Layer) runs the business logic:
   - Calls `_unitOfWork.Users.GetByEmailAsync()` → Repository asks the database
   - Hashes the password via `_passwordHasher.Hash()` → Infrastructure service
   - Creates User entity → Domain layer object
   - Generates 4-digit OTP
   - Saves everything via `_unitOfWork.SaveChangesAsync()` → Repository writes to database
   - Sends OTP email via `_emailService.SendOtpEmailAsync()` → Infrastructure service
5. **Controller** receives the result and sends HTTP response back to React

**Notice:** The Handler (Application Layer) never directly touches the database or sends emails itself. It only calls interfaces (`IUnitOfWork`, `IEmailService`). The actual implementations live in Persistence and Infrastructure layers. This is **Dependency Inversion** — the core of Clean Architecture.

---

## 📁 Project Structure

```
OptiStudio/
│
├── 📂 OptiStudio.Domain/                    ← Layer 1: Core (no dependencies)
│   ├── Entity/
│   │   ├── BaseEntity.cs                    # Id, CreatedAt, UpdatedAt
│   │   ├── User.cs                          # Email, PasswordHash, Role
│   │   ├── OtpRecord.cs                     # 4-digit OTP with expiry
│   │   └── RefreshToken.cs                  # Long-lived token for re-auth
│   └── Enum/
│       └── Role.cs                          # Developer, Architect, Admin
│
├── 📂 OptiStudio.Application/               ← Layer 2: Business Logic
│   ├── Interface/                           # Contracts (what, not how)
│   │   ├── IUserRepository.cs
│   │   ├── IOtpRepository.cs
│   │   ├── IRefreshTokenRepository.cs
│   │   ├── IUnitOfWork.cs
│   │   ├── IJwtService.cs
│   │   ├── IEmailService.cs
│   │   └── IPasswordHasher.cs
│   ├── DTO/                                 # Data shapes for API
│   │   ├── Auth/
│   │   │   ├── RegisterRequestDto.cs
│   │   │   ├── LoginRequestDto.cs
│   │   │   ├── VerifyOtpRequestDto.cs
│   │   │   └── AuthResponseDto.cs           # Includes UserDto with Role
│   │   └── Admin/
│   │       ├── UpdateUserRoleRequestDto.cs
│   │       └── UserListResponseDto.cs
│   ├── Features/                            # CQRS Commands & Queries
│   │   ├── Auth/
│   │   │   ├── Commands/
│   │   │   │   ├── Register/                # Command + Handler + Validator
│   │   │   │   ├── Login/
│   │   │   │   ├── VerifyOtp/
│   │   │   │   ├── Logout/
│   │   │   │   ├── RefreshAccessToken/
│   │   │   │   └── ResendOtp/
│   │   │   └── Queries/
│   │   │       └── GetCurrentUser/
│   │   └── Admin/
│   │       ├── Commands/
│   │       │   └── UpdateUserRole/
│   │       └── Queries/
│   │           └── GetAllUsers/
│   ├── Behaviors/
│   │   └── ValidationBehavior.cs            # Auto-validates all commands
│   └── ApplicationServiceRegistration.cs    # DI setup for this layer
│
├── 📂 OptiStudio.Infrastructure/            ← Layer 3a: External Services
│   ├── Settings/
│   │   ├── JwtSettings.cs                   # Token config (secret, expiry)
│   │   └── SmtpSettings.cs                  # Email config (Gmail SMTP)
│   ├── Services/
│   │   ├── JwtService.cs                    # JWT generation with Role claim
│   │   ├── EmailService.cs                  # Sends OTP via Gmail SMTP
│   │   └── PasswordHasher.cs               # BCrypt hashing (work factor 12)
│   └── InfrastructureServiceRegistration.cs
│
├── 📂 OptiStudio.Persistence/              ← Layer 3b: Database Access
│   ├── Data/
│   │   ├── OptiStudioDbContext.cs           # EF Core DbContext
│   │   └── DbInitializer.cs                # Seeds admin user on first run
│   ├── Configurations/
│   │   ├── UserConfiguration.cs             # Table schema + constraints
│   │   ├── OtpRecordConfiguration.cs
│   │   └── RefreshTokenConfiguration.cs
│   ├── Repository/
│   │   ├── UserRepository.cs
│   │   ├── OtpRepository.cs
│   │   ├── RefreshTokenRepository.cs
│   │   └── UnitOfWork.cs                    # Wraps all repos + SaveChanges
│   ├── Migrations/
│   │   ├── InitialCreate.cs
│   │   └── AddUserRole.cs
│   └── PersistenceServiceRegistration.cs
│
├── 📂 OptiStudio.API/                      ← Layer 4: Entry Point
│   ├── Controllers/
│   │   ├── AuthController.cs               # Register, Login, OTP, Logout, Me
│   │   └── AdminController.cs              # User Management (Admin-only)
│   ├── MiddleWare/
│   │   └── ExceptionHandlingMiddleware.cs  # Global error handler
│   ├── Properties/
│   │   └── launchSettings.json
│   ├── Program.cs                          # Wires everything together
│   └── appsettings.json                    # All configuration
│
└── 📂 optistudio-client/                   ← React Frontend
    └── src/
        ├── services/
        │   ├── api.ts                       # Axios instance + refresh interceptor
        │   └── authService.ts               # All API calls + admin service
        ├── context/
        │   └── AuthContext.tsx               # Auth state + hasRole() helper
        ├── components/
        │   ├── ProtectedRoute.tsx            # Requires login
        │   └── RoleProtectedRoute.tsx        # Requires specific role
        ├── pages/
        │   ├── LoginPage.tsx
        │   ├── RegisterPage.tsx
        │   ├── VerifyOtpPage.tsx
        │   ├── DashboardPage.tsx             # Role-aware feature cards
        │   └── AdminUsersPage.tsx            # User management table
        ├── App.tsx                           # Routes
        ├── main.tsx                          # Entry point
        └── index.css                         # Red & white theme
```

---

## 🔄 Application Flow

### Flow 1: Registration (New User)

```
User fills Register form
        │
        ▼
POST /api/auth/register { email, password, confirmPassword }
        │
        ▼
RegisterCommandValidator checks:
  ✓ Valid email format
  ✓ Password: 8+ chars, uppercase, lowercase, digit, special char
  ✓ Passwords match
        │
        ▼
RegisterCommandHandler:
  1. Check if email already exists → reject if verified user exists
  2. Hash password with BCrypt (work factor 12)
  3. Create User entity (Role = Developer, IsEmailVerified = false)
  4. Generate random 4-digit OTP
  5. Save OtpRecord (expires in 5 minutes)
  6. Save to database
  7. Send OTP email via Gmail SMTP
        │
        ▼
Response: { success: true, message: "Check your email for OTP" }
        │
        ▼
React navigates to /verify-otp page
```

### Flow 2: OTP Verification

```
User enters 4-digit OTP code
        │
        ▼
POST /api/auth/verify-otp { email, otpCode }
        │
        ▼
VerifyOtpCommandHandler:
  1. Find user by email
  2. Get latest unused OTP for this user
  3. Check: code matches AND not expired (< 5 minutes)
  4. Mark OTP as used
  5. Set user.IsEmailVerified = true
  6. Generate JWT access token (15 min expiry)
  7. Generate refresh token (7 day expiry)
  8. Save refresh token to database
  9. Set HttpOnly cookies: accessToken + refreshToken
        │
        ▼
Response: { success: true, user: { id, email, role: "Developer" } }
        │
        ▼
React navigates to /dashboard
```

### Flow 3: Login (Returning User)

```
User fills Login form
        │
        ▼
POST /api/auth/login { email, password }
        │
        ▼
LoginCommandHandler:
  1. Find user by email
  2. Check email is verified → reject if not
  3. BCrypt.Verify(password, storedHash) → reject if mismatch
  4. Revoke all existing refresh tokens for this user
  5. Generate new access + refresh tokens
  6. Set HttpOnly cookies
        │
        ▼
React navigates to /dashboard (shows role-specific cards)
```

### Flow 4: Accessing Protected Routes

```
Browser sends request to GET /api/auth/me
        │
        ▼
ASP.NET reads "accessToken" from HttpOnly cookie
        │
        ▼
JwtBearer middleware validates:
  ✓ Token signature is valid
  ✓ Token is not expired
  ✓ Issuer and audience match
        │
        ├── Valid → Handler returns user info
        │
        └── Expired (401) → React interceptor calls POST /api/auth/refresh-token
                │
                ├── Refresh token valid → New tokens issued, retry original request
                │
                └── Refresh token invalid → Redirect to /login
```

### Flow 5: Admin Changes User Role

```
Admin opens /admin/users page
        │
        ▼
GET /api/admin/users (requires Role = "Admin" in JWT)
        │
        ▼
Returns list of all users with their roles
        │
        ▼
Admin changes dropdown to "Architect" for a user
        │
        ▼
PUT /api/admin/users/{userId}/role { role: "Architect" }
        │
        ▼
UpdateUserRoleCommandHandler:
  1. Find user by ID
  2. Validate role string (Admin/Architect/Developer)
  3. Update user.Role
  4. Save to database
        │
        ▼
User table updates in real-time
```

---

## 📡 API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|:------------:|-------------|
| POST | `/api/auth/register` | ❌ | Register with email + password |
| POST | `/api/auth/verify-otp` | ❌ | Verify email with 4-digit OTP |
| POST | `/api/auth/login` | ❌ | Login with email + password |
| POST | `/api/auth/refresh-token` | ❌ | Get new access token using refresh token |
| POST | `/api/auth/resend-otp` | ❌ | Resend OTP to email |
| POST | `/api/auth/logout` | ✅ | Logout and revoke all tokens |
| GET | `/api/auth/me` | ✅ | Get current user info |

### Admin (`/api/admin`) — Admin Role Required

| Method | Endpoint | Auth Required | Description |
|--------|----------|:------------:|-------------|
| GET | `/api/admin/users` | ✅ Admin | List all users |
| PUT | `/api/admin/users/{id}/role` | ✅ Admin | Update a user's role |

---

## 🗄️ Database Schema

```
OptiStudioDb (SQL Server)

┌─────────────────────────────────────────────┐
│                   Users                     │
├─────────────────────────────────────────────┤
│ Id              uniqueidentifier  PK        │
│ Email           nvarchar(256)     UNIQUE    │
│ PasswordHash    nvarchar(max)               │
│ IsEmailVerified bit               default 0 │
│ Role            nvarchar(20)      default   │
│                                  'Developer'│
│ CreatedAt       datetime2                   │
│ UpdatedAt       datetime2         nullable  │
└─────────────────────────────────────────────┘
        │ 1
        │
        ├──────── * ┌──────────────────────────┐
        │           │       OtpRecords         │
        │           ├──────────────────────────┤
        │           │ Id          GUID    PK   │
        │           │ UserId      GUID    FK   │
        │           │ Code        nvar(4)      │
        │           │ ExpiresAt   datetime2    │
        │           │ IsUsed      bit          │
        │           │ CreatedAt   datetime2    │
        │           │ UpdatedAt   datetime2    │
        │           └──────────────────────────┘
        │
        └──────── * ┌──────────────────────────┐
                    │     RefreshTokens        │
                    ├──────────────────────────┤
                    │ Id          GUID    PK   │
                    │ UserId      GUID    FK   │
                    │ Token       nvar(512)    │
                    │             UNIQUE       │
                    │ ExpiresAt   datetime2    │
                    │ IsRevoked   bit          │
                    │ CreatedAt   datetime2    │
                    │ UpdatedAt   datetime2    │
                    └──────────────────────────┘
```

---

## 📦 Packages & Why They Are Used

### OptiStudio.Domain (No packages)
> The innermost layer. Pure C# classes with zero dependencies. This is intentional — domain entities should never depend on any framework.

### OptiStudio.Application

| Package | Version | Why? |
|---------|---------|------|
| **MediatR** | 14.1.0 | Implements the CQRS pattern. Routes Commands/Queries to their Handlers automatically without the controller needing to know which handler exists. |
| **FluentValidation.DependencyInjectionExtensions** | 12.1.1 | Validates incoming data (email format, password strength) using readable rules. The DI extension auto-discovers all validators in the assembly. |
| **Microsoft.Extensions.DependencyInjection.Abstractions** | 10.0.5 | Provides `IServiceCollection` so this layer can register its own services without depending on ASP.NET Core. |

### OptiStudio.Infrastructure

| Package | Version | Why? |
|---------|---------|------|
| **System.IdentityModel.Tokens.Jwt** | 8.16.0 | Creates and reads JWT tokens. This is the core library for generating the signed access tokens. |
| **Microsoft.IdentityModel.Tokens** | 8.16.0 | Provides `SymmetricSecurityKey` and `SigningCredentials` used to sign JWT tokens with HMAC-SHA256. |
| **MailKit** | 4.15.1 | Industry-standard .NET library for sending emails. We use it to send OTP codes via Gmail SMTP. More reliable and modern than the built-in `System.Net.Mail`. |
| **BCrypt.Net-Next** | 4.1.0 | Hashes passwords using the BCrypt algorithm (work factor 12). BCrypt is specifically designed for passwords — it's slow on purpose to prevent brute-force attacks. |
| **Microsoft.Extensions.Options.ConfigurationExtensions** | 10.0.5 | Maps `appsettings.json` sections (like `JwtSettings`, `SmtpSettings`) to strongly-typed C# classes using the Options Pattern. |
| **Microsoft.Extensions.DependencyInjection.Abstractions** | 10.0.5 | Same as Application — allows DI registration without ASP.NET Core dependency. |

### OptiStudio.Persistence

| Package | Version | Why? |
|---------|---------|------|
| **Microsoft.EntityFrameworkCore.SqlServer** | 10.0.5 | The EF Core database provider for SQL Server. Translates C# LINQ queries into SQL and manages the database connection. |
| **Microsoft.EntityFrameworkCore.Tools** | 10.0.5 | Provides `dotnet ef` CLI commands for creating migrations and updating the database. Only used during development (build tool). |
| **Microsoft.Extensions.DependencyInjection.Abstractions** | 10.0.5 | Same purpose — DI registration for the persistence layer. |

### OptiStudio.API

| Package | Version | Why? |
|---------|---------|------|
| **Microsoft.AspNetCore.Authentication.JwtBearer** | 10.0.5 | ASP.NET Core middleware that automatically validates JWT tokens on every request to `[Authorize]` endpoints. We configured it to read tokens from HttpOnly cookies. |
| **Microsoft.AspNetCore.OpenApi** | 10.0.5 | Generates OpenAPI (Swagger) documentation for all API endpoints. |
| **Microsoft.EntityFrameworkCore.Design** | 10.0.5 | Required by the `dotnet ef` CLI tool in the startup project. Only used during development for migration generation. |

### React Frontend (optistudio-client)

| Package | Why? |
|---------|------|
| **react-router-dom** | Client-side routing — navigates between Login, Register, Dashboard, Admin pages without page reloads. |
| **axios** | HTTP client for calling the backend API. Supports interceptors (auto-refresh tokens on 401), cookies (`withCredentials`), and clean async/await syntax. |

---

## ✅ Prerequisites

Before running this project, make sure you have:

| Tool | Version | Download |
|------|---------|----------|
| **.NET SDK** | 10.0+ | [dotnet.microsoft.com](https://dotnet.microsoft.com/download) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org) |
| **SQL Server** | Express or higher | [SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads) |
| **Visual Studio** | 2022/2026 | [visualstudio.microsoft.com](https://visualstudio.microsoft.com) |
| **EF Core Tools** | Latest | Run: `dotnet tool install --global dotnet-ef` |
| **Gmail App Password** | — | [Generate here](https://myaccount.google.com/apppasswords) (requires 2FA enabled) |

---

## ⚙️ Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/Aditee-agrawal/OptiStudio.git
cd OptiStudio
git checkout feature/rbac-authorization
```

### Step 2: Configure appsettings.json

Open `OptiStudio.API/appsettings.json` and update:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=YOUR_SERVER\\SQLEXPRESS;Initial Catalog=OptiStudioDb;Integrated Security=True;MultipleActiveResultSets=True;Encrypt=True;TrustServerCertificate=True"
  },
  "SmtpSettings": {
    "SenderEmail": "your-gmail@gmail.com",
    "SenderPassword": "your-16-char-app-password"
  }
}
```

> **How to get a Gmail App Password:**
> 1. Go to [myaccount.google.com](https://myaccount.google.com)
> 2. Security → 2-Step Verification → Turn ON
> 3. Security → App Passwords → Generate one for "Mail"
> 4. Copy the 16-character password into `SenderPassword`

### Step 3: Create the Database

```powershell
cd OptiStudio
dotnet ef database update --project OptiStudio.Persistence --startup-project OptiStudio.API
```

This creates the `OptiStudioDb` database with all tables.

### Step 4: Run the Backend

```powershell
# From solution root
dotnet run --project OptiStudio.API --launch-profile https
```

The API runs at: **https://localhost:7126**

On first run, it automatically seeds an admin user:
- **Email:** `admin@optistudio.com`
- **Password:** `Admin@1234`

### Step 5: Run the Frontend

```powershell
cd optistudio-client
npm install
npm run dev
```

The React app runs at: **http://localhost:5173**

### Step 6: Open the App

1. Open **http://localhost:5173** in your browser
2. Login with `admin@optistudio.com` / `Admin@1234`
3. You'll see the Admin dashboard with all feature cards
4. Click "User Management" to manage roles

---

## 🔨 How to Build This From Scratch

If you want to create a similar project from zero, here's the step-by-step approach:

### Phase 1: Create the Solution & Projects

```powershell
# Create solution
dotnet new sln -n OptiStudio

# Create projects
dotnet new classlib -n OptiStudio.Domain
dotnet new classlib -n OptiStudio.Application
dotnet new classlib -n OptiStudio.Infrastructure
dotnet new classlib -n OptiStudio.Persistence
dotnet new webapi -n OptiStudio.API

# Add projects to solution
dotnet sln add OptiStudio.Domain
dotnet sln add OptiStudio.Application
dotnet sln add OptiStudio.Infrastructure
dotnet sln add OptiStudio.Persistence
dotnet sln add OptiStudio.API
```

### Phase 2: Set Up Project References (Dependency Rules)

```powershell
# Application depends on Domain
dotnet add OptiStudio.Application reference OptiStudio.Domain

# Infrastructure depends on Application (to implement interfaces)
dotnet add OptiStudio.Infrastructure reference OptiStudio.Application

# Persistence depends on Application (to implement interfaces)
dotnet add OptiStudio.Persistence reference OptiStudio.Application

# API depends on all (it wires everything together)
dotnet add OptiStudio.API reference OptiStudio.Application
dotnet add OptiStudio.API reference OptiStudio.Infrastructure
dotnet add OptiStudio.API reference OptiStudio.Persistence
```

### Phase 3: Install NuGet Packages

```powershell
# Application layer
dotnet add OptiStudio.Application package MediatR
dotnet add OptiStudio.Application package FluentValidation.DependencyInjectionExtensions
dotnet add OptiStudio.Application package Microsoft.Extensions.DependencyInjection.Abstractions

# Infrastructure layer
dotnet add OptiStudio.Infrastructure package System.IdentityModel.Tokens.Jwt
dotnet add OptiStudio.Infrastructure package Microsoft.IdentityModel.Tokens
dotnet add OptiStudio.Infrastructure package MailKit
dotnet add OptiStudio.Infrastructure package BCrypt.Net-Next
dotnet add OptiStudio.Infrastructure package Microsoft.Extensions.Options.ConfigurationExtensions
dotnet add OptiStudio.Infrastructure package Microsoft.Extensions.DependencyInjection.Abstractions

# Persistence layer
dotnet add OptiStudio.Persistence package Microsoft.EntityFrameworkCore.SqlServer
dotnet add OptiStudio.Persistence package Microsoft.EntityFrameworkCore.Tools
dotnet add OptiStudio.Persistence package Microsoft.Extensions.DependencyInjection.Abstractions

# API layer
dotnet add OptiStudio.API package Microsoft.AspNetCore.Authentication.JwtBearer
dotnet add OptiStudio.API package Microsoft.EntityFrameworkCore.Design

# Install EF Core CLI tool (global)
dotnet tool install --global dotnet-ef
```

### Phase 4: Build Layer by Layer (Inside → Outside)

1. **Domain** — Create entities (`User`, `OtpRecord`, `RefreshToken`) and enums (`Role`)
2. **Application** — Define interfaces, DTOs, CQRS commands/queries/handlers, validators
3. **Infrastructure** — Implement `IJwtService`, `IEmailService`, `IPasswordHasher`
4. **Persistence** — Create `DbContext`, configurations, repositories, `UnitOfWork`
5. **API** — Create controllers, middleware, configure `Program.cs` (auth, CORS, DI)
6. **Migrations** — Run `dotnet ef migrations add InitialCreate` and `dotnet ef database update`

### Phase 5: Create React Frontend

```powershell
npm create vite@latest optistudio-client -- --template react-ts
cd optistudio-client
npm install react-router-dom axios
```

Build pages: Login → Register → OTP Verification → Dashboard → Admin Panel

---

## 🔐 Role-Based Access Control

### Roles & Permissions

| Feature | Admin | Architect | Developer |
|---------|:-----:|:---------:|:---------:|
| Artifact Chatbot | ✅ Full | ✅ Full | ✅ Read-only |
| Presales Deck Generation | ✅ | ✅ | ❌ |
| Approve Final Deck | ✅ | ❌ | ❌ |
| Admin Chatbot | ✅ | ❌ | ❌ |
| Dashboards & Monitoring | ✅ | ❌ | ❌ |
| User Management | ✅ | ❌ | ❌ |

### How It Works

**Backend:** The user's role is embedded in the JWT token as a claim. ASP.NET Core's `[Authorize(Roles = "Admin")]` attribute automatically reads this claim and blocks unauthorized users with a `403 Forbidden` response.

**Frontend:** The `hasRole()` helper in `AuthContext` conditionally renders dashboard cards based on the user's role. The `RoleProtectedRoute` component guards routes like `/admin/users`.

**Default behavior:**
- New users register as **Developer**
- Only **Admin** can promote users to Architect or Admin
- A seeded admin (`admin@optistudio.com`) is created on first run

---

## 🛡️ Security Features

| Feature | Implementation |
|---------|---------------|
| **Password Hashing** | BCrypt with work factor 12 (slow by design, resistant to brute-force) |
| **JWT in HttpOnly Cookies** | Tokens cannot be read by JavaScript (prevents XSS attacks) |
| **Secure & SameSite Cookies** | `Secure=true`, `SameSite=None` (only sent over HTTPS) |
| **Access Token Expiry** | 15 minutes (short-lived, limits damage if compromised) |
| **Refresh Token Rotation** | Old refresh token is revoked when new one is issued |
| **Token Revocation on Logout** | All refresh tokens for the user are revoked |
| **OTP Expiry** | 4-digit code expires in 5 minutes |
| **Password Policy** | Min 8 chars, uppercase, lowercase, digit, special character |
| **Input Validation** | FluentValidation on every command (server-side, cannot be bypassed) |
| **Global Error Handling** | `ExceptionHandlingMiddleware` catches all errors, returns sanitized messages |
| **CORS Restriction** | Only `http://localhost:5173` (React dev server) is allowed |
| **Role in JWT** | `ClaimTypes.Role` claim enables `[Authorize(Roles = ...)]` on endpoints |

---

## 📝 License

This project is part of the OptiStudio initiative by [Optimus Information Inc.](https://www.optimusinfo.com/)
