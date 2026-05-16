export default function AboutPage() {
  return (
    <div className="page-wrapper">
      <div className="about-page">
        <h1>About Pridicto</h1>
        <p>
          Pridicto is an AI-powered Indian Railways route finder that uses a <strong>BFS graph algorithm</strong> 
          to discover optimal multi-hop train journeys — including connections other apps miss.
        </p>

        <h2>🧠 How the Algorithm Works</h2>
        <p>
          Stations are <strong>graph nodes</strong>. Trains are <strong>directed edges</strong> with departure/arrival time weights.
          BFS explores all paths from origin to destination up to 2 hops, 
          then scores each route by total time + connection wait penalty.
        </p>

        <h2>🔧 Tech Stack</h2>
        <table className="stack-table">
          <thead><tr><th>Layer</th><th>Technology</th><th>Cost</th></tr></thead>
          <tbody>
            <tr><td>Frontend</td><td>React + Vite + Framer Motion</td><td>Free</td></tr>
            <tr><td>Backend</td><td>Django + Django REST Framework</td><td>Free</td></tr>
            <tr><td>Host (FE)</td><td>Vercel</td><td>Free</td></tr>
            <tr><td>Host (BE)</td><td>Railway.app / Render.com</td><td>$5 credit/mo</td></tr>
            <tr><td>Database</td><td>Supabase PostgreSQL</td><td>Free 500MB</td></tr>
            <tr><td>Cache</td><td>Upstash Redis (REST)</td><td>Free 10k req/day</td></tr>
            <tr><td>Train Data</td><td>RapidAPI Indian Railways</td><td>Free 100-500/day</td></tr>
            <tr><td>AI Layer</td><td>Claude 3 Haiku (Anthropic)</td><td>Free credits</td></tr>
          </tbody>
        </table>

        <h2>🔑 Environment Variables Needed</h2>
        <p>Copy <code>backend/.env.example</code> → <code>backend/.env</code> and fill in:</p>
        <div className="env-block">
          <div><span className="env-comment"># Django</span></div>
          <div><span className="env-key">DJANGO_SECRET_KEY</span>=<span className="env-val">your-secret-key</span></div>
          <div style={{marginTop:'0.5rem'}}><span className="env-comment"># Supabase → supabase.com → Settings → API</span></div>
          <div><span className="env-key">SUPABASE_URL</span>=<span className="env-val">https://xxx.supabase.co</span></div>
          <div><span className="env-key">SUPABASE_ANON_KEY</span>=<span className="env-val">eyJ...</span></div>
          <div style={{marginTop:'0.5rem'}}><span className="env-comment"># Upstash → upstash.com → Redis → REST API</span></div>
          <div><span className="env-key">UPSTASH_REDIS_REST_URL</span>=<span className="env-val">https://xxx.upstash.io</span></div>
          <div><span className="env-key">UPSTASH_REDIS_REST_TOKEN</span>=<span className="env-val">AXxx...</span></div>
          <div style={{marginTop:'0.5rem'}}><span className="env-comment"># RapidAPI → rapidapi.com → "Indian Railway" → Subscribe free</span></div>
          <div><span className="env-key">RAPIDAPI_KEY</span>=<span className="env-val">your-rapidapi-key</span></div>
          <div style={{marginTop:'0.5rem'}}><span className="env-comment"># Anthropic → console.anthropic.com → API Keys</span></div>
          <div><span className="env-key">ANTHROPIC_API_KEY</span>=<span className="env-val">sk-ant-...</span></div>
          <div><span className="env-key">CLAUDE_MODEL</span>=<span className="env-val">claude-3-haiku-20240307</span></div>
        </div>

        <h2>🚀 Running Locally</h2>
        <p><strong>Backend:</strong></p>
        <div className="env-block">
          cd backend<br/>
          pip install -r requirements.txt<br/>
          copy .env.example .env  <span className="env-comment"># then fill in values</span><br/>
          python manage.py migrate<br/>
          python manage.py runserver
        </div>
        <p><strong>Frontend:</strong></p>
        <div className="env-block">
          cd frontend<br/>
          npm install<br/>
          npm run dev
        </div>
        <p>App runs at <strong>http://localhost:3000</strong> — backend at <strong>http://localhost:8000</strong></p>

        <h2>🤖 Best AI Model</h2>
        <p>
          Use <strong>claude-3-haiku-20240307</strong> — it's the fastest and cheapest Claude model, 
          perfect for intent parsing. It handles natural language like "avoid long waits" or 
          "Chhath Puja special trains" accurately. Falls back to regex if no API key is set.
        </p>
      </div>
    </div>
  )
}
