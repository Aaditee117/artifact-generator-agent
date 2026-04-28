using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Chat.Queries.GetUserChatGroups;

public class GetUserChatGroupsQueryHandler : IRequestHandler<GetUserChatGroupsQuery, ChatGroupListResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public GetUserChatGroupsQueryHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatGroupListResponseDto> Handle(GetUserChatGroupsQuery request, CancellationToken cancellationToken)
    {
        var groups = await _unitOfWork.ChatGroups.GetByUserIdAsync(request.UserId);

        return new ChatGroupListResponseDto
        {
            Success = true,
            Message = "Groups retrieved successfully.",
            Groups = groups.Select(g => new ChatGroupDto
            {
                Id = g.Id,
                Name = g.Name,
                CreatedAt = g.CreatedAt,
                SessionCount = g.ChatSessions?.Count ?? 0
            }).ToList()
        };
    }
}
