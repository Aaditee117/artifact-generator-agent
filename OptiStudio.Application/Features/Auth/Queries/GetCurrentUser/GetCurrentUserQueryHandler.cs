using MediatR;
using OptiStudio.Application.DTO.Auth;
using OptiStudio.Application.Interface;

namespace OptiStudio.Application.Features.Auth.Queries.GetCurrentUser;

public class GetCurrentUserQueryHandler : IRequestHandler<GetCurrentUserQuery, AuthResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public GetCurrentUserQueryHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<AuthResponseDto> Handle(GetCurrentUserQuery request, CancellationToken cancellationToken)
    {
        var user = await _unitOfWork.Users.GetByIdAsync(request.UserId);
        if (user == null)
        {
            return new AuthResponseDto { Success = false, Message = "User not found." };
        }

        return new AuthResponseDto
        {
            Success = true,
            Message = "User retrieved successfully.",
            User = new UserDto
            {
                Id = user.Id,
                Name = user.Name,
                Email = user.Email,
                IsEmailVerified = user.IsEmailVerified,
                Role = user.Role.ToString()
            }
        };
    }
}
