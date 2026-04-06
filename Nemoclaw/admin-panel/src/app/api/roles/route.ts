import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET() {
  try {
    const roles = await prisma.role.findMany({
      include: {
        rolePermissions: { include: { permission: true } },
        _count: { select: { users: true } },
      },
      orderBy: { id: "asc" },
    });
    return NextResponse.json(roles);
  } catch (error) {
    console.error("[GET /api/roles]", error);
    return NextResponse.json({ error: "Failed to fetch roles" }, { status: 500 });
  }
}
