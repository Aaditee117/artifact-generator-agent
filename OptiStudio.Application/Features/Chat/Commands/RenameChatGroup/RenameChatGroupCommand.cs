using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Commands.RenameChatGroup;

public class RenameChatGroupCommand : IRequest<ChatGroupResponseDto>
{
    public Guid GroupId { get; set; }
    public Guid UserId { get; set; }
    public string Name { get; set; } = string.Empty;
}
