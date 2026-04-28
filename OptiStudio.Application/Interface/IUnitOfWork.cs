namespace OptiStudio.Application.Interface;

public interface IUnitOfWork
{
    IUserRepository Users { get; }
    IOtpRepository Otps { get; }
    IRefreshTokenRepository RefreshTokens { get; }
    IChatGroupRepository ChatGroups { get; }
    IChatSessionRepository ChatSessions { get; }
    IChatMessageRepository ChatMessages { get; }
    IArtifactRepository Artifacts { get; }
    IPresalesDeckRepository PresalesDecks { get; }
    ITokenUsageRepository TokenUsages { get; }
    Task<int> SaveChangesAsync();
}
