/** Review API 客户端 */

export interface ReviewSegment {
  segment_id: string;
  start: number;
  end: number;
  asr_text: string;
  normalized_text?: string;
  alignment_status?: string;
  similarity?: number;
  source_text?: string;
  model_action?: string;
  model_reason?: string;
  model_confidence?: number;
  suggested_cut?: {
    start: number;
    end: number;
    pre_padding?: number;
    post_padding?: number;
  } | null;
  filler_candidates?: Array<{ token: string; type: string; auto_delete: boolean }>;
}

export interface ReviewData {
  project_id: string;
  chapter_id: string;
  title: string;
  source_audio: string;
  normalized_source_text: string;
  segments: ReviewSegment[];
  llm_engine?: string;
}

export interface UserDecision {
  segment_id: string;
  user_action: "keep" | "delete" | "uncertain";
  user_adjusted_cut?: ReviewSegment["suggested_cut"];
  note?: string;
}

export interface CutPlan {
  chapter_id: string;
  source_audio: string;
  delete_ranges: Array<{
    range_id: string;
    start: number;
    end: number;
    reason?: string;
    confirmed_by_user?: boolean;
  }>;
  keep_ranges: Array<Record<string, unknown>>;
}

const API_BASE = "/api";

const DEMO_PROJECT = "book_001";
const DEMO_CHAPTER = "chapter_001";

/** 将 API 错误转为用户可读文案，避免暴露本机绝对路径或原始 JSON */
export function parseApiError(body: string, status: number): string {
  if (status === 404) {
    return `未找到项目或章节。请检查参数，或打开演示章节 ${DEMO_PROJECT}/${DEMO_CHAPTER}。`;
  }

  try {
    const parsed = JSON.parse(body) as { detail?: string };
    const detail = parsed.detail ?? body;
    if (
      typeof detail === "string" &&
      (detail.includes("/Users/") ||
        detail.includes(":\\") ||
        detail.includes("manifest 不存在") ||
        detail.includes("文件不存在"))
    ) {
      return `未找到项目或章节。请检查参数，或打开演示章节 ${DEMO_PROJECT}/${DEMO_CHAPTER}。`;
    }
    return typeof detail === "string" ? detail : "请求失败，请稍后重试。";
  } catch {
    if (body.includes("/Users/") || body.includes("manifest 不存在")) {
      return `未找到项目或章节。请检查参数，或打开演示章节 ${DEMO_PROJECT}/${DEMO_CHAPTER}。`;
    }
    return body || "请求失败，请稍后重试。";
  }
}

export async function fetchReviewData(
  projectId: string,
  chapterId: string,
): Promise<ReviewData> {
  const res = await fetch(
    `${API_BASE}/projects/${projectId}/chapters/${chapterId}/review-data`,
  );
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), res.status));
  }
  return res.json();
}

export async function saveReview(
  projectId: string,
  chapterId: string,
  decisions: UserDecision[],
): Promise<{ cut_plan_path: string; delete_count: number; keep_count: number }> {
  const res = await fetch(
    `${API_BASE}/projects/${projectId}/chapters/${chapterId}/review`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decisions }),
    },
  );
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), res.status));
  }
  return res.json();
}

export async function fetchCutPlan(
  projectId: string,
  chapterId: string,
): Promise<CutPlan | null> {
  const res = await fetch(
    `${API_BASE}/projects/${projectId}/chapters/${chapterId}/cut-plan`,
  );
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), res.status));
  }
  return res.json();
}

export async function updateCutPlan(
  projectId: string,
  chapterId: string,
  cutPlan: Pick<CutPlan, "delete_ranges" | "keep_ranges">,
): Promise<{ cut_plan_path: string }> {
  const res = await fetch(
    `${API_BASE}/projects/${projectId}/chapters/${chapterId}/cut-plan`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        delete_ranges: cutPlan.delete_ranges,
        keep_ranges: cutPlan.keep_ranges,
        version: 2,
      }),
    },
  );
  if (!res.ok) {
    throw new Error(parseApiError(await res.text(), res.status));
  }
  return res.json();
}

export function audioServeUrl(sourceAudioPath: string): string {
  return `${API_BASE}/audio/${sourceAudioPath}`;
}

export const DEMO = { projectId: DEMO_PROJECT, chapterId: DEMO_CHAPTER };
