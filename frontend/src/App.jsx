import { useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    const trimmed = query.trim()
    if (!trimmed) return

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmed }),
      })

      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`)
      }

      const data = await response.json()
      setAnswer(data.answer || "I don't know")
      setSources(Array.isArray(data.sources) ? data.sources : [])
    } catch (err) {
      setError(err.message || 'Something went wrong')
      setAnswer('')
      setSources([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container">
      <h1>AI Answer Engine</h1>
      <p className="subtitle">Ask a question and get an answer grounded in live web sources.</p>

      <form onSubmit={handleSubmit} className="query-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What is Dijkstra's Algorithm?"
          aria-label="Query"
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Searching…' : 'Ask'}
        </button>
      </form>

      {loading && <div className="spinner" aria-label="Loading" />}
      {error && <p className="error">{error}</p>}

      {answer && (
        <section className="result-card">
          <h2>Answer</h2>
          <p>{answer}</p>
        </section>
      )}

      {sources.length > 0 && (
        <section className="result-card">
          <h2>Sources</h2>
          <ol>
            {sources.map((source, index) => (
              <li key={`${source.link}-${index}`}>
                <a href={source.link} target="_blank" rel="noreferrer">
                  {source.title}
                </a>
              </li>
            ))}
          </ol>
        </section>
      )}
    </main>
  )
}

export default App
