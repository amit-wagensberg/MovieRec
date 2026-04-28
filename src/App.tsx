/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export default function App() {
  return (
    <div className="min-h-screen w-full bg-[#0a0505] text-zinc-100 font-sans overflow-x-hidden flex flex-col p-4 md:p-8">
      {/* Header Navigation */}
      <nav className="flex justify-between items-center mb-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-orange-600 rounded-full flex items-center justify-center shadow-[0_0_15px_rgba(234,88,12,0.4)]">
            <span className="text-white font-bold">C</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tighter uppercase">CineVibe</h1>
        </div>
        <div className="hidden md:flex gap-6 text-xs uppercase tracking-[0.2em] font-medium text-zinc-500">
          <span className="text-orange-500 border-b border-orange-500 pb-1">DNA Analysis</span>
          <span className="hover:text-zinc-300 cursor-pointer transition-colors">History</span>
          <span className="hover:text-zinc-300 cursor-pointer transition-colors">Settings</span>
        </div>
      </nav>

      <div className="flex-1 grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left Column: Letterboxd DNA */}
        <div className="md:col-span-3 flex flex-col gap-6">
          <div className="p-6 rounded-2xl bg-zinc-900/50 border border-zinc-800/50">
            <h2 className="text-xs font-bold uppercase tracking-widest text-zinc-500 mb-4">Cinematic DNA</h2>
            <div className="flex flex-wrap gap-2 mb-4">
              <span className="px-3 py-1 rounded-full bg-orange-600/10 text-orange-400 text-[10px] border border-orange-600/20">NEO-NOIR</span>
              <span className="px-3 py-1 rounded-full bg-zinc-800 text-zinc-400 text-[10px]">SLOW BURN</span>
              <span className="px-3 py-1 rounded-full bg-zinc-800 text-zinc-400 text-[10px]">ANALOG HORROR</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-[11px] text-zinc-500 uppercase tracking-tighter">
                <span>Aesthetic Bias</span>
                <span>88% Dark</span>
              </div>
              <div className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
                <div className="h-full bg-orange-600 w-[88%] shadow-[0_0_8px_rgba(234,88,12,0.5)]"></div>
              </div>
            </div>
          </div>

          <div className="flex-1 p-6 rounded-2xl bg-zinc-900/30 border border-zinc-800/50 flex flex-col">
            <h2 className="text-xs font-bold uppercase tracking-widest text-zinc-500 mb-6">Taste Foundations</h2>
            <div className="space-y-4 overflow-hidden">
              <div className="flex items-center gap-3">
                <div className="w-10 h-14 bg-zinc-800 rounded shadow-lg shrink-0"></div>
                <div>
                  <p className="text-xs font-bold">Stalker (1979)</p>
                  <p className="text-[10px] text-zinc-500">Tarkovsky</p>
                </div>
              </div>
              <div className="flex items-center gap-3 opacity-60">
                <div className="w-10 h-14 bg-zinc-800 rounded shrink-0"></div>
                <div>
                  <p className="text-xs font-bold">Cure (1997)</p>
                  <p className="text-[10px] text-zinc-500">Kurosawa</p>
                </div>
              </div>
              <div className="flex items-center gap-3 opacity-40">
                <div className="w-10 h-14 bg-zinc-800 rounded shrink-0"></div>
                <div>
                  <p className="text-xs font-bold">Incendies</p>
                  <p className="text-[10px] text-zinc-500">Villeneuve</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Middle Column: Hero Recommendation */}
        <div className="md:col-span-6 flex flex-col">
          <div className="flex flex-wrap justify-between items-center mb-6 gap-4">
            <h3 className="text-lg font-light italic text-zinc-400">What's the current mood?</h3>
            <div className="flex flex-wrap gap-2">
              <button className="px-4 py-1.5 rounded-full bg-orange-600 text-white text-xs font-bold shadow-lg">MELANCHOLY</button>
              <button className="px-4 py-1.5 rounded-full bg-zinc-800 hover:bg-zinc-700 transition-colors text-zinc-400 text-xs font-bold">ADRENALINE</button>
              <button className="px-4 py-1.5 rounded-full bg-zinc-800 hover:bg-zinc-700 transition-colors text-zinc-400 text-xs font-bold">COMFORT</button>
            </div>
          </div>

          <div className="relative flex-1 group min-h-[500px]">
             <div className="absolute -inset-1 bg-gradient-to-r from-orange-600/50 to-purple-600/50 rounded-3xl blur-xl opacity-30"></div>
             <div className="relative h-full w-full bg-zinc-900 rounded-3xl border border-zinc-700/50 flex flex-col items-center justify-center p-6 md:p-12 overflow-hidden shadow-2xl">
              {/* Poster Placeholder */}
              <div className="w-48 h-72 md:w-64 md:h-96 bg-gradient-to-br from-zinc-800 to-zinc-950 rounded-xl mb-8 shadow-2xl border border-zinc-700 flex flex-col items-center justify-center relative overflow-hidden shrink-0">
                 <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-orange-500 via-transparent to-transparent"></div>
                 <div className="w-32 md:w-48 h-1 bg-orange-600/30 blur-md mb-2"></div>
                 <div className="w-24 md:w-32 h-1 bg-orange-600/20 blur-sm"></div>
              </div>
              
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-2 uppercase italic text-center">Perfect Blue</h2>
              <p className="text-orange-400 text-xs md:text-sm font-medium tracking-widest mb-6 uppercase text-center">Recommended for your Melancholy Mood</p>
              <div className="max-w-md">
                <p className="text-center text-zinc-400 leading-relaxed italic text-base md:text-lg">
                  "A neon-soaked psychological descent into the blurred lines of identity and fame that resonates with your love for high-stakes Neo-Noir."
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: System Status */}
        <div className="md:col-span-3 flex flex-col gap-6">
          <div className="p-6 rounded-2xl bg-zinc-900/50 border border-zinc-800/50">
            <h2 className="text-xs font-bold uppercase tracking-widest text-zinc-500 mb-4">Analysis Filters</h2>
            <ul className="space-y-4">
              <li className="flex justify-between items-center">
                <span className="text-xs text-zinc-400 font-mono">Min Rating {'>'} 4.0</span>
                <div className="w-4 h-4 rounded bg-orange-600 flex items-center justify-center"><div className="w-1.5 h-1.5 bg-white rounded-full"></div></div>
              </li>
              <li className="flex justify-between items-center">
                <span className="text-xs text-zinc-400 font-mono">Exclude Watched</span>
                <div className="w-4 h-4 rounded bg-orange-600 flex items-center justify-center"><div className="w-1.5 h-1.5 bg-white rounded-full"></div></div>
              </li>
              <li className="flex justify-between items-center">
                <span className="text-xs text-zinc-400 font-mono">AI Active</span>
                <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]"></div>
              </li>
            </ul>
          </div>

          <div className="flex-1 p-6 rounded-2xl bg-zinc-900/20 border border-zinc-800/30">
            <h2 className="text-xs font-bold uppercase tracking-widest text-zinc-500 mb-4">Metadata Context</h2>
            <div className="space-y-6">
              <div>
                 <p className="text-[10px] uppercase text-zinc-600 mb-1 tracking-widest">Engine Logic</p>
                 <p className="text-xs leading-relaxed text-zinc-500">Synthesizing <span className="text-orange-300">142 high-rated titles</span> to find cinematic overlaps in cinematography and pacing.</p>
              </div>
              <div className="pt-4 border-t border-zinc-800/50">
                <p className="text-[10px] uppercase text-zinc-600 mb-2 tracking-widest">Recent Activity</p>
                <div className="h-12 w-full bg-zinc-900/50 rounded flex items-center px-3 mb-2">
                  <div className="w-1 h-1 bg-orange-600 rounded-full mr-3 shadow-[0_0_4px_orange]"></div>
                  <p className="text-[10px] text-zinc-500">watched.csv updated 2h ago</p>
                </div>
                <div className="h-12 w-full bg-zinc-900/50 rounded flex items-center px-3">
                  <div className="w-1 h-1 bg-zinc-600 rounded-full mr-3"></div>
                  <p className="text-[10px] text-zinc-500">ratings.csv stable</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Status Bar */}
      <footer className="mt-8 flex flex-col sm:flex-row justify-between items-center py-4 border-t border-zinc-900 text-[10px] font-mono text-zinc-600 gap-4 transition-all">
        <div>DEPLOYED: VITE REACT • V0.4.2</div>
        <div className="flex gap-4">
          <span>GEMINI-1.5-FLASH: OK</span>
          <span>TMDB-POSTERS: OK</span>
        </div>
      </footer>
    </div>
  );
}
