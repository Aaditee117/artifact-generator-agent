namespace OptiStudio.Domain.Entity;

public class ChatGroup : BaseEntity
{
    public string Name { get; set; } = string.Empty;

    public Guid UserId { get; set; }
    public User User { get; set; } = null!;

    public ICollection<ChatSession> ChatSessions { get; set; } = new List<ChatSession>();
}
