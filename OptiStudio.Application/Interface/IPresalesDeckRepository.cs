using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Interface;

public interface IPresalesDeckRepository
{
    Task<PresalesDeck?> GetByIdAsync(Guid id);
    Task<List<PresalesDeck>> GetAllAsync();
    Task<List<PresalesDeck>> GetByCreatorIdAsync(Guid creatorId);
    Task AddAsync(PresalesDeck presalesDeck);
    void Update(PresalesDeck presalesDeck);
}
