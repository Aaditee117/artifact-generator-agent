using Microsoft.EntityFrameworkCore;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class ChatSessionRepository : IChatSessionRepository
{
    private readonly OptiStudioDbContext _context;

    public ChatSessionRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task<ChatSession?> GetByIdAsync(Guid id)
    {
        return await _context.ChatSessions
            .Include(s => s.ChatGroup)
            .FirstOrDefaultAsync(s => s.Id == id);
    }

    public async Task<ChatSession?> GetByIdWithMessagesAsync(Guid id)
    {
        return await _context.ChatSessions
            .Include(s => s.ChatGroup)
            .Include(s => s.Messages.OrderBy(m => m.CreatedAt))
                .ThenInclude(m => m.Artifacts)
            .Include(s => s.Messages)
                .ThenInclude(m => m.User)
            .FirstOrDefaultAsync(s => s.Id == id);
    }

    public async Task<List<ChatSession>> GetByUserIdAsync(Guid userId)
    {
        return await _context.ChatSessions
            .Include(s => s.ChatGroup)
            .Include(s => s.Messages.OrderByDescending(m => m.CreatedAt).Take(1))
            .Where(s => s.UserId == userId)
            .OrderByDescending(s => s.UpdatedAt ?? s.CreatedAt)
            .ToListAsync();
    }

    public async Task AddAsync(ChatSession session)
    {
        await _context.ChatSessions.AddAsync(session);
    }

    public void Update(ChatSession session)
    {
        _context.ChatSessions.Update(session);
    }

    public void Remove(ChatSession session)
    {
        _context.ChatSessions.Remove(session);
    }
}
