namespace OptiStudio.Application.DTO.Artifact;

public class ArtifactResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public ArtifactDto? Artifact { get; set; }
}

public class ArtifactListResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<ArtifactDto> Artifacts { get; set; } = [];
}

public class UploadArtifactsResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<ArtifactDto> UploadedArtifacts { get; set; } = [];
    public List<string> Errors { get; set; } = [];
}

public class ArtifactDto
{
    public Guid Id { get; set; }
    public string? FileName { get; set; }
    public string? FileType { get; set; }
    public string Category { get; set; } = string.Empty;
    public long? FileSizeBytes { get; set; }
    public string? BlobUrl { get; set; }
    public string? StoragePath { get; set; }  // Raw storage path without URL encoding
    public int Version { get; set; }
    public Guid ChatMessageId { get; set; }
    public Guid UploadedByUserId { get; set; }
    public string UploadedByUserName { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
}
