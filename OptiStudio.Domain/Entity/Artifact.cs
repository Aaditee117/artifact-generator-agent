using OptiStudio.Domain.Enum;

namespace OptiStudio.Domain.Entity;

public class Artifact : BaseEntity
{
    public string? FileName { get; set; }
    public string? FileType { get; set; }
    public ArtifactCategory Category { get; set; }
    public long? FileSizeBytes { get; set; }
    public string? BlobUrl { get; set; }
    public string? StoragePath { get; set; }
    public int Version { get; set; } = 1;

    public Guid ChatMessageId { get; set; }
    public ChatMessage ChatMessage { get; set; } = null!;

    public Guid UploadedByUserId { get; set; }
    public User UploadedByUser { get; set; } = null!;
}
