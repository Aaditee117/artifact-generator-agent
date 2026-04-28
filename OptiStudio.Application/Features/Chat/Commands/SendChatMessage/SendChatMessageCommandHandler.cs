using MediatR;
using OptiStudio.Application.DTO.Artifact;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Domain.Enum;

namespace OptiStudio.Application.Features.Chat.Commands.SendChatMessage;

public class SendChatMessageCommandHandler : IRequestHandler<SendChatMessageCommand, SendMessageResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly IBlobStorageService _blobStorageService;
    private const string ContainerName = "artifacts";

    public SendChatMessageCommandHandler(IUnitOfWork unitOfWork, IBlobStorageService blobStorageService)
    {
        _unitOfWork = unitOfWork;
        _blobStorageService = blobStorageService;
    }

    public async Task<SendMessageResponseDto> Handle(SendChatMessageCommand request, CancellationToken cancellationToken)
    {
        var session = await _unitOfWork.ChatSessions.GetByIdAsync(request.ChatSessionId);
        if (session is null || session.UserId != request.UserId)
            return new SendMessageResponseDto { Success = false, Message = "Session not found." };

        var user = await _unitOfWork.Users.GetByIdAsync(request.UserId);
        if (user is null)
            return new SendMessageResponseDto { Success = false, Message = "User not found." };

        var chatMessage = new ChatMessage
        {
            Content = request.Content?.Trim(),
            SenderType = SenderType.User,
            ChatSessionId = request.ChatSessionId,
            UserId = request.UserId
        };

        await _unitOfWork.ChatMessages.AddAsync(chatMessage);

        var artifactDtos = new List<ArtifactDto>();
        var errors = new List<string>();

        // Build session folder for organized blob storage
        var sessionFolder = BuildSessionFolder(session.Title, session.Id);

        foreach (var file in request.Files)
        {
            try
            {
                var (blobUrl, storagePath) = await _blobStorageService.UploadAsync(
                    file.Stream, file.FileName, file.ContentType, ContainerName, sessionFolder);

                var isSafe = await _blobStorageService.CheckMalwareScanResultAsync(storagePath, ContainerName);
                if (!isSafe)
                {
                    await _blobStorageService.DeleteAsync(storagePath, ContainerName);
                    errors.Add($"'{file.FileName}' was flagged as malicious and rejected.");
                    continue;
                }

                var artifact = new Artifact
                {
                    FileName = file.FileName,
                    FileType = Path.GetExtension(file.FileName).TrimStart('.').ToLowerInvariant(),
                    Category = file.Category,
                    FileSizeBytes = file.Length,
                    BlobUrl = blobUrl,
                    StoragePath = storagePath,
                    Version = 1,
                    ChatMessageId = chatMessage.Id,
                    UploadedByUserId = request.UserId
                };

                await _unitOfWork.Artifacts.AddAsync(artifact);
                artifactDtos.Add(new ArtifactDto
                {
                    Id = artifact.Id,
                    FileName = artifact.FileName,
                    FileType = artifact.FileType,
                    Category = artifact.Category.ToString(),
                    FileSizeBytes = artifact.FileSizeBytes,
                    BlobUrl = artifact.BlobUrl,
                    StoragePath = artifact.StoragePath,  // Include raw storage path
                    Version = artifact.Version,
                    ChatMessageId = artifact.ChatMessageId,
                    UploadedByUserId = artifact.UploadedByUserId,
                    UploadedByUserName = user.Name,
                    CreatedAt = artifact.CreatedAt
                });
            }
            catch (Exception ex)
            {
                errors.Add($"Failed to upload '{file.FileName}': {ex.Message}");
            }
        }

        // Auto-generate title from first message or uploaded file
        if (session.Title == "New Chat")
        {
            if (!string.IsNullOrWhiteSpace(request.Content))
            {
                session.Title = request.Content.Length <= 60
                    ? request.Content.Trim()
                    : request.Content[..60].Trim() + "…";
            }
            else if (request.Files != null && request.Files.Count > 0)
            {
                // Use the first file's name (without extension) as the session title
                var fileName = request.Files[0].FileName;
                var nameWithoutExt = System.IO.Path.GetFileNameWithoutExtension(fileName);
                // Limit to 60 chars for consistency
                session.Title = nameWithoutExt.Length <= 60 ? nameWithoutExt : nameWithoutExt[..60] + "…";
            }
        }

        session.UpdatedAt = DateTime.UtcNow;
        _unitOfWork.ChatSessions.Update(session);
        await _unitOfWork.SaveChangesAsync();

        return new SendMessageResponseDto
        {
            Success = true,
            Message = errors.Count == 0 ? "Message sent." : $"Message sent with {errors.Count} upload error(s).",
            ChatMessage = new ChatMessageDto
            {
                Id = chatMessage.Id,
                Content = chatMessage.Content,
                SenderType = chatMessage.SenderType.ToString(),
                ChatSessionId = chatMessage.ChatSessionId,
                UserId = chatMessage.UserId,
                UserName = user.Name,
                CreatedAt = chatMessage.CreatedAt,
                Artifacts = artifactDtos
            },
            Errors = errors
        };
    }

    private static string BuildSessionFolder(string sessionTitle, Guid sessionId)
    {
        var slug = System.Text.RegularExpressions.Regex.Replace(
            (sessionTitle ?? "untitled").ToLowerInvariant().Trim(), @"[^\w\s-]", "");
        slug = System.Text.RegularExpressions.Regex.Replace(slug, @"[\s_]+", "-");
        slug = System.Text.RegularExpressions.Regex.Replace(slug, @"-+", "-").Trim('-');
        if (slug.Length > 80) slug = slug[..80];
        if (string.IsNullOrEmpty(slug)) slug = "untitled";
        return $"{slug}_{sessionId.ToString()[..8]}";
    }
}
