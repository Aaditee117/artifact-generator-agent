using OptiStudio.Application.DTO.Auth;

namespace OptiStudio.Application.DTO.Admin;

public class UserListResponseDto
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public List<UserDto> Users { get; set; } = [];
}
