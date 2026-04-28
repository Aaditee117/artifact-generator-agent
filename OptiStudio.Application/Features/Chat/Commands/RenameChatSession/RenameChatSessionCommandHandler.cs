using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Chat.Commands.RenameChatSession;

public class RenameChatSessionCommandHandler : IRequestHandler<RenameChatSessionCommand, ChatSessionResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public RenameChatSessionCommandHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatSessionResponseDto> Handle(RenameChatSessionCommand request, CancellationToken cancellationToken)
    {
        var session = await _unitOfWork.ChatSessions.GetByIdAsync(request.SessionId);
        if (session is null || session.UserId != request.UserId)
            return new ChatSessionResponseDto { Success = false, Message = "Session not found." };

        session.Title = request.Title.Trim();
        session.UpdatedAt = DateTime.UtcNow;
        _unitOfWork.ChatSessions.Update(session);
        await _unitOfWork.SaveChangesAsync();

        return new ChatSessionResponseDto
        {
            Success = true,
            Message = "Session renamed successfully.",
            Session = new ChatSessionDto
            {
                Id = session.Id,
                Title = session.Title,
                ChatGroupId = session.ChatGroupId,
                ChatGroupName = session.ChatGroup?.Name,
                CreatedAt = session.CreatedAt,
                UpdatedAt = session.UpdatedAt
            }
        };
    }
}
