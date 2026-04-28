using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using OptiStudio.Domain.Entity;

namespace OptiStudio.Persistence.Configurations;

public class PresalesDeckConfiguration : IEntityTypeConfiguration<PresalesDeck>
{
    public void Configure(EntityTypeBuilder<PresalesDeck> builder)
    {
        builder.HasKey(p => p.Id);

        builder.Property(p => p.Name)
            .IsRequired()
            .HasMaxLength(255);

        builder.Property(p => p.Description)
            .HasMaxLength(2000);

        builder.Property(p => p.ClientName)
            .HasMaxLength(200);

        builder.Property(p => p.StoragePath)
            .HasMaxLength(1000);

        builder.Property(p => p.RejectionReason)
            .HasMaxLength(1000);

        builder.Property(p => p.ApprovalNotes)
            .HasMaxLength(1000);

        builder.HasOne(p => p.Creator)
            .WithMany(u => u.PresalesDecks)
            .HasForeignKey(p => p.CreatorId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(p => p.Approver)
            .WithMany()
            .HasForeignKey(p => p.ApproverId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(p => p.ChatSession)
            .WithMany()
            .HasForeignKey(p => p.ChatSessionId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasOne(p => p.Project)
            .WithMany(proj => proj.PresalesDecks)
            .HasForeignKey(p => p.ProjectId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(p => p.Status);
        builder.HasIndex(p => p.CreatedAt);
        builder.HasIndex(p => p.ClientName);
    }
}
