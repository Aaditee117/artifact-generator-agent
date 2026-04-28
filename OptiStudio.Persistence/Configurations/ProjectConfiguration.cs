using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using OptiStudio.Domain.Entity;

namespace OptiStudio.Persistence.Configurations;

public class ProjectConfiguration : IEntityTypeConfiguration<Project>
{
    public void Configure(EntityTypeBuilder<Project> builder)
    {
        builder.HasKey(p => p.Id);
        
        builder.Property(p => p.Name)
            .IsRequired()
            .HasMaxLength(200);
            
        builder.Property(p => p.Description)
            .HasMaxLength(2000);
            
        builder.Property(p => p.ClientName)
            .HasMaxLength(200);
            
        builder.Property(p => p.TechStack)
            .HasMaxLength(500);
            
        builder.Property(p => p.Notes)
            .HasMaxLength(4000);
            
        builder.Property(p => p.EstimatedBudget)
            .HasPrecision(18, 2);

        builder.HasOne(p => p.Owner)
            .WithMany()
            .HasForeignKey(p => p.OwnerId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasMany(p => p.PresalesDecks)
            .WithOne(d => d.Project)
            .HasForeignKey(d => d.ProjectId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(p => p.Name);
        builder.HasIndex(p => p.ClientName);
        builder.HasIndex(p => p.Status);
        builder.HasIndex(p => p.Phase);
        builder.HasIndex(p => p.CreatedAt);
    }
}
