import { useCallback, useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import {
  checkApiHealth,
  getRecommendations,
  predictRent,
  type City,
  type PredictionResponse,
  type RecommendationItem,
} from './api'
import './App.css'

const INITIAL_PREDICTION_FORM = {
  city: 'Yerevan' as City,
  district: 'Kentron',
  rooms: '2',
  areaSqm: '60',
  floor: '3',
  totalFloors: '9',
}

const INITIAL_RECOMMENDATION_FORM = {
  city: 'Yerevan' as City,
  rooms: '',
  minAreaSqm: '',
  maxAreaSqm: '',
  maxBudgetAmd: '',
}

function App() {
  const [predictionForm, setPredictionForm] = useState(INITIAL_PREDICTION_FORM)
  const [recommendationForm, setRecommendationForm] = useState(INITIAL_RECOMMENDATION_FORM)
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null)
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([])
  const [predictionError, setPredictionError] = useState<string | null>(null)
  const [recommendationError, setRecommendationError] = useState<string | null>(null)
  const [isPredicting, setIsPredicting] = useState(false)
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false)
  const [apiStatus, setApiStatus] = useState<
    'starting' | 'ready' | 'unavailable'
  >('starting')
  const healthCheckStarted = useRef(false)

  const refreshApiStatus = useCallback(async () => {
    setApiStatus('starting')

    try {
      await checkApiHealth()
      setApiStatus('ready')
    } catch {
      setApiStatus('unavailable')
    }
  }, [])

  useEffect(() => {
    if (healthCheckStarted.current) {
      return
    }

    healthCheckStarted.current = true
    void refreshApiStatus()
  }, [refreshApiStatus])

  const isApiReady = apiStatus === 'ready'

  async function handlePrediction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsPredicting(true)
    setPredictionError(null)

    try {
      const result = await predictRent({
        city: predictionForm.city,
        district: predictionForm.district,
        rooms: Number(predictionForm.rooms),
        area_sqm: Number(predictionForm.areaSqm),
        floor: Number(predictionForm.floor),
        total_floors: Number(predictionForm.totalFloors),
      })
      setPrediction(result)
    } catch (error) {
      setPrediction(null)
      setPredictionError(error instanceof Error ? error.message : 'Request failed.')
    } finally {
      setIsPredicting(false)
    }
  }

  async function handleRecommendations(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsLoadingRecommendations(true)
    setRecommendationError(null)

    try {
      const result = await getRecommendations({
        city: recommendationForm.city,
        rooms: optionalNumber(recommendationForm.rooms),
        min_area_sqm: optionalNumber(recommendationForm.minAreaSqm),
        max_area_sqm: optionalNumber(recommendationForm.maxAreaSqm),
        max_budget_amd: optionalNumber(recommendationForm.maxBudgetAmd),
        limit: 5,
      })
      setRecommendations(result.recommendations)
    } catch (error) {
      setRecommendations([])
      setRecommendationError(error instanceof Error ? error.message : 'Request failed.')
    } finally {
      setIsLoadingRecommendations(false)
    }
  }

  return (
    <main className="page-shell">
      <header className="hero">
        <p className="eyebrow">Armenian long-term rental estimator</p>
        <h1>Estimate an apartment’s monthly asking rent.</h1>
        <p className="hero-copy">
          A student machine-learning project based on structured rental listing data.
          All estimates are in Armenian dram (AMD).
        </p>
      </header>

      <section
        className={`api-status api-status--${apiStatus}`}
        aria-live="polite"
      >
        {apiStatus === 'starting' && (
          <>
            <span className="loader" aria-hidden="true" />
            <p>
              Connecting to the demo API. Free hosting can take around a minute
              after inactivity.
            </p>
          </>
        )}

        {apiStatus === 'ready' && <p>● Demo API is ready.</p>}

        {apiStatus === 'unavailable' && (
          <>
            <p>The demo API could not be reached. It may still be starting.</p>
            <button type="button" onClick={() => void refreshApiStatus()}>
              Try again
            </button>
          </>
        )}
      </section>

      <section className="tool-grid" aria-label="Rental estimation tools">
        <article className="panel">
          <div className="panel-heading">
            <p className="panel-number">01</p>
            <h2>Estimate a rent</h2>
            <p>Enter the attributes of one apartment.</p>
          </div>
          <form onSubmit={handlePrediction} className="form-grid">
            <CityField value={predictionForm.city} onChange={(city) => setPredictionForm({ ...predictionForm, city })} />
            <label>District<input value={predictionForm.district} onChange={(event) => setPredictionForm({ ...predictionForm, district: event.target.value })} minLength={1} maxLength={100} required /></label>
            <NumberField label="Rooms" value={predictionForm.rooms} min="1" max="20" onChange={(rooms) => setPredictionForm({ ...predictionForm, rooms })} />
            <NumberField label="Area, m²" value={predictionForm.areaSqm} min="1" max="1000" onChange={(areaSqm) => setPredictionForm({ ...predictionForm, areaSqm })} />
            <NumberField label="Floor" value={predictionForm.floor} min="0" max="200" onChange={(floor) => setPredictionForm({ ...predictionForm, floor })} />
            <NumberField label="Total floors" value={predictionForm.totalFloors} min="1" max="200" onChange={(totalFloors) => setPredictionForm({ ...predictionForm, totalFloors })} />
            <button type="submit" disabled={isPredicting || !isApiReady}>{!isApiReady ? 'Waiting for API…' : isPredicting ? 'Estimating…' : 'Estimate rent'}</button>
          </form>
          <ResultMessage error={predictionError}>{prediction && <div className="estimate-result"><span>Estimated monthly rent</span><strong>{formatAmd(prediction.predicted_monthly_rent_amd)}</strong><small>Model {prediction.model_version}</small></div>}</ResultMessage>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <p className="panel-number">02</p>
            <h2>Find lower estimates</h2>
            <p>Leave filters empty when they do not matter.</p>
          </div>
          <form onSubmit={handleRecommendations} className="form-grid">
            <CityField value={recommendationForm.city} onChange={(city) => setRecommendationForm({ ...recommendationForm, city })} />
            <NumberField label="Rooms (optional)" value={recommendationForm.rooms} min="1" max="20" required={false} onChange={(rooms) => setRecommendationForm({ ...recommendationForm, rooms })} />
            <NumberField label="Minimum area, m²" value={recommendationForm.minAreaSqm} min="1" max="1000" required={false} onChange={(minAreaSqm) => setRecommendationForm({ ...recommendationForm, minAreaSqm })} />
            <NumberField label="Maximum area, m²" value={recommendationForm.maxAreaSqm} min="1" max="1000" required={false} onChange={(maxAreaSqm) => setRecommendationForm({ ...recommendationForm, maxAreaSqm })} />
            <NumberField label="Maximum budget, AMD" value={recommendationForm.maxBudgetAmd} min="1" required={false} onChange={(maxBudgetAmd) => setRecommendationForm({ ...recommendationForm, maxBudgetAmd })} />
            <button type="submit" disabled={isLoadingRecommendations || !isApiReady}>{!isApiReady ? 'Waiting for API…' : isLoadingRecommendations ? 'Searching…' : 'Show lowest estimates'}</button>
          </form>
          <ResultMessage error={recommendationError}>{recommendations.length > 0 && <ol className="recommendation-list">{recommendations.map((item) => <li key={`${item.city}-${item.district}-${item.rooms}-${item.area_sqm}-${item.floor}`}><div><strong>{item.district}</strong><span>{item.rooms} rooms · {item.area_sqm} m² · floor {item.floor}/{item.total_floors}</span></div><b>{formatAmd(item.estimated_monthly_rent_amd)}</b></li>)}</ol>}</ResultMessage>
        </article>
      </section>
      <footer>Estimates describe asking rents in the project dataset; they are not an appraisal, guarantee, or financial advice.</footer>
    </main>
  )
}

function CityField({ value, onChange }: { value: City; onChange: (city: City) => void }) {
  return <label>City<select value={value} onChange={(event) => onChange(event.target.value as City)}><option value="Yerevan">Yerevan</option><option value="Gyumri">Gyumri</option></select></label>
}

function NumberField({ label, value, min, max, required = true, onChange }: { label: string; value: string; min: string; max?: string; required?: boolean; onChange: (value: string) => void }) {
  return <label>{label}<input type="number" value={value} min={min} max={max} step="1" required={required} onChange={(event) => onChange(event.target.value)} /></label>
}

function ResultMessage({ children, error }: { children: React.ReactNode; error: string | null }) {
  return error ? <p className="error-message">{error}</p> : <div aria-live="polite">{children}</div>
}

function optionalNumber(value: string): number | undefined { return value === '' ? undefined : Number(value) }

function formatAmd(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'AMD', maximumFractionDigits: 0 }).format(value)
}

export default App
