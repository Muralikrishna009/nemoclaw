import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

// PUT /api/roles/:id/permissions — replace role's permission set
export async function PUT(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { permissionIds }: { permissionIds: number[] } = await req.json();
    const roleId = Number(params.id);

    // Replace all permissions for this role
    await prisma.rolePermission.deleteMany({ where: { roleId } });

    if (permissionIds.length > 0) {
      await prisma.rolePermission.createMany({
        data: permissionIds.map((permissionId) => ({ roleId, permissionId })),
      });
    }

    const updated = await prisma.role.findUnique({
      where: { id: roleId },
      include: { rolePermissions: { include: { permission: true } } },
    });

    return NextResponse.json(updated);
  } catch (error) {
    console.error("[PUT /api/roles/:id/permissions]", error);
    return NextResponse.json({ error: "Failed to update permissions" }, { status: 500 });
  }
}
