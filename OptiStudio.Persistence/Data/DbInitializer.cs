using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using OptiStudio.Persistence.Data;

namespace OptiStudio.Persistence;

public static class DbInitializer
{
    public static async Task SeedAsync(IServiceProvider serviceProvider)
    {
        using var scope = serviceProvider.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<OptiStudioDbContext>();

        // Apply any pending migrations
        await context.Database.MigrateAsync();

        // Remove old test/seed users and their related data (if they exist)
        var testEmails = new[] { "admin@optistudio.com", "architect@optistudio.com", "developer@optistudio.com" };
        var testUsers = await context.Users
            .Where(u => testEmails.Contains(u.Email))
            .ToListAsync();

        if (testUsers.Any())
        {
            var testUserIds = testUsers.Select(u => u.Id).ToList();

            // Delete related data first (due to foreign key constraints)

            // 1. Delete ApiRequestLogs referencing test users
            var apiLogs = await context.ApiRequestLogs
                .Where(l => l.UserId != null && testUserIds.Contains(l.UserId.Value))
                .ToListAsync();
            if (apiLogs.Any())
            {
                context.ApiRequestLogs.RemoveRange(apiLogs);
            }

            // 2. Delete TokenUsages referencing test users (UserId is not nullable here)
            var tokenUsages = await context.TokenUsages
                .Where(t => testUserIds.Contains(t.UserId))
                .ToListAsync();
            if (tokenUsages.Any())
            {
                context.TokenUsages.RemoveRange(tokenUsages);
            }

            // 3. Delete PresalesDecks created/approved by test users
            var decks = await context.PresalesDecks
                .Where(d => testUserIds.Contains(d.CreatorId) || 
                           (d.ApproverId != null && testUserIds.Contains(d.ApproverId.Value)))
                .ToListAsync();
            if (decks.Any())
            {
                context.PresalesDecks.RemoveRange(decks);
            }

            // 4. Delete Projects owned by test users
            var projects = await context.Projects
                .Where(p => testUserIds.Contains(p.OwnerId))
                .ToListAsync();
            if (projects.Any())
            {
                context.Projects.RemoveRange(projects);
            }

            // 5. Delete ChatMessages and ChatSessions for test users
            var chatSessions = await context.ChatSessions
                .Where(s => testUserIds.Contains(s.UserId))
                .ToListAsync();
            if (chatSessions.Any())
            {
                var sessionIds = chatSessions.Select(s => s.Id).ToList();
                var messages = await context.ChatMessages
                    .Where(m => sessionIds.Contains(m.ChatSessionId))
                    .ToListAsync();
                if (messages.Any())
                {
                    context.ChatMessages.RemoveRange(messages);
                }
                context.ChatSessions.RemoveRange(chatSessions);
            }

            // 6. Delete RefreshTokens for test users
            var refreshTokens = await context.RefreshTokens
                .Where(r => testUserIds.Contains(r.UserId))
                .ToListAsync();
            if (refreshTokens.Any())
            {
                context.RefreshTokens.RemoveRange(refreshTokens);
            }

            // 7. Delete OtpRecords for test users
            var otpRecords = await context.OtpRecords
                .Where(o => testUserIds.Contains(o.UserId))
                .ToListAsync();
            if (otpRecords.Any())
            {
                context.OtpRecords.RemoveRange(otpRecords);
            }

            // Save all deletions of related data
            await context.SaveChangesAsync();

            // Now delete the test users
            context.Users.RemoveRange(testUsers);
            await context.SaveChangesAsync();

            Console.WriteLine($"[DbInitializer] Removed {testUsers.Count} test user(s) and their related data from database.");
        }

        // Note: Real users are created via MSAL login flow in AuthController.GetCurrentUser()
        // No seed users are created here - all users come from Azure AD authentication
    }
}
