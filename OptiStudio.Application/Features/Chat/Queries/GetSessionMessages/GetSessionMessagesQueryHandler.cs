using MediatR;
using OptiStudio.Application.DTO.Artifact;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Chat.Queries.GetSessionMessages;

public class GetSessionMessagesQueryHandler : IRequestHandler<GetSessionMessagesQuery, ChatMessageListResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public GetSessionMessagesQueryHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatMessageListResponseDto> Handle(GetSessionMessagesQuery request, CancellationToken cancellationToken)
    {
        var session = await _unitOfWork.ChatSessions.GetByIdAsync(request.SessionId);
        if (session is null || session.UserId != request.UserId)
            return new ChatMessageListResponseDto { Success = false, Message = "Session not found." };

        var messages = await _unitOfWork.ChatMessages.GetBySessionIdAsync(request.SessionId);

        return new ChatMessageListResponseDto
        {
            Success = true,
            Message = "Messages retrieved successfully.",
            Messages = messages.Select(m => new ChatMessageDto
            {
                Id = m.Id,
                Content = m.Content,
                SenderType = m.SenderType.ToString(),
                ChatSessionId = m.ChatSessionId,
                UserId = m.UserId,
                UserName = m.User?.Name,
                CreatedAt = m.CreatedAt,
                Artifacts = m.Artifacts.Select(a => new ArtifactDto
                {
                    Id = a.Id,
                    FileName = a.FileName,
                    FileType = a.FileType,
                    Category = a.Category.ToString(),
                    FileSizeBytes = a.FileSizeBytes,
                    BlobUrl = a.BlobUrl,
                    Version = a.Version,
                    ChatMessageId = a.ChatMessageId,
                    UploadedByUserId = a.UploadedByUserId,
                    UploadedByUserName = a.UploadedByUser?.Name ?? string.Empty,
                    CreatedAt = a.CreatedAt
                }).ToList()
            }).ToList()
        };
    }
}
