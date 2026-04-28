using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Commands.MoveChatSession;

public class MoveChatSessionCommand : IRequest<ChatSessionResponseDto>
{
    public Guid SessionId { get; set; }
    public Guid UserId { get; set; }
    public Guid? ChatGroupId { get; set; }
}
