using MediatR;
using OptiStudio.Application.DTO.Auth;

namespace OptiStudio.Application.Features.Admin.Commands.UpdateUserRole;

public class UpdateUserRoleCommand : IRequest<AuthResponseDto>
{
    public Guid UserId { get; set; }
    public string Role { get; set; } = string.Empty;
}
