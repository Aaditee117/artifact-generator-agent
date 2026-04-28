using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Features.Chat.Commands.CreateChatSession;

public class CreateChatSessionCommandHandler : IRequestHandler<CreateChatSessionCommand, ChatSessionResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public CreateChatSessionCommandHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatSessionResponseDto> Handle(CreateChatSessionCommand request, CancellationToken cancellationToken)
    {
        if (request.ChatGroupId.HasValue)
        {
            var group = await _unitOfWork.ChatGroups.GetByIdAsync(request.ChatGroupId.Value);
            if (group is null || group.UserId != request.UserId)
                return new ChatSessionResponseDto { Success = false, Message = "Group not found." };
        }

        var session = new ChatSession
        {
            Title = "New Chat",
            UserId = request.UserId,
            ChatGroupId = request.ChatGroupId
        };

        await _unitOfWork.ChatSessions.AddAsync(session);
        await _unitOfWork.SaveChangesAsync();

        return new ChatSessionResponseDto
        {
            Success = true,
            Message = "Chat session created successfully.",
            Session = new ChatSessionDto
            {
                Id = session.Id,
                Title = session.Title,
                ChatGroupId = session.ChatGroupId,
                CreatedAt = session.CreatedAt
            }
        };
    }
}
