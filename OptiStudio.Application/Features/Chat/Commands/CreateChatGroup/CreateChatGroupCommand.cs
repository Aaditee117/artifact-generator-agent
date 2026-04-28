using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Commands.CreateChatGroup;

public class CreateChatGroupCommand : IRequest<ChatGroupResponseDto>
{
    public string Name { get; set; } = string.Empty;
    public Guid UserId { get; set; }
}
