import { useState } from 'react'
import './App.css'
import WelcomeScreen from './WelcomeScreen.jsx'
import LoginScreen from './LoginScreen.jsx'
import SignupScreen from './SignupScreen.jsx'

function App() {
  const [screen, setScreen] = useState('welcome')

  return (
    <main className="app-shell">
      <div className="screen-container">
        <WelcomeScreen active={screen === 'welcome'} onSelect={setScreen} />
        <LoginScreen active={screen === 'login'} onBack={() => setScreen('welcome')} />
        <SignupScreen active={screen === 'signup'} onBack={() => setScreen('welcome')} />
      </div>
    </main>
  )
}

export default App
