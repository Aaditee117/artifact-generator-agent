using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using OptiStudio.Application.DTO.Admin;
using OptiStudio.Application.Features.Admin.Commands.UpdateUserRole;
using OptiStudio.Application.Features.Admin.Queries.GetAllUsers;

namespace OptiStudio.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize(Roles = "Admin")]
public class AdminController : ControllerBase
{
    private readonly IMediator _mediator;

    public AdminController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("users")]
    public async Task<IActionResult> GetAllUsers([FromQuery] string? search)
    {
        var query = new GetAllUsersQuery { SearchTerm = search };
        var result = await _mediator.Send(query);
        return Ok(result);
    }

    [HttpPut("users/{userId}/role")]
    public async Task<IActionResult> UpdateUserRole(Guid userId, [FromBody] UpdateUserRoleRequestDto dto)
    {
        var command = new UpdateUserRoleCommand
        {
            UserId = userId,
            Role = dto.Role
        };

        var result = await _mediator.Send(command);
        return result.Success ? Ok(result) : BadRequest(result);
    }
}
