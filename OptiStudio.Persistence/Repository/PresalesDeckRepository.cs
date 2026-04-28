using Microsoft.EntityFrameworkCore;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class PresalesDeckRepository : IPresalesDeckRepository
{
    private readonly OptiStudioDbContext _context;

    public PresalesDeckRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task<PresalesDeck?> GetByIdAsync(Guid id)
    {
        return await _context.PresalesDecks
            .Include(p => p.Creator)
            .FirstOrDefaultAsync(p => p.Id == id);
    }

    public async Task<List<PresalesDeck>> GetAllAsync()
    {
        return await _context.PresalesDecks
            .Include(p => p.Creator)
            .OrderByDescending(p => p.CreatedAt)
            .ToListAsync();
    }

    public async Task<List<PresalesDeck>> GetByCreatorIdAsync(Guid creatorId)
    {
        return await _context.PresalesDecks
            .Include(p => p.Creator)
            .Where(p => p.CreatorId == creatorId)
            .OrderByDescending(p => p.CreatedAt)
            .ToListAsync();
    }

    public async Task AddAsync(PresalesDeck presalesDeck)
    {
        await _context.PresalesDecks.AddAsync(presalesDeck);
    }

    public void Update(PresalesDeck presalesDeck)
    {
        _context.PresalesDecks.Update(presalesDeck);
    }
}
