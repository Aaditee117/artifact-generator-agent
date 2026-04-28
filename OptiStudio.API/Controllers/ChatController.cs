using System.Security.Claims;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using OptiStudio.Application.Features.Chat.Commands.CreateChatGroup;
using OptiStudio.Application.Features.Chat.Commands.CreateChatSession;
using OptiStudio.Application.Features.Chat.Commands.DeleteChatGroup;
using OptiStudio.Application.Features.Chat.Commands.DeleteChatSession;
using OptiStudio.Application.Features.Chat.Commands.MoveChatSession;
using OptiStudio.Application.Features.Chat.Commands.RenameChatGroup;
using OptiStudio.Application.Features.Chat.Commands.RenameChatSession;
using OptiStudio.Application.Features.Chat.Commands.SendChatMessage;
using OptiStudio.Application.Features.Chat.Queries.GetSessionMessages;
using OptiStudio.Application.Features.Chat.Queries.GetUserChatGroups;
using OptiStudio.Application.Features.Chat.Queries.GetUserChatSessions;
using OptiStudio.Application.Interface;
using OptiStudio.Application.Models;
using OptiStudio.Domain.Enum;

namespace OptiStudio.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize(Policy = "ArchitectOrAdmin")]
public class ChatController : ControllerBase
{
    private readonly IMediator _mediator;
    private readonly IUnitOfWork _unitOfWork;
    private readonly IBlobStorageService _blobStorageService;
    private const string ContainerName = "artifacts";

    public ChatController(IMediator mediator, IUnitOfWork unitOfWork, IBlobStorageService blobStorageService)
    {
        _mediator = mediator;
        _unitOfWork = unitOfWork;
        _blobStorageService = blobStorageService;
    }

    private Guid GetUserId() => Guid.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);

    // ── Sessions ──────────────────────────────────────────────

    [HttpPost("sessions")]
    public async Task<IActionResult> CreateSession([FromBody] CreateChatSessionRequest dto)
    {
        var result = await _mediator.Send(new CreateChatSessionCommand
        {
            UserId = GetUserId(),
            ChatGroupId = dto.ChatGroupId
        });
        return result.Success ? Ok(result) : BadRequest(result);
    }

    [HttpGet("sessions")]
    public async Task<IActionResult> GetSessions()
    {
        var result = await _mediator.Send(new GetUserChatSessionsQuery { UserId = GetUserId() });
        return Ok(result);
    }

    [HttpPut("sessions/{id}/rename")]
    public async Task<IActionResult> RenameSession(Guid id, [FromBody] RenameRequest dto)
    {
        var result = await _mediator.Send(new RenameChatSessionCommand
        {
            SessionId = id,
            UserId = GetUserId(),
            Title = dto.Name
        });
        return result.Success ? Ok(result) : BadRequest(result);
    }

    [HttpPut("sessions/{id}/move")]
    public async Task<IActionResult> MoveSession(Guid id, [FromBody] MoveSessionRequest dto)
    {
        var result = await _mediator.Send(new MoveChatSessionCommand
        {
            SessionId = id,
            UserId = GetUserId(),
            ChatGroupId = dto.ChatGroupId
        });
        return result.Success ? Ok(result) : BadRequest(result);
    }

    [HttpDelete("sessions/{id}")]
    public async Task<IActionResult> DeleteSession(Guid id)
    {
        var result = await _mediator.Send(new DeleteChatSessionCommand { SessionId = id, UserId = GetUserId() });
        return result.Success ? Ok(result) : BadRequest(result);
    }

    // ── Messages ──────────────────────────────────────────────

    [HttpPost("sessions/{sessionId}/messages")]
    [RequestSizeLimit(50 * 1024 * 1024)]
    public async Task<IActionResult> SendMessage(Guid sessionId,
        [FromForm] string? content,
        [FromForm] List<IFormFile>? files,
        [FromForm] string? categories)
    {
        var command = new SendChatMessageCommand
        {
            ChatSessionId = sessionId,
            UserId = GetUserId(),
            Content = content
        };

        var categoryList = categories?.Split(',', StringSplitOptions.TrimEntries) ?? [];

        if (files is not null)
        {
            for (var i = 0; i < files.Count; i++)
            {
                var file = files[i];
                var category = ArtifactCategory.Document;
                if (i < categoryList.Length &&
                    Enum.TryParse<ArtifactCategory>(categoryList[i], true, out var parsed))
                    category = parsed;

                command.Files.Add(new FileUploadData
                {
                    FileName = file.FileName,
                    ContentType = file.ContentType,
                    Length = file.Length,
                    Stream = file.OpenReadStream(),
                    Category = category
                });
            }
        }

        var result = await _mediator.Send(command);

        foreach (var f in command.Files)
            await f.Stream.DisposeAsync();

        return result.Success ? Ok(result) : BadRequest(result);
    }

    [HttpGet("sessions/{sessionId}/messages")]
    public async Task<IActionResult> GetMessages(Guid sessionId)
    {
        var result = await _mediator.Send(new GetSessionMessagesQuery
        {
            SessionId = sessionId,
            UserId = GetUserId()
        });
        return result.Success ? Ok(result) : NotFound(result);
    }

    // ── Groups ────────────────────────────────────────────────

    [HttpPost("groups")]
    public async Task<IActionResult> CreateGroup([FromBody] RenameRequest dto)
    {
        var result = await _mediator.Send(new CreateChatGroupCommand { Name = dto.Name, UserId = GetUserId() });
        return result.Success ? Ok(result) : BadRequest(result);
    }

    [HttpGet("groups")]
    public async Task<IActionResult> GetGroups()
    {
        var result = await _mediator.Send(new GetUserChatGroupsQuery { UserId = GetUserId() });
        return Ok(result);
    }

    [HttpPut("groups/{id}")]
    public async Task<IActionResult> RenameGroup(Guid id, [FromBody] RenameRequest dto)
    {
        var result = await _mediator.Send(new RenameChatGroupCommand { GroupId = id, UserId = GetUserId(), Name = dto.Name });
        return result.Success ? Ok(result) : BadRequest(result);
    }

    [HttpDelete("groups/{id}")]
    public async Task<IActionResult> DeleteGroup(Guid id)
    {
        var result = await _mediator.Send(new DeleteChatGroupCommand { GroupId = id, UserId = GetUserId() });
        return result.Success ? Ok(result) : BadRequest(result);
    }

    // ── Artifact Download ─────────────────────────────────────

    [HttpGet("artifacts/{artifactId}/url")]
    public async Task<IActionResult> GetArtifactDownloadUrl(Guid artifactId)
    {
        var artifact = await _unitOfWork.Artifacts.GetByIdAsync(artifactId);
        if (artifact is null)
            return NotFound(new { Success = false, Message = "Artifact not found." });

        if (string.IsNullOrEmpty(artifact.StoragePath))
            return BadRequest(new { Success = false, Message = "No file associated with this artifact." });

        var sasUrl = await _blobStorageService.GenerateSasUrlAsync(artifact.StoragePath, ContainerName);
        return Ok(new { Success = true, Url = sasUrl, FileName = artifact.FileName });
    }
}

// ── Request DTOs ──────────────────────────────────────────────
public record RenameRequest(string Name);
public record CreateChatSessionRequest(Guid? ChatGroupId);
public record MoveSessionRequest(Guid? ChatGroupId);
