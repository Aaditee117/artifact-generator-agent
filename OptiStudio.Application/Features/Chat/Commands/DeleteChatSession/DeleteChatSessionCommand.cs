using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Commands.DeleteChatSession;

public class DeleteChatSessionCommand : IRequest<ChatSessionResponseDto>
{
    public Guid SessionId { get; set; }
    public Guid UserId { get; set; }
}
