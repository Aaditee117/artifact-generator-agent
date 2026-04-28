namespace OptiStudio.Application.DTO.Chat;

public class ChatSessionResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public ChatSessionDto? Session { get; set; }
}

public class ChatSessionListResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<ChatSessionDto> Sessions { get; set; } = [];
}

public class ChatSessionDto
{
    public Guid Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public Guid? ChatGroupId { get; set; }
    public string? ChatGroupName { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
    public string? LastMessagePreview { get; set; }
}
