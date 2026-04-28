using Microsoft.EntityFrameworkCore;
using OptiStudio.Domain.Entity;
using OptiStudio.Domain.Enum;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class ProjectRepository
{
    private readonly OptiStudioDbContext _context;

    public ProjectRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task<Project?> GetByIdAsync(Guid id) =>
        await _context.Projects
            .Include(p => p.Owner)
            .Include(p => p.PresalesDecks)
            .FirstOrDefaultAsync(p => p.Id == id);

    public async Task<List<Project>> GetAllAsync() =>
        await _context.Projects
            .Include(p => p.Owner)
            .OrderByDescending(p => p.CreatedAt)
            .ToListAsync();

    public async Task<List<Project>> GetByStatusAsync(ProjectStatus status) =>
        await _context.Projects
            .Include(p => p.Owner)
            .Where(p => p.Status == status)
            .OrderByDescending(p => p.CreatedAt)
            .ToListAsync();

    public async Task<List<Project>> GetByPhaseAsync(ProjectPhase phase) =>
        await _context.Projects
            .Include(p => p.Owner)
            .Where(p => p.Phase == phase)
            .OrderByDescending(p => p.CreatedAt)
            .ToListAsync();

    public async Task<List<Project>> GetRecentAsync(int days = 30) =>
        await _context.Projects
            .Include(p => p.Owner)
            .Where(p => p.CreatedAt >= DateTime.UtcNow.AddDays(-days))
            .OrderByDescending(p => p.CreatedAt)
            .ToListAsync();

    public async Task<List<Project>> GetByOwnerAsync(Guid ownerId) =>
        await _context.Projects
            .Include(p => p.Owner)
            .Where(p => p.OwnerId == ownerId)
            .OrderByDescending(p => p.CreatedAt)
            .ToListAsync();

    public async Task<Project> CreateAsync(Project project)
    {
        await _context.Projects.AddAsync(project);
        await _context.SaveChangesAsync();
        return project;
    }

    public async Task UpdateAsync(Project project)
    {
        project.UpdatedAt = DateTime.UtcNow;
        _context.Projects.Update(project);
        await _context.SaveChangesAsync();
    }

    public async Task<int> GetTotalCountAsync() =>
        await _context.Projects.CountAsync();

    public async Task<Dictionary<ProjectStatus, int>> GetCountByStatusAsync() =>
        await _context.Projects
            .GroupBy(p => p.Status)
            .Select(g => new { Status = g.Key, Count = g.Count() })
            .ToDictionaryAsync(x => x.Status, x => x.Count);

    public async Task<Dictionary<ProjectPhase, int>> GetCountByPhaseAsync() =>
        await _context.Projects
            .GroupBy(p => p.Phase)
            .Select(g => new { Phase = g.Key, Count = g.Count() })
            .ToDictionaryAsync(x => x.Phase, x => x.Count);
}
