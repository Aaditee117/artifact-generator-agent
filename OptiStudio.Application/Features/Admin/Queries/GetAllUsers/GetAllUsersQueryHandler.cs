using MediatR;
using OptiStudio.Application.DTO.Admin;
using OptiStudio.Application.DTO.Auth;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Admin.Queries.GetAllUsers;

public class GetAllUsersQueryHandler : IRequestHandler<GetAllUsersQuery, UserListResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public GetAllUsersQueryHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<UserListResponseDto> Handle(GetAllUsersQuery request, CancellationToken cancellationToken)
    {
        var users = string.IsNullOrWhiteSpace(request.SearchTerm)
            ? await _unitOfWork.Users.GetAllAsync()
            : await _unitOfWork.Users.SearchAsync(request.SearchTerm);

        var userDtos = users.Select(u => new UserDto
        {
            Id = u.Id,
            Name = u.Name,
            Email = u.Email,
            IsEmailVerified = u.IsEmailVerified,
            Role = u.Role.ToString()
        }).ToList();

        return new UserListResponseDto
        {
            Success = true,
            Message = "Users retrieved successfully.",
            Users = userDtos
        };
    }
}
