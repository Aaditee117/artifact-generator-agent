using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Chat.Queries.GetUserChatSessions;

public class GetUserChatSessionsQueryHandler : IRequestHandler<GetUserChatSessionsQuery, ChatSessionListResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public GetUserChatSessionsQueryHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatSessionListResponseDto> Handle(GetUserChatSessionsQuery request, CancellationToken cancellationToken)
    {
        var sessions = await _unitOfWork.ChatSessions.GetByUserIdAsync(request.UserId);

        return new ChatSessionListResponseDto
        {
            Success = true,
            Message = "Sessions retrieved successfully.",
            Sessions = sessions.Select(s => new ChatSessionDto
            {
                Id = s.Id,
                Title = s.Title,
                ChatGroupId = s.ChatGroupId,
                ChatGroupName = s.ChatGroup?.Name,
                CreatedAt = s.CreatedAt,
                UpdatedAt = s.UpdatedAt,
                LastMessagePreview = s.Messages
                    .OrderByDescending(m => m.CreatedAt)
                    .FirstOrDefault()?.Content?
                    .Substring(0, Math.Min(60, s.Messages.OrderByDescending(m => m.CreatedAt).First().Content?.Length ?? 0))
            }).ToList()
        };
    }
}
