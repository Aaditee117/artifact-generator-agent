using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Interface;

public interface IChatGroupRepository
{
    Task<ChatGroup?> GetByIdAsync(Guid id);
    Task<List<ChatGroup>> GetByUserIdAsync(Guid userId);
    Task AddAsync(ChatGroup group);
    void Update(ChatGroup group);
    void Remove(ChatGroup group);
}
