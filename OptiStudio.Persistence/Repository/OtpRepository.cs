using Microsoft.EntityFrameworkCore;
using OptiStudio.Application.Interface;
using OptiStudio.Domain.Entity;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class OtpRepository : IOtpRepository
{
    private readonly OptiStudioDbContext _context;

    public OtpRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task AddAsync(OtpRecord otp)
    {
        await _context.OtpRecords.AddAsync(otp);
    }

    public async Task<OtpRecord?> GetLatestActiveOtpAsync(Guid userId)
    {
        return await _context.OtpRecords
            .Where(o => o.UserId == userId && !o.IsUsed)
            .OrderByDescending(o => o.CreatedAt)
            .FirstOrDefaultAsync();
    }

    public void Update(OtpRecord otp)
    {
        _context.OtpRecords.Update(otp);
    }
}
