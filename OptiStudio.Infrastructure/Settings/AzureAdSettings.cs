namespace OptiStudio.Infrastructure.Settings;

/// <summary>
/// Configuration settings for Azure AD / Microsoft Entra ID authentication.
/// </summary>
public class AzureAdSettings
{
    public const string SectionName = "AzureAd";

    /// <summary>
    /// The Azure AD instance (e.g., https://login.microsoftonline.com/).
    /// </summary>
    public string Instance { get; set; } = "https://login.microsoftonline.com/";

    /// <summary>
    /// The Directory (tenant) ID from Azure AD app registration.
    /// </summary>
    public string TenantId { get; set; } = string.Empty;

    /// <summary>
    /// The Application (client) ID from Azure AD app registration.
    /// </summary>
    public string ClientId { get; set; } = string.Empty;

    /// <summary>
    /// The client secret for confidential client authentication (optional for SPA).
    /// </summary>
    public string? ClientSecret { get; set; }

    /// <summary>
    /// The API scope URI for this application.
    /// </summary>
    public string Audience { get; set; } = string.Empty;

    /// <summary>
    /// The redirect URI for the frontend application.
    /// </summary>
    public string FrontendRedirectUri { get; set; } = "http://localhost:5173";

    /// <summary>
    /// Whether to validate the token issuer. Set to false for multi-tenant apps.
    /// </summary>
    public bool ValidateIssuer { get; set; } = true;

    /// <summary>
    /// List of email addresses that should be assigned the Admin role.
    /// </summary>
    public List<string> AdminEmails { get; set; } = new();

    /// <summary>
    /// List of email addresses that should be assigned the Architect role.
    /// </summary>
    public List<string> ArchitectEmails { get; set; } = new();

    /// <summary>
    /// Gets the authority URL combining Instance and TenantId.
    /// </summary>
    public string Authority => $"{Instance.TrimEnd('/')}/{TenantId}";
}
