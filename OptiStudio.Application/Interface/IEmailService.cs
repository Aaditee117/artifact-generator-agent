namespace OptiStudio.Application.Interface;

public interface IEmailService
{
    Task SendOtpEmailAsync(string toEmail, string otpCode);
}
