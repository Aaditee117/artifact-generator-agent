using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Security.Claims;
using OptiStudio.API.MiddleWare;
using OptiStudio.Application;
using OptiStudio.Infrastructure;
using OptiStudio.Persistence;
using OptiStudio.Persistence.Data;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddOpenApi();

// Register application layers
builder.Services.AddApplicationServices();
builder.Services.AddInfrastructureServices(builder.Configuration);
builder.Services.AddPersistenceServices(builder.Configuration.GetConnectionString("DefaultConnection")!);

// Get Azure AD settings
var azureAdConfig = builder.Configuration.GetSection("AzureAd");
var clientId = azureAdConfig["ClientId"];

// Azure AD / MSAL Authentication - configured for multi-tenant with ID tokens
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        // Use the common endpoint for multi-tenant apps
        options.Authority = "https://login.microsoftonline.com/common/v2.0";

        // Token validation parameters for ID tokens
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = false,           // Multi-tenant - accept any issuer
            ValidateAudience = true,          
            ValidAudiences = new[] { clientId, $"api://{clientId}" }, // ID token audience is the client ID
            ValidateLifetime = true,          
            ValidateIssuerSigningKey = true
        };

        options.Events = new JwtBearerEvents
        {
            OnTokenValidated = async context =>
            {
                if (context.Principal?.Identity is ClaimsIdentity identity)
                {
                    var email = context.Principal.FindFirstValue("preferred_username") 
                             ?? context.Principal.FindFirstValue(ClaimTypes.Email) 
                             ?? context.Principal.FindFirstValue("email");

                    if (!string.IsNullOrEmpty(email))
                    {
                        var userRepository = context.HttpContext.RequestServices.GetRequiredService<OptiStudio.Application.Interface.IUserRepository>();
                        var dbUser = await userRepository.GetByEmailAsync(email);

                        if (dbUser != null)
                        {
                            var existingNameIdClaims = identity.FindAll(ClaimTypes.NameIdentifier).ToList();
                            foreach (var claim in existingNameIdClaims)
                            {
                                identity.RemoveClaim(claim);
                            }

                            identity.AddClaim(new Claim(ClaimTypes.Role, dbUser.Role.ToString()));
                            identity.AddClaim(new Claim(ClaimTypes.NameIdentifier, dbUser.Id.ToString()));
                        }
                        else
                        {
                            // User not yet in DB (first login) — resolve role from email config
                            // so [Authorize(Roles=...)] works before /auth/me creates the user
                            var msalAuthService = context.HttpContext.RequestServices.GetRequiredService<OptiStudio.Application.Interface.IMsalAuthService>();
                            var assignedRole = msalAuthService.GetRoleForEmail(email);
                            identity.AddClaim(new Claim(ClaimTypes.Role, assignedRole.ToString()));
                        }
                    }
                }
            }
        };
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
    options.AddPolicy("ArchitectOrAdmin", policy => policy.RequireRole("Admin", "Architect"));
    options.AddPolicy("AllRoles", policy => policy.RequireRole("Admin", "Architect", "Developer"));
});

// CORS for React frontend (both dev ports)
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactApp", policy =>
    {
        policy.WithOrigins(
                  "http://localhost:5173",
                  "http://localhost:3000",
                  "https://proud-mud-0633ce80f.2.azurestaticapps.net")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

var app = builder.Build();

// Seed admin user on first run
await DbInitializer.SeedAsync(app.Services);

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseMiddleware<ExceptionHandlingMiddleware>();

app.UseHttpsRedirection();

app.UseCors("AllowReactApp");

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();
