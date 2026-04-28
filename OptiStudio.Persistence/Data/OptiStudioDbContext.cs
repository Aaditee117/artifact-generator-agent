using Microsoft.EntityFrameworkCore;
using OptiStudio.Domain.Entity;

namespace OptiStudio.Persistence.Data;

public class OptiStudioDbContext : DbContext
{
    public OptiStudioDbContext(DbContextOptions<OptiStudioDbContext> options) : base(options)
    {
    }

    public DbSet<User> Users => Set<User>();
    public DbSet<OtpRecord> OtpRecords => Set<OtpRecord>();
    public DbSet<RefreshToken> RefreshTokens => Set<RefreshToken>();
    public DbSet<ChatGroup> ChatGroups => Set<ChatGroup>();
    public DbSet<ChatSession> ChatSessions => Set<ChatSession>();
    public DbSet<ChatMessage> ChatMessages => Set<ChatMessage>();
    public DbSet<Artifact> Artifacts => Set<Artifact>();
    public DbSet<PresalesDeck> PresalesDecks => Set<PresalesDeck>();
    public DbSet<TokenUsage> TokenUsages => Set<TokenUsage>();
    public DbSet<Project> Projects => Set<Project>();
    public DbSet<ApiRequestLog> ApiRequestLogs => Set<ApiRequestLog>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(OptiStudioDbContext).Assembly);
    }
}
