using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using OptiStudio.Domain.Entity;

namespace OptiStudio.Persistence.Configurations;

public class ChatGroupConfiguration : IEntityTypeConfiguration<ChatGroup>
{
    public void Configure(EntityTypeBuilder<ChatGroup> builder)
    {
        builder.ToTable("ChatGroups");
        builder.HasKey(g => g.Id);

        builder.Property(g => g.Name)
            .IsRequired()
            .HasMaxLength(200);

        builder.HasOne(g => g.User)
            .WithMany(u => u.ChatGroups)
            .HasForeignKey(g => g.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(g => g.ChatSessions)
            .WithOne(s => s.ChatGroup)
            .HasForeignKey(s => s.ChatGroupId)
            .OnDelete(DeleteBehavior.NoAction);
    }
}
