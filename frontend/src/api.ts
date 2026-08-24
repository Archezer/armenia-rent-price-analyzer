export type City = 'Yerevan' | 'Gyumri'

export type PredictionRequest = {
  city: City
  district: string
  rooms: number
  area_sqm: number
  floor: number
  total_floors: number
}

export type PredictionResponse = {
  predicted_monthly_rent_amd: number
  currency: 'AMD'
  model_version: string
}

export type HealthResponse = {
  status: 'OK'
  model_version: string
}

export type RecommendationRequest = {
  city: City
  rooms?: number
  min_area_sqm?: number
  max_area_sqm?: number
  max_budget_amd?: number
  limit: number
}

export type RecommendationItem = {
  city: City
  district: string
  rooms: number
  area_sqm: number
  floor: number
  total_floors: number
  estimated_monthly_rent_amd: number
  currency: 'AMD'
}

type RecommendationResponse = {
  model_version: string
  recommendations: RecommendationItem[]
}

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? 'https://armenian-rent-estimator-api.onrender.com'
).replace(/\/$/, '')

export function predictRent(payload: PredictionRequest): Promise<PredictionResponse> {
  return postJson('/predict', payload)
}

export function getRecommendations(
  payload: RecommendationRequest,
): Promise<RecommendationResponse> {
  return postJson('/recommendations', payload)
}

export async function checkApiHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    cache: 'no-store',
  })

  if (!response.ok) {
    throw new Error(`The API returned HTTP ${response.status}.`)
  }

  return response.json() as Promise<HealthResponse>
}

async function postJson<Response>(path: string, payload: unknown): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }

  return response.json() as Promise<Response>
}

async function readErrorMessage(response: Response): Promise<string> {
  const body = await response.json().catch(() => null)
  if (typeof body?.detail === 'string') {
    return body.detail
  }
  return `The API returned HTTP ${response.status}.`
}
