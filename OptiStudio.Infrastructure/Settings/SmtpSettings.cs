namespace OptiStudio.Infrastructure.Settings;

public class SmtpSettings
{
    public string Host { get; set; } = string.Empty;
    public int Port { get; set; } = 587;
    public string SenderEmail { get; set; } = string.Empty;
    public string SenderPassword { get; set; } = string.Empty;
    public string SenderName { get; set; } = "OptiStudio";
    public bool EnableSsl { get; set; } = true;
}
