using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Chat.Commands.RenameChatGroup;

public class RenameChatGroupCommandHandler : IRequestHandler<RenameChatGroupCommand, ChatGroupResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public RenameChatGroupCommandHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatGroupResponseDto> Handle(RenameChatGroupCommand request, CancellationToken cancellationToken)
    {
        var group = await _unitOfWork.ChatGroups.GetByIdAsync(request.GroupId);
        if (group is null || group.UserId != request.UserId)
            return new ChatGroupResponseDto { Success = false, Message = "Group not found." };

        group.Name = request.Name.Trim();
        group.UpdatedAt = DateTime.UtcNow;
        _unitOfWork.ChatGroups.Update(group);
        await _unitOfWork.SaveChangesAsync();

        return new ChatGroupResponseDto
        {
            Success = true,
            Message = "Group renamed successfully.",
            Group = new ChatGroupDto
            {
                Id = group.Id,
                Name = group.Name,
                CreatedAt = group.CreatedAt,
                SessionCount = group.ChatSessions?.Count ?? 0
            }
        };
    }
}
