using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Interface;

public interface IRefreshTokenRepository
{
    Task AddAsync(RefreshToken token);
    Task<RefreshToken?> GetByTokenAsync(string token);
    Task RevokeAllForUserAsync(Guid userId);
    void Update(RefreshToken token);
}
