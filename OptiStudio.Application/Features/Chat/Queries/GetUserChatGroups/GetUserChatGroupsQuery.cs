using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Queries.GetUserChatGroups;

public class GetUserChatGroupsQuery : IRequest<ChatGroupListResponseDto>
{
    public Guid UserId { get; set; }
}
