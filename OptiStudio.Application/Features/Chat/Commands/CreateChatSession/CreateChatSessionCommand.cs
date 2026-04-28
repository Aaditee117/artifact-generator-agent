using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Commands.CreateChatSession;

public class CreateChatSessionCommand : IRequest<ChatSessionResponseDto>
{
    public Guid UserId { get; set; }
    public Guid? ChatGroupId { get; set; }
}
