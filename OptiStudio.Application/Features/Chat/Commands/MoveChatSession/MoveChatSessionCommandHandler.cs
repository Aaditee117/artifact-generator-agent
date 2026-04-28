using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Chat.Commands.MoveChatSession;

public class MoveChatSessionCommandHandler : IRequestHandler<MoveChatSessionCommand, ChatSessionResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public MoveChatSessionCommandHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatSessionResponseDto> Handle(MoveChatSessionCommand request, CancellationToken cancellationToken)
    {
        var session = await _unitOfWork.ChatSessions.GetByIdAsync(request.SessionId);
        if (session is null || session.UserId != request.UserId)
            return new ChatSessionResponseDto { Success = false, Message = "Session not found." };

        if (request.ChatGroupId.HasValue)
        {
            var group = await _unitOfWork.ChatGroups.GetByIdAsync(request.ChatGroupId.Value);
            if (group is null || group.UserId != request.UserId)
                return new ChatSessionResponseDto { Success = false, Message = "Group not found." };
        }

        session.ChatGroupId = request.ChatGroupId;
        session.UpdatedAt = DateTime.UtcNow;
        _unitOfWork.ChatSessions.Update(session);
        await _unitOfWork.SaveChangesAsync();

        return new ChatSessionResponseDto
        {
            Success = true,
            Message = "Session moved successfully.",
            Session = new ChatSessionDto
            {
                Id = session.Id,
                Title = session.Title,
                ChatGroupId = session.ChatGroupId,
                CreatedAt = session.CreatedAt,
                UpdatedAt = session.UpdatedAt
            }
        };
    }
}
