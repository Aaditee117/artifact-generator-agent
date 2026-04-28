using MediatR;
using OptiStudio.Application.DTO.Admin;

namespace OptiStudio.Application.Features.Admin.Queries.GetAllUsers;

public class GetAllUsersQuery : IRequest<UserListResponseDto>
{
    public string? SearchTerm { get; set; }
}
