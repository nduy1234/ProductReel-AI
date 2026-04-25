/**
 * GET /api/status?id=<taskId>
 * ─────────────────────────────────────────────────────────────
 * Polls the status of a Seedance 2.0 video generation task.
 *
 * The client calls this every 5 seconds until status is
 * "succeeded" or "failed".
 *
 * Response:
 *   { taskId, status, videoUrl?, thumbnailUrl?, error? }
 */

import { NextRequest, NextResponse } from "next/server";
import { isDemoMode } from "@/lib/utils";
import { hasSeedanceKey } from "@/services/byteplus/seedanceClient";
import { getVideoTaskStatus } from "@/services/byteplus/seedanceService";
import { mockGetVideoStatus } from "@/services/mock/mockService";

// Never cache polling responses
export const dynamic = "force-dynamic";
export const maxDuration = 60;

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const taskId = searchParams.get("id");

    if (!taskId) {
      return NextResponse.json(
        { error: "id query parameter is required" },
        { status: 400 }
      );
    }

    // Mirror the same logic as generate-video: use real API only when not in demo mode and key is set
    const result = (!isDemoMode() && hasSeedanceKey())
      ? await getVideoTaskStatus(taskId)
      : await mockGetVideoStatus(taskId);

    return NextResponse.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unexpected error";
    console.error("[status]", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
