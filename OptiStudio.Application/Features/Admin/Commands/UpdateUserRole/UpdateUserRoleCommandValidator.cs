using FluentValidation;

namespace OptiStudio.Application.Features.Admin.Commands.UpdateUserRole;

public class UpdateUserRoleCommandValidator : AbstractValidator<UpdateUserRoleCommand>
{
    public UpdateUserRoleCommandValidator()
    {
        RuleFor(x => x.UserId)
            .NotEmpty().WithMessage("User ID is required.");

        RuleFor(x => x.Role)
            .NotEmpty().WithMessage("Role is required.")
            .Must(role => role.Equals("Admin", StringComparison.OrdinalIgnoreCase)
                       || role.Equals("Architect", StringComparison.OrdinalIgnoreCase)
                       || role.Equals("Developer", StringComparison.OrdinalIgnoreCase))
            .WithMessage("Role must be Admin, Architect, or Developer.");
    }
}
