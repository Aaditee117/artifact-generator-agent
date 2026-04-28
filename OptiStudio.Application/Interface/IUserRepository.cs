using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Interface;

public interface IUserRepository
{
    Task<User?> GetByIdAsync(Guid id);
    Task<User?> GetByEmailAsync(string email);
    Task<List<User>> GetAllAsync();
    Task<List<User>> SearchAsync(string searchTerm);
    Task AddAsync(User user);
    void Update(User user);
}
