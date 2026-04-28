using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Chat.Commands.DeleteChatGroup;

public class DeleteChatGroupCommandHandler : IRequestHandler<DeleteChatGroupCommand, ChatGroupResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public DeleteChatGroupCommandHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatGroupResponseDto> Handle(DeleteChatGroupCommand request, CancellationToken cancellationToken)
    {
        var group = await _unitOfWork.ChatGroups.GetByIdAsync(request.GroupId);
        if (group is null || group.UserId != request.UserId)
            return new ChatGroupResponseDto { Success = false, Message = "Group not found." };

        // Ungroup all sessions before deleting (NoAction FK requires manual ungrouping)
        var sessions = await _unitOfWork.ChatSessions.GetByUserIdAsync(request.UserId);
        foreach (var session in sessions.Where(s => s.ChatGroupId == request.GroupId))
        {
            session.ChatGroupId = null;
            session.UpdatedAt = DateTime.UtcNow;
            _unitOfWork.ChatSessions.Update(session);
        }

        _unitOfWork.ChatGroups.Remove(group);
        await _unitOfWork.SaveChangesAsync();

        return new ChatGroupResponseDto { Success = true, Message = "Group deleted successfully." };
    }
}
