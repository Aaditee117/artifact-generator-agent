using Microsoft.EntityFrameworkCore;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class UserRepository : IUserRepository
{
    private readonly OptiStudioDbContext _context;

    public UserRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task<User?> GetByIdAsync(Guid id)
    {
        return await _context.Users.FindAsync(id);
    }

    public async Task<User?> GetByEmailAsync(string email)
    {
        if (string.IsNullOrEmpty(email)) return null;
        
        var lowerEmail = email.ToLower();
        return await _context.Users
            .FirstOrDefaultAsync(u => u.Email.ToLower() == lowerEmail);
    }

    public async Task<List<User>> GetAllAsync()
    {
        return await _context.Users
            .OrderBy(u => u.CreatedAt)
            .ToListAsync();
    }

    public async Task<List<User>> SearchAsync(string searchTerm)
    {
        var term = searchTerm.ToLowerInvariant();
        return await _context.Users
            .Where(u => u.Name.ToLower().Contains(term) || u.Email.Contains(term) || u.Role.ToString().ToLower().Contains(term))
            .OrderBy(u => u.CreatedAt)
            .ToListAsync();
    }

    public async Task AddAsync(User user)
    {
        await _context.Users.AddAsync(user);
    }

    public void Update(User user)
    {
        _context.Users.Update(user);
    }
}
