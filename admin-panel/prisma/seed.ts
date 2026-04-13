/**
 * Seed script: creates default roles, permissions, and role_permissions.
 * Run: npx prisma db seed
 */

import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  // Roles
  const adminRole = await prisma.role.upsert({
    where: { name: "admin" },
    update: {},
    create: { name: "admin" },
  });

  const userRole = await prisma.role.upsert({
    where: { name: "user" },
    update: {},
    create: { name: "user" },
  });

  // Permissions
  const pdfPerm = await prisma.permission.upsert({
    where: { name: "generate_pdf" },
    update: {},
    create: { name: "generate_pdf", description: "Can generate PDF reports via MCP" },
  });

  const imagePerm = await prisma.permission.upsert({
    where: { name: "generate_image" },
    update: {},
    create: { name: "generate_image", description: "Can generate diagrams/charts via MCP" },
  });

  // Admin gets all permissions
  await prisma.rolePermission.upsert({
    where: { roleId_permissionId: { roleId: adminRole.id, permissionId: pdfPerm.id } },
    update: {},
    create: { roleId: adminRole.id, permissionId: pdfPerm.id },
  });

  await prisma.rolePermission.upsert({
    where: { roleId_permissionId: { roleId: adminRole.id, permissionId: imagePerm.id } },
    update: {},
    create: { roleId: adminRole.id, permissionId: imagePerm.id },
  });

  // Regular user gets generate_pdf only
  await prisma.rolePermission.upsert({
    where: { roleId_permissionId: { roleId: userRole.id, permissionId: pdfPerm.id } },
    update: {},
    create: { roleId: userRole.id, permissionId: pdfPerm.id },
  });

  // Sample users
  await prisma.user.upsert({
    where: { telegramId: "admin_001" },
    update: {},
    create: {
      name: "Admin User",
      telegramId: "admin_001",
      phoneNumber: "+1234567890",
      roleId: adminRole.id,
      isActive: true,
    },
  });

  await prisma.user.upsert({
    where: { telegramId: "user_001" },
    update: {},
    create: {
      name: "John Doe",
      telegramId: "user_001",
      phoneNumber: "+0987654321",
      roleId: userRole.id,
      isActive: true,
    },
  });

  // Default settings
  await prisma.setting.upsert({
    where: { key: "pdf_password_enabled" },
    update: {},
    create: { key: "pdf_password_enabled", value: "false" },
  });
  await prisma.setting.upsert({
    where: { key: "pdf_password" },
    update: {},
    create: { key: "pdf_password", value: "" },
  });

  console.log("✓ Seed complete");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
