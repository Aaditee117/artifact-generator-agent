using OptiStudio.Domain.Enum;

namespace OptiStudio.Domain.Entity;

public class User : BaseEntity
{
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
    public bool IsEmailVerified { get; set; }
    public Role Role { get; set; } = Role.Developer;

    public ICollection<OtpRecord> OtpRecords { get; set; } = new List<OtpRecord>();
    public ICollection<RefreshToken> RefreshTokens { get; set; } = new List<RefreshToken>();
    public ICollection<ChatGroup> ChatGroups { get; set; } = new List<ChatGroup>();
    public ICollection<ChatSession> ChatSessions { get; set; } = new List<ChatSession>();
    public ICollection<ChatMessage> ChatMessages { get; set; } = new List<ChatMessage>();
    public ICollection<Artifact> UploadedArtifacts { get; set; } = new List<Artifact>();
    public ICollection<PresalesDeck> PresalesDecks { get; set; } = new List<PresalesDeck>();
    public ICollection<TokenUsage> TokenUsages { get; set; } = new List<TokenUsage>();
}
