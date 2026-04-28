using MailKit.Net.Smtp;
using Microsoft.Extensions.Options;
using MimeKit;
using OptiStudio.Application.Interface;
using OptiStudio.Infrastructure.Settings;

namespace OptiStudio.Infrastructure.Services;

public class EmailService : IEmailService
{
    private readonly SmtpSettings _settings;

    public EmailService(IOptions<SmtpSettings> settings)
    {
        _settings = settings.Value;
    }

    public async Task SendOtpEmailAsync(string toEmail, string otpCode)
    {
        var message = new MimeMessage();
        message.From.Add(new MailboxAddress(_settings.SenderName, _settings.SenderEmail));
        message.To.Add(MailboxAddress.Parse(toEmail));
        message.Subject = "OptiStudio - Email Verification OTP";

        var bodyBuilder = new BodyBuilder
        {
            HtmlBody = $@"
                <div style='font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px; border: 1px solid #e0e0e0; border-radius: 8px;'>
                    <div style='text-align: center; margin-bottom: 24px;'>
                        <img src='https://www.optimusinfo.com/wp-content/uploads/2014/11/optimusinfologo.png' alt='OptiStudio' style='height: 48px;' />
                    </div>
                    <h2 style='color: #c62828; text-align: center;'>Email Verification</h2>
                    <p style='text-align: center; color: #333;'>Your one-time verification code is:</p>
                    <div style='text-align: center; margin: 24px 0;'>
                        <span style='font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #c62828; background: #fce4ec; padding: 12px 32px; border-radius: 8px;'>{otpCode}</span>
                    </div>
                    <p style='text-align: center; color: #888; font-size: 14px;'>This code will expire in <strong>5 minutes</strong>.</p>
                    <hr style='border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;' />
                    <p style='text-align: center; color: #aaa; font-size: 12px;'>If you did not request this code, please ignore this email.</p>
                </div>"
        };
        message.Body = bodyBuilder.ToMessageBody();

        using var client = new SmtpClient();
        await client.ConnectAsync(_settings.Host, _settings.Port, MailKit.Security.SecureSocketOptions.StartTls);
        await client.AuthenticateAsync(_settings.SenderEmail, _settings.SenderPassword);
        await client.SendAsync(message);
        await client.DisconnectAsync(true);
    }
}
