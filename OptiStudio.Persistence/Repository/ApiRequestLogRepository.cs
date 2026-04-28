using Microsoft.EntityFrameworkCore;
using OptiStudio.Domain.Entity;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence.Repository;

public class ApiRequestLogRepository
{
    private readonly OptiStudioDbContext _context;

    public ApiRequestLogRepository(OptiStudioDbContext context)
    {
        _context = context;
    }

    public async Task<ApiRequestLog> CreateAsync(ApiRequestLog log)
    {
        await _context.ApiRequestLogs.AddAsync(log);
        await _context.SaveChangesAsync();
        return log;
    }

    public async Task<List<ApiRequestLog>> GetRecentAsync(int count = 100) =>
        await _context.ApiRequestLogs
            .Include(a => a.User)
            .OrderByDescending(a => a.CreatedAt)
            .Take(count)
            .ToListAsync();

    public async Task<int> GetTotalRequestsAsync() =>
        await _context.ApiRequestLogs.CountAsync();

    public async Task<int> GetRequestsInPeriodAsync(DateTime from, DateTime to) =>
        await _context.ApiRequestLogs
            .Where(a => a.CreatedAt >= from && a.CreatedAt <= to)
            .CountAsync();

    public async Task<int> GetErrorCountAsync() =>
        await _context.ApiRequestLogs
            .Where(a => a.StatusCode >= 400)
            .CountAsync();

    public async Task<double> GetAverageResponseTimeAsync() =>
        await _context.ApiRequestLogs.AverageAsync(a => (double?)a.ResponseTimeMs) ?? 0;

    public async Task<Dictionary<string, int>> GetRequestsByEndpointAsync() =>
        await _context.ApiRequestLogs
            .GroupBy(a => a.Endpoint)
            .Select(g => new { Endpoint = g.Key, Count = g.Count() })
            .ToDictionaryAsync(x => x.Endpoint, x => x.Count);

    public async Task<Dictionary<int, int>> GetRequestsByStatusCodeAsync() =>
        await _context.ApiRequestLogs
            .GroupBy(a => a.StatusCode)
            .Select(g => new { StatusCode = g.Key, Count = g.Count() })
            .ToDictionaryAsync(x => x.StatusCode, x => x.Count);

    public async Task<List<ApiRequestLog>> GetByUserAsync(Guid userId) =>
        await _context.ApiRequestLogs
            .Where(a => a.UserId == userId)
            .OrderByDescending(a => a.CreatedAt)
            .ToListAsync();

    public async Task<Dictionary<DateTime, int>> GetDailyRequestCountAsync(int days = 7) =>
        await _context.ApiRequestLogs
            .Where(a => a.CreatedAt >= DateTime.UtcNow.AddDays(-days))
            .GroupBy(a => a.CreatedAt.Date)
            .Select(g => new { Date = g.Key, Count = g.Count() })
            .ToDictionaryAsync(x => x.Date, x => x.Count);
}
