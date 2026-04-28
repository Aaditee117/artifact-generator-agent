using Microsoft.EntityFrameworkCore;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class ChatMessageRepository : IChatMessageRepository
{
    private readonly OptiStudioDbContext _context;

    public ChatMessageRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task<ChatMessage?> GetByIdAsync(Guid id)
    {
        return await _context.ChatMessages
            .Include(m => m.User)
            .Include(m => m.Artifacts)
            .FirstOrDefaultAsync(m => m.Id == id);
    }

    public async Task<List<ChatMessage>> GetBySessionIdAsync(Guid sessionId)
    {
        return await _context.ChatMessages
            .Include(m => m.User)
            .Include(m => m.Artifacts)
                .ThenInclude(a => a.UploadedByUser)
            .Where(m => m.ChatSessionId == sessionId)
            .OrderBy(m => m.CreatedAt)
            .ToListAsync();
    }

    public async Task AddAsync(ChatMessage message)
    {
        await _context.ChatMessages.AddAsync(message);
    }
}
