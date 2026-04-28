using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Models;

namespace OptiStudio.Application.Features.Chat.Commands.SendChatMessage;

public class SendChatMessageCommand : IRequest<SendMessageResponseDto>
{
    public Guid ChatSessionId { get; set; }
    public Guid UserId { get; set; }
    public string? Content { get; set; }
    public List<FileUploadData> Files { get; set; } = [];
}
