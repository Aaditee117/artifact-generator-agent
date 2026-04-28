using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Chat.Commands.DeleteChatSession;

public class DeleteChatSessionCommandHandler : IRequestHandler<DeleteChatSessionCommand, ChatSessionResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public DeleteChatSessionCommandHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatSessionResponseDto> Handle(DeleteChatSessionCommand request, CancellationToken cancellationToken)
    {
        var session = await _unitOfWork.ChatSessions.GetByIdAsync(request.SessionId);
        if (session is null || session.UserId != request.UserId)
            return new ChatSessionResponseDto { Success = false, Message = "Session not found." };

        _unitOfWork.ChatSessions.Remove(session);
        await _unitOfWork.SaveChangesAsync();

        return new ChatSessionResponseDto { Success = true, Message = "Session deleted successfully." };
    }
}
