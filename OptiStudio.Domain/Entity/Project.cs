using OptiStudio.Domain.Enum;

namespace OptiStudio.Domain.Entity;

public class Project : BaseEntity
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? ClientName { get; set; }
    public ProjectStatus Status { get; set; } = ProjectStatus.Discovery;
    public ProjectPhase Phase { get; set; } = ProjectPhase.PreSales;
    
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public decimal? EstimatedBudget { get; set; }
    public string? TechStack { get; set; }
    public string? Notes { get; set; }

    // Owner/Lead
    public Guid OwnerId { get; set; }
    public User Owner { get; set; } = null!;

    // Related presales decks
    public ICollection<PresalesDeck> PresalesDecks { get; set; } = new List<PresalesDeck>();
    
    // Related chat sessions for this project
    public ICollection<ChatSession> ChatSessions { get; set; } = new List<ChatSession>();
}
