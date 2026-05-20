import api from '../api.js'
import {useEffect} from 'react'
import {useNavigate} from 'react-router-dom'
function SignupScreen({ active, onBack }) {
  

  const handleGoogleConnect = () => {
    const params = new URLSearchParams(window.location.search)
    const igId = params.get('ig_id')
    const sig = params.get("sig")
    window.location.href = `${import.meta.env.VITE_API_URL}/auth/google?ig_id=${igId}&sig=${sig}`
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

        <div className="auth-form">
          <button className="primary-btn form-submit" type="button" onClick={handleGoogleConnect}>
            Connect Google
          </button>
        </div>
      </div>
    </section>
  )
}

export default SignupScreen
