import { useState } from 'react'

function LoginScreen({ active, onBack }) {
  const [email, setEmail] = useState('')
  const [instagramUsername, setInstagramUsername] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    alert(`Login submitted for ${email || 'your email'}`)
  }

  return (
    <section className={`screen ${active ? 'active' : ''}`}>
      <div className="screen-card screen-card--narrow">
        <div className="screen-header">
          <button type="button" className="back-link" onClick={onBack}>
            ← Back
          </button>
          <div>
            <span className="eyebrow">Login to Visla</span>
            <h1>Welcome back.</h1>
            <p>Access your schedule, review upcoming events, and keep your day organized.</p>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="jane@visla.com"
              required
            />
          </label>
          <label className="form-field">
            <span>Instagram Username</span>
            <input
              type="text"
              value={instagramUsername}
              onChange={(event) => setInstagramUsername(event.target.value)}
              placeholder="@username"
              required
            />
          </label>
          <button className="primary-btn form-submit" type="submit">
            Sign in
          </button>
        </form>
      </div>
    </section>
  )
}

export default LoginScreen
