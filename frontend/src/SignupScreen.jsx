import { useState } from 'react'

function SignupScreen({ active, onBack }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    alert(`Sign up submitted for ${name || 'new user'}`)
  }

  return (
    <section className={`screen ${active ? 'active' : ''}`}>
      <div className="screen-card screen-card--narrow">
        <div className="screen-header">
          <button type="button" className="back-link" onClick={onBack}>
            ← Back
          </button>
          <div>
            <span className="eyebrow">Create account</span>
            <h1>Start with Visla.</h1>
            <p>Sign up now to organize appointments, reminders, and team availability.</p>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>Name</span>
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Jane Doe"
              required
            />
          </label>
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
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="********"
              required
            />
          </label>
          <button className="primary-btn form-submit" type="submit">
            Create account
          </button>
        </form>
      </div>
    </section>
  )
}

export default SignupScreen
