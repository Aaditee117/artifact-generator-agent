using MediatR;
using OptiStudio.Application.DTO.Auth;

namespace OptiStudio.Application.Features.Auth.Queries.GetCurrentUser;

public class GetCurrentUserQuery : IRequest<AuthResponseDto>
{
    public Guid UserId { get; set; }
}
