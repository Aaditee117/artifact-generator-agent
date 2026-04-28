using OptiStudio.Domain.Entity;

namespace OptiStudio.Application.Interface;

public interface IOtpRepository
{
    Task AddAsync(OtpRecord otp);
    Task<OtpRecord?> GetLatestActiveOtpAsync(Guid userId);
    void Update(OtpRecord otp);
}
