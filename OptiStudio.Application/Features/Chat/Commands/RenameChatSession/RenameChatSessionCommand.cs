using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Commands.RenameChatSession;

public class RenameChatSessionCommand : IRequest<ChatSessionResponseDto>
{
    public Guid SessionId { get; set; }
    public Guid UserId { get; set; }
    public string Title { get; set; } = string.Empty;
}
