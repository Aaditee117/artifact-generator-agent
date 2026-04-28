using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Interface;

public interface IChatMessageRepository
{
    Task<ChatMessage?> GetByIdAsync(Guid id);
    Task<List<ChatMessage>> GetBySessionIdAsync(Guid sessionId);
    Task AddAsync(ChatMessage message);
}
