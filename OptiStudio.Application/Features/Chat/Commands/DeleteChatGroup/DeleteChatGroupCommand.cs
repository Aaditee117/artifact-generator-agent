using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Commands.DeleteChatGroup;

public class DeleteChatGroupCommand : IRequest<ChatGroupResponseDto>
{
    public Guid GroupId { get; set; }
    public Guid UserId { get; set; }
}
