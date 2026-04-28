using FluentValidation;

namespace OptiStudio.Application.Features.Chat.Commands.SendChatMessage;

public class SendChatMessageCommandValidator : AbstractValidator<SendChatMessageCommand>
{
    private static readonly HashSet<string> AllowedExtensions = new(StringComparer.OrdinalIgnoreCase)
    {
        ".pdf", ".docx", ".pptx", ".txt", ".jpg", ".jpeg", ".png"
    };

    private const long MaxFileSizeBytes = 15 * 1024 * 1024;
    private const long MaxRequestSizeBytes = 50 * 1024 * 1024;

    public SendChatMessageCommandValidator()
    {
        RuleFor(x => x.ChatSessionId)
            .NotEmpty().WithMessage("Session ID is required.");

        RuleFor(x => x.UserId)
            .NotEmpty().WithMessage("User ID is required.");

        RuleFor(x => x)
            .Must(x => !string.IsNullOrWhiteSpace(x.Content) || x.Files.Count > 0)
            .WithMessage("A message must contain text or at least one file.");

        RuleFor(x => x.Content)
            .MaximumLength(10000).WithMessage("Message content must not exceed 10,000 characters.")
            .When(x => !string.IsNullOrWhiteSpace(x.Content));

        RuleFor(x => x.Files)
            .Must(files => files.Sum(f => f.Length) <= MaxRequestSizeBytes)
            .When(x => x.Files.Count > 0)
            .WithMessage("Total upload size must not exceed 50 MB.");

        RuleForEach(x => x.Files).ChildRules(file =>
        {
            file.RuleFor(f => f.Length)
                .GreaterThan(0).WithMessage("File cannot be empty.")
                .LessThanOrEqualTo(MaxFileSizeBytes).WithMessage("Each file must not exceed 15 MB.");

            file.RuleFor(f => f.FileName)
                .Must(name => AllowedExtensions.Contains(Path.GetExtension(name)))
                .WithMessage(f => $"File '{f.FileName}' has an unsupported format. Allowed: {string.Join(", ", AllowedExtensions)}");
        });
    }
}
