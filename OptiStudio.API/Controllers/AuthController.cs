using System.Security.Claims;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using OptiStudio.Application.DTO.Auth;
using OptiStudio.Application.Features.Auth.Queries.GetCurrentUser;
using OptiStudio.Application.Interface;
using OptiStudio.Infrastructure.Settings;
using Microsoft.Extensions.Options;

namespace OptiStudio.API.Controllers;

/// <summary>
/// Authentication controller for MSAL/Azure AD authentication.
/// Login is handled by the frontend via MSAL.js redirect to Azure AD.
/// This controller provides endpoints for user info and session management.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly IMediator _mediator;
    private readonly IMsalAuthService _msalAuthService;
    private readonly IUserRepository _userRepository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly AzureAdSettings _azureAdSettings;
    private readonly ILogger<AuthController> _logger;

    public AuthController(
        IMediator mediator,
        IMsalAuthService msalAuthService,
        IUserRepository userRepository,
        IUnitOfWork unitOfWork,
        IOptions<AzureAdSettings> azureAdSettings,
        ILogger<AuthController> logger)
    {
        _mediator = mediator;
        _msalAuthService = msalAuthService;
        _userRepository = userRepository;
        _unitOfWork = unitOfWork;
        _azureAdSettings = azureAdSettings.Value;
        _logger = logger;
    }

    /// <summary>
    /// Gets the current authenticated user's information from Azure AD token.
    /// Checks database first for role, falls back to config-based role assignment.
    /// Creates user in database if they don't exist.
    /// </summary>
    [Authorize]
    [HttpGet("me")]
    public async Task<IActionResult> GetCurrentUser()
    {
        var userInfo = _msalAuthService.ExtractUserFromToken(User);

        _logger.LogInformation("[Auth] GetCurrentUser called for email: {Email}, ObjectId: {ObjectId}", 
            userInfo.Email, userInfo.ObjectId);

        if (string.IsNullOrEmpty(userInfo.ObjectId))
        {
            _logger.LogWarning("[Auth] Invalid token - ObjectId is empty");
            return Unauthorized(new AuthResponseDto { Success = false, Message = "Invalid token." });
        }

        if (string.IsNullOrEmpty(userInfo.Email))
        {
            _logger.LogWarning("[Auth] Invalid token - Email is empty");
            return Unauthorized(new AuthResponseDto { Success = false, Message = "Email not found in token." });
        }

        // First, check if user exists in database and get their role
        var dbUser = await _userRepository.GetByEmailAsync(userInfo.Email);

        string role;
        Guid userId;

        if (dbUser != null)
        {
            // User exists in database - use their database role
            _logger.LogInformation("[Auth] User found in database: {Email}, Role: {Role}", dbUser.Email, dbUser.Role);
            role = dbUser.Role.ToString();
            userId = dbUser.Id;
        }
        else
        {
            // User not in database - compute assigned initial role and CREATE the user
            _logger.LogInformation("[Auth] User NOT found in database, creating new user: {Email}", userInfo.Email);

            var initialRole = _msalAuthService.GetRoleForEmail(userInfo.Email);
            role = initialRole.ToString();

            _logger.LogInformation("[Auth] Assigned role for new user {Email}: {Role}", userInfo.Email, role);

            // Insert MSAL logged-in user to database for admin management
            var newUser = new OptiStudio.Domain.Entity.User
            {
                Id = Guid.NewGuid(),
                Name = userInfo.Name ?? userInfo.Email.Split('@')[0], // Fallback to email prefix if name is empty
                Email = userInfo.Email,
                Role = initialRole,
                IsEmailVerified = true,
                PasswordHash = "MSAL_EXTERNAL", // Mark as external auth user
                CreatedAt = DateTime.UtcNow
            };

            try
            {
                await _userRepository.AddAsync(newUser);
                var savedCount = await _unitOfWork.SaveChangesAsync();

                _logger.LogInformation("[Auth] Successfully created user {Email} in database. Saved {Count} changes.", 
                    userInfo.Email, savedCount);

                userId = newUser.Id;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "[Auth] Failed to create user {Email} in database", userInfo.Email);

                // Try to fetch again in case of race condition (user was created by another request)
                dbUser = await _userRepository.GetByEmailAsync(userInfo.Email);
                if (dbUser != null)
                {
                    _logger.LogInformation("[Auth] User {Email} found after retry (race condition)", userInfo.Email);
                    role = dbUser.Role.ToString();
                    userId = dbUser.Id;
                }
                else
                {
                    throw; // Re-throw if still no user
                }
            }
        }

        // Return user info
        return Ok(new AuthResponseDto
        {
            Success = true,
            Message = "User authenticated via Azure AD.",
            User = new UserDto
            {
                Id = userId,
                Name = userInfo.Name ?? userInfo.Email.Split('@')[0],
                Email = userInfo.Email,
                IsEmailVerified = true, // Azure AD users are verified
                Role = role
            }
        });
    }

    /// <summary>
    /// Validates the Azure AD token and returns user claims.
    /// Used by frontend to verify token validity.
    /// </summary>
    [Authorize]
    [HttpGet("validate")]
    public IActionResult ValidateToken()
    {
        var userInfo = _msalAuthService.ExtractUserFromToken(User);

        if (string.IsNullOrEmpty(userInfo.ObjectId))
        {
            return Unauthorized(new { valid = false, message = "Invalid token." });
        }

        return Ok(new
        {
            valid = true,
            objectId = userInfo.ObjectId,
            email = userInfo.Email,
            name = userInfo.Name,
            roles = userInfo.Roles
        });
    }

    /// <summary>
    /// Logout endpoint - clears any server-side session data.
    /// Note: MSAL logout is primarily handled on the frontend by clearing the token cache.
    /// </summary>
    [Authorize]
    [HttpPost("logout")]
    public IActionResult Logout()
    {
        // With MSAL, logout is primarily handled on the frontend
        // This endpoint can be used for any server-side cleanup if needed
        return Ok(new { success = true, message = "Logout successful. Please clear your local session." });
    }

    /// <summary>
    /// Returns Azure AD configuration for the frontend MSAL setup.
    /// This endpoint does not require authentication.
    /// </summary>
    [HttpGet("config")]
    public IActionResult GetAuthConfig()
    {
        // Return only the client-side configuration (no secrets)
        return Ok(new
        {
            clientId = _azureAdSettings.ClientId,
            authority = $"https://login.microsoftonline.com/{_azureAdSettings.TenantId}",
            redirectUri = "http://localhost:5173",
            scopes = new[] { $"api://{_azureAdSettings.ClientId}/.default" }
        });
    }

    /// <summary>
    /// Debug endpoint to check role assignment for an email.
    /// Remove in production.
    /// </summary>
    [HttpGet("debug/role/{email}")]
    public async Task<IActionResult> DebugGetRole(string email)
    {
        var configRole = _msalAuthService.GetRoleForEmail(email);
        var dbUser = await _userRepository.GetByEmailAsync(email);

        object databaseUserInfo;
        if (dbUser != null)
        {
            databaseUserInfo = new 
            { 
                found = true,
                email = dbUser.Email,
                role = dbUser.Role.ToString(),
                id = dbUser.Id.ToString()
            };
        }
        else
        {
            databaseUserInfo = new 
            { 
                found = false,
                email = (string?)null,
                role = (string?)null,
                id = (string?)null
            };
        }

        return Ok(new
        {
            inputEmail = email,
            databaseUser = databaseUserInfo,
            configRole = configRole.ToString(),
            adminEmails = _azureAdSettings.AdminEmails,
            architectEmails = _azureAdSettings.ArchitectEmails
        });
    }
}
