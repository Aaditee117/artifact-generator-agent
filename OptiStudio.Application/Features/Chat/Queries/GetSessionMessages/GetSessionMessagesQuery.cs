using MediatR;
using OptiStudio.Application.DTO.Chat;

namespace OptiStudio.Application.Features.Chat.Queries.GetSessionMessages;

public class GetSessionMessagesQuery : IRequest<ChatMessageListResponseDto>
{
    public Guid SessionId { get; set; }
    public Guid UserId { get; set; }
}
