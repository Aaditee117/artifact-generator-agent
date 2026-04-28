using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using OptiStudio.Application.Interface;
using Microsoft.EntityFrameworkCore;
using OptiStudio.Domain.Enum;

namespace OptiStudio.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize(Roles = "Admin")]
public class DashboardController : ControllerBase
{
    private readonly IUnitOfWork _unitOfWork;

    public DashboardController(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    [HttpGet("stats")]
    public async Task<IActionResult> GetDashboardStats()
    {
        // Total users
        var users = await _unitOfWork.Users.GetAllAsync();
        var totalUsers = users.Count;

        // Pending Presales
        var allDecks = await _unitOfWork.PresalesDecks.GetAllAsync();
        var pendingApprovals = allDecks.Count(d => d.Status == PresalesStatus.PendingApproval);
        var totalDecks = allDecks.Count;

        // Token usage (Total sum)
        var usages = await _unitOfWork.TokenUsages.GetAllAsync();
        var totalTokens = usages.Sum(u => u.TotalTokens);
        
        // Let's create some simplistic chart data by grouping by Role
        var usersByRole = users.GroupBy(u => u.Role.ToString())
                               .Select(g => new { name = g.Key, value = g.Count() });

        return Ok(new
        {
            totalUsers,
            pendingApprovals,
            totalDecks,
            totalTokens,
            chartData = usersByRole
        });
    }

    [HttpGet("presales")]
    public async Task<IActionResult> GetPresalesList()
    {
        var decks = await _unitOfWork.PresalesDecks.GetAllAsync();
        
        var dtoList = decks.Select(d => new
        {
            id = d.Id,
            name = d.Name,
            status = d.Status.ToString(),
            createdAt = d.CreatedAt,
            creatorEmail = d.Creator?.Email ?? "Unknown"
        }).OrderByDescending(x => x.createdAt);

        return Ok(dtoList);
    }
}
