using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Interface;

public interface IChatSessionRepository
{
    Task<ChatSession?> GetByIdAsync(Guid id);
    Task<ChatSession?> GetByIdWithMessagesAsync(Guid id);
    Task<List<ChatSession>> GetByUserIdAsync(Guid userId);
    Task AddAsync(ChatSession session);
    void Update(ChatSession session);
    void Remove(ChatSession session);
}
