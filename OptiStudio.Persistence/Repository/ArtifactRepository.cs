using Microsoft.EntityFrameworkCore;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class ArtifactRepository : IArtifactRepository
{
    private readonly OptiStudioDbContext _context;

    public ArtifactRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task<Artifact?> GetByIdAsync(Guid id)
    {
        return await _context.Artifacts
            .Include(a => a.UploadedByUser)
            .FirstOrDefaultAsync(a => a.Id == id);
    }

    public async Task<List<Artifact>> GetByMessageIdAsync(Guid chatMessageId)
    {
        return await _context.Artifacts
            .Include(a => a.UploadedByUser)
            .Where(a => a.ChatMessageId == chatMessageId)
            .OrderByDescending(a => a.CreatedAt)
            .ToListAsync();
    }

    public async Task AddAsync(Artifact artifact)
    {
        await _context.Artifacts.AddAsync(artifact);
    }

    public async Task AddRangeAsync(IEnumerable<Artifact> artifacts)
    {
        await _context.Artifacts.AddRangeAsync(artifacts);
    }

    public void Remove(Artifact artifact)
    {
        _context.Artifacts.Remove(artifact);
    }
}
