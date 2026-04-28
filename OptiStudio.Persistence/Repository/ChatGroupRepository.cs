using Microsoft.EntityFrameworkCore;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class ChatGroupRepository : IChatGroupRepository
{
    private readonly OptiStudioDbContext _context;

    public ChatGroupRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task<ChatGroup?> GetByIdAsync(Guid id)
    {
        return await _context.ChatGroups
            .Include(g => g.ChatSessions)
            .FirstOrDefaultAsync(g => g.Id == id);
    }

    public async Task<List<ChatGroup>> GetByUserIdAsync(Guid userId)
    {
        return await _context.ChatGroups
            .Include(g => g.ChatSessions)
            .Where(g => g.UserId == userId)
            .OrderBy(g => g.CreatedAt)
            .ToListAsync();
    }

    public async Task AddAsync(ChatGroup group)
    {
        await _context.ChatGroups.AddAsync(group);
    }

    public void Update(ChatGroup group)
    {
        _context.ChatGroups.Update(group);
    }

    public void Remove(ChatGroup group)
    {
        _context.ChatGroups.Remove(group);
    }
}
