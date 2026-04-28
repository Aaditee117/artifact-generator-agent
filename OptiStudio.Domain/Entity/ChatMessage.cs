using OptiStudio.Domain.Enum;

namespace OptiStudio.Domain.Entity;

public class ChatMessage : BaseEntity
{
    public string? Content { get; set; }
    public SenderType SenderType { get; set; } = SenderType.User;

    public Guid ChatSessionId { get; set; }
    public ChatSession ChatSession { get; set; } = null!;

    public Guid? UserId { get; set; }
    public User? User { get; set; }

    public ICollection<Artifact> Artifacts { get; set; } = new List<Artifact>();
}
