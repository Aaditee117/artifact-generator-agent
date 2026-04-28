using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Interface;

public interface ITokenUsageRepository
{
    Task<List<TokenUsage>> GetAllAsync();
    Task<List<TokenUsage>> GetByUserIdAsync(Guid userId);
    Task AddAsync(TokenUsage tokenUsage);
}
