using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Interface;

public interface IArtifactRepository
{
    Task<Artifact?> GetByIdAsync(Guid id);
    Task<List<Artifact>> GetByMessageIdAsync(Guid chatMessageId);
    Task AddAsync(Artifact artifact);
    Task AddRangeAsync(IEnumerable<Artifact> artifacts);
    void Remove(Artifact artifact);
}
