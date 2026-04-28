using System.Security.Claims;
using OptiStudio.Domain.Enum;

namespace OptiStudio.Application.Interface;

/// <summary>
/// Interface for MSAL/Azure AD authentication service.
/// </summary>
public interface IMsalAuthService
{
    /// <summary>
    /// Extracts user information from Azure AD token claims.
    /// </summary>
    MsalUserInfo ExtractUserFromToken(ClaimsPrincipal principal);

    /// <summary>
    /// Gets the Azure AD Object ID from the claims principal.
    /// </summary>
    string? GetAzureAdObjectId(ClaimsPrincipal principal);

    /// <summary>
    /// Gets the preferred username (email) from the claims principal.
    /// </summary>
    string? GetUserEmail(ClaimsPrincipal principal);

    /// <summary>
    /// Gets the display name from the claims principal.
    /// </summary>
    string? GetUserName(ClaimsPrincipal principal);

    /// <summary>
    /// Gets the user's roles from Azure AD app roles.
    /// </summary>
    IReadOnlyList<string> GetUserRoles(ClaimsPrincipal principal);

    /// <summary>
    /// Validates that the token is from the expected Azure AD tenant.
    /// </summary>
    bool ValidateTenant(ClaimsPrincipal principal);

    /// <summary>
    /// Determines the role for a user based on their email address.
    /// Checks AdminEmails and ArchitectEmails configuration.
    /// </summary>
    Role GetRoleForEmail(string email);
}

/// <summary>
/// User information extracted from Azure AD token.
/// </summary>
public class MsalUserInfo
{
    public string ObjectId { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public List<string> Roles { get; set; } = new();
}
