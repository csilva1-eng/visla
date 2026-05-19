function WelcomeScreen({ active, onSelect }) {
  return (
    <section className={`screen ${active ? 'active' : ''}`}>
      <div className="screen-card">
        <div>
          <span className="eyebrow">Welcome to Visla</span>
          <h1>Scheduling made simple.</h1>
          <p>
            Start by creating an account or logging in to manage meetings,
            reminders, and daily planning with a calm, focused experience.
          </p>
        </div>

        <div className="button-group">
          <button className="primary-btn" type="button" onClick={() => onSelect('signup')}>
            Create account
          </button>
          <button className="secondary-btn" type="button" onClick={() => onSelect('login')}>
            Login
          </button>
        </div>
      </div>
    </section>
  )
}

export default WelcomeScreen
