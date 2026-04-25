/**
 * POST /api/generate-video
 * ─────────────────────────────────────────────────────────────
 * Step 3: submits a video generation task to Seedance 2.0.
 * Returns { taskId, status } immediately — the client must
 * poll /api/status?id=<taskId> to wait for completion.
 */

import { NextRequest, NextResponse } from "next/server";
import type { GenerateVideoRequest } from "@/types";
import { isDemoMode } from "@/lib/utils";
import { hasSeedanceKey } from "@/services/byteplus/seedanceClient";
import { createVideoTask } from "@/services/byteplus/seedanceService";
import { mockCreateVideoTask } from "@/services/mock/mockService";

// Allow up to 60 s for the Seedance submission call
export const maxDuration = 60;

export async function POST(request: NextRequest) {
  try {
    const body: GenerateVideoRequest = await request.json();

    if (!body.imageBase64) {
      return NextResponse.json(
        { error: "imageBase64 is required" },
        { status: 400 }
      );
    }

    if (!body.full_prompt) {
      return NextResponse.json(
        { error: "full_prompt is required" },
        { status: 400 }
      );
    }

    // Use real Seedance only when a key is configured AND not in demo mode.
    const result = (!isDemoMode() && hasSeedanceKey())
      ? await createVideoTask(body)
      : await mockCreateVideoTask(body);

    return NextResponse.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unexpected error";
    console.error("[generate-video]", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
