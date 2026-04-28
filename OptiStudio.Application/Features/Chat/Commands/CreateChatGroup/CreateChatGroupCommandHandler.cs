using MediatR;
using OptiStudio.Application.DTO.Chat;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Features.Chat.Commands.CreateChatGroup;

public class CreateChatGroupCommandHandler : IRequestHandler<CreateChatGroupCommand, ChatGroupResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public CreateChatGroupCommandHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatGroupResponseDto> Handle(CreateChatGroupCommand request, CancellationToken cancellationToken)
    {
        var group = new ChatGroup
        {
            Name = request.Name.Trim(),
            UserId = request.UserId
        };

        await _unitOfWork.ChatGroups.AddAsync(group);
        await _unitOfWork.SaveChangesAsync();

        return new ChatGroupResponseDto
        {
            Success = true,
            Message = "Group created successfully.",
            Group = new ChatGroupDto
            {
                Id = group.Id,
                Name = group.Name,
                CreatedAt = group.CreatedAt,
                SessionCount = 0
            }
        };
    }
}
