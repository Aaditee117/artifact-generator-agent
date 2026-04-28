using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using OptiStudio.Application.Interface;
using OptiStudio.Persistence.Data;
using OptiStudio.Persistence.Repository;

namespace OptiStudio.Persistence;

public static class PersistenceServiceRegistration
{
    public static IServiceCollection AddPersistenceServices(this IServiceCollection services, string connectionString)
    {
        services.AddDbContext<OptiStudioDbContext>(options =>
            options.UseSqlServer(connectionString)
                   .ConfigureWarnings(w => w.Ignore(Microsoft.EntityFrameworkCore.Diagnostics.RelationalEventId.PendingModelChangesWarning)));

        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IOtpRepository, OtpRepository>();
        services.AddScoped<IRefreshTokenRepository, RefreshTokenRepository>();
        services.AddScoped<IChatGroupRepository, ChatGroupRepository>();
        services.AddScoped<IChatSessionRepository, ChatSessionRepository>();
        services.AddScoped<IChatMessageRepository, ChatMessageRepository>();
        services.AddScoped<IArtifactRepository, ArtifactRepository>();
        services.AddScoped<IPresalesDeckRepository, PresalesDeckRepository>();
        services.AddScoped<ITokenUsageRepository, TokenUsageRepository>();
        services.AddScoped<IUnitOfWork, UnitOfWork>();

        return services;
    }
}
