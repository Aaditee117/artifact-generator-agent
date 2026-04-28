namespace OptiStudio.Domain.Entity;

public class OtpRecord : BaseEntity
{
    public Guid UserId { get; set; }
    public string Code { get; set; } = string.Empty;
    public DateTime ExpiresAt { get; set; }
    public bool IsUsed { get; set; }

    public User User { get; set; } = null!;
}
