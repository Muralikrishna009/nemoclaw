import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

// GET /api/users — list all users with role and permissions
export async function GET() {
  try {
    const users = await prisma.user.findMany({
      include: {
        role: {
          include: {
            rolePermissions: {
              include: { permission: true },
            },
          },
        },
      },
      orderBy: { createdAt: "desc" },
    });
    return NextResponse.json(users);
  } catch (error) {
    console.error("[GET /api/users]", error);
    return NextResponse.json({ error: "Failed to fetch users" }, { status: 500 });
  }
}

// POST /api/users — create a new user
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, telegramId, phoneNumber, roleId, isActive } = body;

    if (!name || !roleId) {
      return NextResponse.json({ error: "name and roleId are required" }, { status: 400 });
    }

    const user = await prisma.user.create({
      data: {
        name,
        telegramId: telegramId || null,
        phoneNumber: phoneNumber || null,
        roleId: Number(roleId),
        isActive: isActive ?? true,
      },
      include: {
        role: true,
      },
    });

    return NextResponse.json(user, { status: 201 });
  } catch (error: unknown) {
    console.error("[POST /api/users]", error);
    // Unique constraint violation (telegram_id already exists)
    if ((error as { code?: string }).code === "P2002") {
      return NextResponse.json({ error: "Telegram ID already exists" }, { status: 409 });
    }
    return NextResponse.json({ error: "Failed to create user" }, { status: 500 });
  }
}
