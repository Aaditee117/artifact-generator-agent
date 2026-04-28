using OptiStudio.Application.DTO.Artifact;

namespace OptiStudio.Application.DTO.Chat;

public class SendMessageResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public ChatMessageDto? ChatMessage { get; set; }
    public List<string> Errors { get; set; } = [];
}

public class ChatMessageListResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<ChatMessageDto> Messages { get; set; } = [];
}

public class ChatMessageDto
{
    public Guid Id { get; set; }
    public string? Content { get; set; }
    public string SenderType { get; set; } = string.Empty;
    public Guid ChatSessionId { get; set; }
    public Guid? UserId { get; set; }
    public string? UserName { get; set; }
    public DateTime CreatedAt { get; set; }
    public List<ArtifactDto> Artifacts { get; set; } = [];
}
