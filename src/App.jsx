import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <h1>Welcome to Eleven Bunker</h1>
      <button onClick={() => setCount(count + 1)}>
        Count: {count}
      </button>
      <p>Ready to build something amazing!</p>
    </div>
  )
}

export default App
