using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Queries.GetUserChatSessions;

public class GetUserChatSessionsQuery : IRequest<ChatSessionListResponseDto>
{
    public Guid UserId { get; set; }
}
