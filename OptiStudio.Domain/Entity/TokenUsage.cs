namespace OptiStudio.Domain.Entity;

public class TokenUsage : BaseEntity
{
    public string Feature { get; set; } = string.Empty;
    public string? Action { get; set; }
    public int InputTokens { get; set; }
    public int OutputTokens { get; set; }
    public int TotalTokens { get; set; }
    public string? ModelUsed { get; set; }
    public decimal? EstimatedCost { get; set; }
    public bool IsSuccessful { get; set; } = true;
    public string? ErrorMessage { get; set; }

    public Guid UserId { get; set; }
    public User User { get; set; } = null!;

    public Guid? ChatSessionId { get; set; }
    public ChatSession? ChatSession { get; set; }
}
