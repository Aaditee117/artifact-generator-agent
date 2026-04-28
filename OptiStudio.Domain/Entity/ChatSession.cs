namespace OptiStudio.Domain.Entity;

public class ChatSession : BaseEntity
{
    public string Title { get; set; } = "New Chat";

    public Guid UserId { get; set; }
    public User User { get; set; } = null!;

    public Guid? ChatGroupId { get; set; }
    public ChatGroup? ChatGroup { get; set; }

    public ICollection<ChatMessage> Messages { get; set; } = new List<ChatMessage>();
}
