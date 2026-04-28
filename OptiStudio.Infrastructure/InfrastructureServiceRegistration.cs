using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using OptiStudio.Application.Interface;
using OptiStudio.Infrastructure.Services;
using OptiStudio.Infrastructure.Settings;

namespace OptiStudio.Infrastructure;

public static class InfrastructureServiceRegistration
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
    {
        // Azure AD / MSAL settings
        services.Configure<AzureAdSettings>(configuration.GetSection(AzureAdSettings.SectionName));

        services.Configure<SmtpSettings>(configuration.GetSection("SmtpSettings"));
        services.Configure<AzureBlobSettings>(configuration.GetSection("AzureBlobSettings"));

        // MSAL Authentication Service
        services.AddScoped<IMsalAuthService, MsalAuthService>();

        services.AddScoped<IEmailService, EmailService>();
        services.AddScoped<IPasswordHasher, PasswordHasher>();
        services.AddScoped<IBlobStorageService, BlobStorageService>();

        return services;
    }
}
