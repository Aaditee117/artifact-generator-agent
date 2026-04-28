using OptiStudio.Domain.Enum;

namespace OptiStudio.Domain.Entity;

public class PresalesDeck : BaseEntity
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? ClientName { get; set; }
    public string StoragePath { get; set; } = string.Empty;
    public PresalesStatus Status { get; set; } = PresalesStatus.Draft;

    // Approval tracking
    public DateTime? SubmittedAt { get; set; }
    public DateTime? ApprovedAt { get; set; }
    public DateTime? RejectedAt { get; set; }
    public string? RejectionReason { get; set; }
    public string? ApprovalNotes { get; set; }
    public int Version { get; set; } = 1;

    // Creator relationship
    public Guid CreatorId { get; set; }
    public User Creator { get; set; } = null!;

    // Approver relationship (nullable - only set when approved/rejected)
    public Guid? ApproverId { get; set; }
    public User? Approver { get; set; }

    // Project relationship
    public Guid? ProjectId { get; set; }
    public Project? Project { get; set; }

    public Guid? ChatSessionId { get; set; }
    public ChatSession? ChatSession { get; set; }
}
