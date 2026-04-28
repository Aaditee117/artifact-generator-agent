using OptiStudio.Application.Interface;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class UnitOfWork : IUnitOfWork
{
    private readonly OptiStudioDbContext _context;

    public IUserRepository Users { get; }
    public IOtpRepository Otps { get; }
    public IRefreshTokenRepository RefreshTokens { get; }
    public IChatGroupRepository ChatGroups { get; }
    public IChatSessionRepository ChatSessions { get; }
    public IChatMessageRepository ChatMessages { get; }
    public IArtifactRepository Artifacts { get; }
    public IPresalesDeckRepository PresalesDecks { get; }
    public ITokenUsageRepository TokenUsages { get; }

    public UnitOfWork(OptiStudioDbContext context,
        IUserRepository users,
        IOtpRepository otps,
        IRefreshTokenRepository refreshTokens,
        IChatGroupRepository chatGroups,
        IChatSessionRepository chatSessions,
        IChatMessageRepository chatMessages,
        IArtifactRepository artifacts,
        IPresalesDeckRepository presalesDecks,
        ITokenUsageRepository tokenUsages)
    {
        _context = context;
        Users = users;
        Otps = otps;
        RefreshTokens = refreshTokens;
        ChatGroups = chatGroups;
        ChatSessions = chatSessions;
        ChatMessages = chatMessages;
        Artifacts = artifacts;
        PresalesDecks = presalesDecks;
        TokenUsages = tokenUsages;
    }

    public async Task<int> SaveChangesAsync()
    {
        return await _context.SaveChangesAsync();
    }
}
