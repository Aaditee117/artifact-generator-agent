using Microsoft.EntityFrameworkCore;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class TokenUsageRepository : ITokenUsageRepository
{
    private readonly OptiStudioDbContext _context;

    public TokenUsageRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task<List<TokenUsage>> GetAllAsync()
    {
        return await _context.TokenUsages
            .Include(t => t.User)
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync();
    }

    public async Task<List<TokenUsage>> GetByUserIdAsync(Guid userId)
    {
        return await _context.TokenUsages
            .Where(t => t.UserId == userId)
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync();
    }

    public async Task AddAsync(TokenUsage tokenUsage)
    {
        await _context.TokenUsages.AddAsync(tokenUsage);
    }
}
