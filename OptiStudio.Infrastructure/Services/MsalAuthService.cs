using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Domain.Enum;
using OptiStudio.Infrastructure.Settings;

namespace OptiStudio.Infrastructure.Services;

/// <summary>
/// Service for handling MSAL/Azure AD token operations and user synchronization.
/// </summary>
public class MsalAuthService : IMsalAuthService
{
    private readonly AzureAdSettings _settings;

    public MsalAuthService(IOptions<AzureAdSettings> settings)
    {
        _settings = settings.Value;
    }

    /// <summary>
    /// Extracts user information from Azure AD token claims.
    /// </summary>
    public MsalUserInfo ExtractUserFromToken(ClaimsPrincipal principal)
    {
        var objectId = principal.FindFirstValue("oid") ?? principal.FindFirstValue(ClaimTypes.NameIdentifier);
        var email = principal.FindFirstValue("preferred_username") 
                    ?? principal.FindFirstValue(ClaimTypes.Email) 
                    ?? principal.FindFirstValue("email");
        var name = principal.FindFirstValue("name") ?? principal.FindFirstValue(ClaimTypes.Name);

        // Get roles from Azure AD claims
        var roles = principal.FindAll(ClaimTypes.Role).Select(c => c.Value).ToList();
        var appRoles = principal.FindAll("roles").Select(c => c.Value).ToList();
        roles.AddRange(appRoles);

        // If no roles from Azure AD, determine role based on email configuration
        if (!roles.Any() && !string.IsNullOrEmpty(email))
        {
            var assignedRole = GetRoleForEmail(email);
            roles.Add(assignedRole.ToString());
        }

        return new MsalUserInfo
        {
            ObjectId = objectId ?? string.Empty,
            Email = email ?? string.Empty,
            Name = name ?? string.Empty,
            Roles = roles.Distinct().ToList()
        };
    }

    /// <summary>
    /// Determines the role for a user based on their email address.
    /// Checks AdminEmails and ArchitectEmails configuration.
    /// </summary>
    public Role GetRoleForEmail(string email)
    {
        if (string.IsNullOrEmpty(email))
            return Role.Developer;

        // Check if user is in AdminEmails list (case-insensitive)
        if (_settings.AdminEmails?.Any(e => 
            string.Equals(e, email, StringComparison.OrdinalIgnoreCase)) == true)
        {
            return Role.Admin;
        }

        // Check if user is in ArchitectEmails list (case-insensitive)
        if (_settings.ArchitectEmails?.Any(e => 
            string.Equals(e, email, StringComparison.OrdinalIgnoreCase)) == true)
        {
            return Role.Architect;
        }

        // Default role
        return Role.Developer;
    }

    /// <summary>
    /// Gets the Azure AD Object ID from the claims principal.
    /// </summary>
    public string? GetAzureAdObjectId(ClaimsPrincipal principal)
    {
        return principal.FindFirstValue("oid") ?? principal.FindFirstValue(ClaimTypes.NameIdentifier);
    }

    /// <summary>
    /// Gets the preferred username (email) from the claims principal.
    /// </summary>
    public string? GetUserEmail(ClaimsPrincipal principal)
    {
        return principal.FindFirstValue("preferred_username") 
               ?? principal.FindFirstValue(ClaimTypes.Email) 
               ?? principal.FindFirstValue("email");
    }

    /// <summary>
    /// Gets the display name from the claims principal.
    /// </summary>
    public string? GetUserName(ClaimsPrincipal principal)
    {
        return principal.FindFirstValue("name") ?? principal.FindFirstValue(ClaimTypes.Name);
    }

    /// <summary>
    /// Gets the user's roles from Azure AD app roles.
    /// </summary>
    public IReadOnlyList<string> GetUserRoles(ClaimsPrincipal principal)
    {
        var roles = principal.FindAll(ClaimTypes.Role).Select(c => c.Value).ToList();
        var appRoles = principal.FindAll("roles").Select(c => c.Value).ToList();
        roles.AddRange(appRoles);
        return roles.Distinct().ToList();
    }

    /// <summary>
    /// Validates that the token is from the expected Azure AD tenant.
    /// </summary>
    public bool ValidateTenant(ClaimsPrincipal principal)
    {
        var tid = principal.FindFirstValue("tid");
        return string.Equals(tid, _settings.TenantId, StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>
    /// Gets the Azure AD settings.
    /// </summary>
    public AzureAdSettings GetAzureAdSettings() => _settings;
}
