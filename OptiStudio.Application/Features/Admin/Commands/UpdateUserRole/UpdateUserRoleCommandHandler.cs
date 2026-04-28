using MediatR;
using OptiStudio.Application.DTO.Auth;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Enum;

namespace OptiStudio.Application.Features.Admin.Commands.UpdateUserRole;

public class UpdateUserRoleCommandHandler : IRequestHandler<UpdateUserRoleCommand, AuthResponseDto>
{
    private readonly IUnitOfWork _unitOfWork;

    public UpdateUserRoleCommandHandler(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    public async Task<AuthResponseDto> Handle(UpdateUserRoleCommand request, CancellationToken cancellationToken)
    {
        var user = await _unitOfWork.Users.GetByIdAsync(request.UserId);
        if (user == null)
        {
            return new AuthResponseDto { Success = false, Message = "User not found." };
        }

        if (!System.Enum.TryParse<Role>(request.Role, ignoreCase: true, out var newRole))
        {
            return new AuthResponseDto { Success = false, Message = "Invalid role. Valid roles: Admin, Architect, Developer." };
        }

        user.Role = newRole;
        user.UpdatedAt = DateTime.UtcNow;
        _unitOfWork.Users.Update(user);
        await _unitOfWork.SaveChangesAsync();

        return new AuthResponseDto
        {
            Success = true,
            Message = $"User role updated to {newRole} successfully.",
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
