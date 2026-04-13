import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

// GET /api/settings — returns all settings as a flat key/value object
export async function GET() {
  try {
    const rows = await prisma.setting.findMany();
    const result: Record<string, string> = {};
    for (const r of rows) result[r.key] = r.value;
    return NextResponse.json(result);
  } catch (error) {
    console.error("[GET /api/settings]", error);
    return NextResponse.json({ error: "Failed to fetch settings" }, { status: 500 });
  }
}

// PATCH /api/settings — upserts one or more settings
// Body: { "pdf_password_enabled": "true", "pdf_password": "secret" }
export async function PATCH(req: NextRequest) {
  try {
    const body: Record<string, string> = await req.json();

    await Promise.all(
      Object.entries(body).map(([key, value]) =>
        prisma.setting.upsert({
          where: { key },
          update: { value },
          create: { key, value },
        })
      )
    );

    return NextResponse.json({ ok: true });
  } catch (error) {
    console.error("[PATCH /api/settings]", error);
    return NextResponse.json({ error: "Failed to save settings" }, { status: 500 });
  }
}
