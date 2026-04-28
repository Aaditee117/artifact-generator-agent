namespace OptiStudio.Application.DTO.Chat;

public class ChatGroupResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public ChatGroupDto? Group { get; set; }
}

public class ChatGroupListResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<ChatGroupDto> Groups { get; set; } = [];
}

public class ChatGroupDto
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public int SessionCount { get; set; }
}
