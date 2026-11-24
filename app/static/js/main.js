// Controle de Modais e Requisicoes Assincronas (Funcao C2)

async function abrirModal(tmdbId) {
    const modal = document.getElementById("movieModal");
    const content = document.getElementById("modalContent");
    
    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");

    content.innerHTML = `
        <div class="flex flex-col items-center justify-center py-20 text-slate-400">
            <i data-lucide="loader-2" class="w-10 h-10 animate-spin text-amber-400 mb-3"></i>
            <p class="text-sm">Carregando ficha técnica consolidada...</p>
        </div>
    `;
    lucide.createIcons();

    try {
        const response = await fetch(`/api/filmes/${tmdbId}`);
        if (!response.ok) throw new Error("Erro ao carregar detalhes");
        const f = await response.json();

        // Renderiza modal da Funcao C2
        content.innerHTML = `
            <div class="space-y-6">
                <!-- Cabecalho: Pôster + Titulo + Scores -->
                <div class="flex flex-col sm:flex-row gap-6">
                    <div class="w-full sm:w-44 aspect-[2/3] bg-slate-950 rounded-xl overflow-hidden flex-shrink-0 shadow-xl border border-slate-800">
                        ${f.poster_path ? `<img src="https://image.tmdb.org/t/p/w500${f.poster_path}" alt="${f.titulo}" class="w-full h-full object-cover">` : `<div class="w-full h-full flex items-center justify-center text-slate-600">Sem pôster</div>`}
                    </div>

                    <div class="flex-grow space-y-3">
                        <div class="flex items-start justify-between gap-4">
                            <div>
                                <span class="text-xs uppercase tracking-wider text-amber-400 font-mono font-semibold">Oscar ${f.ano_edicao}</span>
                                <h2 class="text-2xl font-black text-white leading-tight">${f.titulo}</h2>
                                <p class="text-xs text-slate-400 italic">${f.titulo_original} · ${f.duracao_min ? f.duracao_min + ' min' : 'Duração N/A'}</p>
                            </div>
                            <div class="text-right flex-shrink-0 bg-slate-950/80 border border-amber-500/30 p-2.5 rounded-xl">
                                <span class="block text-2xl font-black text-amber-400 font-mono">${Number(f.oscar_buzz_score).toFixed(1)}</span>
                                <span class="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Buzz Score</span>
                            </div>
                        </div>

                        <!-- Metricas Criticas -->
                        <div class="grid grid-cols-3 gap-2 pt-1">
                            <div class="bg-slate-950 border border-slate-800/80 p-2 rounded-lg text-center">
                                <span class="block text-[10px] uppercase text-slate-500 font-bold">IMDb Rating</span>
                                <span class="text-sm font-black text-yellow-400 font-mono">${f.imdb_rating ? f.imdb_rating + ' / 10' : 'N/A'}</span>
                            </div>
                            <div class="bg-slate-950 border border-slate-800/80 p-2 rounded-lg text-center">
                                <span class="block text-[10px] uppercase text-slate-500 font-bold">Metascore</span>
                                <span class="text-sm font-black text-emerald-400 font-mono">${f.metascore ? f.metascore + ' / 100' : 'N/A'}</span>
                            </div>
                            <div class="bg-slate-950 border border-slate-800/80 p-2 rounded-lg text-center">
                                <span class="block text-[10px] uppercase text-slate-500 font-bold">Popularidade</span>
                                <span class="text-sm font-black text-blue-400 font-mono">${Number(f.popularidade).toFixed(1)}</span>
                            </div>
                        </div>

                        <!-- Generos -->
                        <div class="flex flex-wrap gap-1.5 pt-1">
                            ${f.generos.map(g => `<span class="text-xs bg-slate-800 text-slate-300 px-2.5 py-0.5 rounded-md font-medium">${g.nome}</span>`).join('')}
                        </div>
                    </div>
                </div>

                <!-- Sinopse -->
                <div class="space-y-1">
                    <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Sinopse</h4>
                    <p class="text-sm text-slate-300 leading-relaxed">${f.sinopse || 'Sinopse não informada.'}</p>
                </div>

                <!-- Onde Assistir no Brasil (Disponibilidade) -->
                <div class="space-y-2 pt-2 border-t border-slate-800">
                    <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Onde Assistir no Brasil (Catálogo Atual)</h4>
                    ${f.streamings && f.streamings.length > 0 ? `
                        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                            ${f.streamings.map(st => `
                                <div class="bg-slate-950 border border-slate-800/90 p-2 rounded-lg flex items-center space-x-2">
                                    ${st.logo_path ? `<img src="https://image.tmdb.org/t/p/w92${st.logo_path}" alt="${st.nome}" class="w-7 h-7 rounded object-cover">` : ''}
                                    <div class="min-w-0">
                                        <p class="text-xs font-bold text-white truncate">${st.nome}</p>
                                        <span class="text-[10px] text-amber-400 font-semibold uppercase tracking-wider">${st.modalidade}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : `<p class="text-xs text-slate-500 italic">Nenhuma plataforma de streaming identificada no momento (Em cartaz nos cinemas ou distribuição física).</p>`}
                </div>

                <!-- Candidaturas ao Oscar -->
                ${f.candidaturas && f.candidaturas.length > 0 ? `
                    <div class="space-y-2 pt-2 border-t border-slate-800">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Candidaturas Oficiais da Temporada</h4>
                        <div class="flex flex-wrap gap-2">
                            ${f.candidaturas.map(c => `
                                <span class="text-xs bg-slate-950 border ${c.status === 'VENCEDOR' ? 'border-amber-500/60 text-amber-300' : (c.status === 'INDICADO' ? 'border-blue-500/50 text-blue-300' : 'border-slate-700 text-slate-400')} px-3 py-1.5 rounded-lg flex items-center space-x-1.5 font-medium">
                                    <i data-lucide="${c.status === 'VENCEDOR' ? 'trophy' : (c.status === 'INDICADO' ? 'award' : 'sparkles')}" class="w-3.5 h-3.5"></i>
                                    <span>${c.categoria_nome} ${c.profissional_nome ? '— ' + c.profissional_nome : ''}</span>
                                    <strong class="uppercase text-[10px] ml-1">(${c.status})</strong>
                                </span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- Elenco & Direção -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800">
                    <div>
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono mb-2">Equipe Chave</h4>
                        <ul class="text-xs space-y-1 text-slate-300">
                            ${f.equipe.map(eq => `<li><span class="text-slate-500 uppercase">${eq.funcao}:</span> <strong class="text-white">${eq.nome}</strong></li>`).join('')}
                        </ul>
                    </div>

                    <div>
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono mb-2">Elenco Principal (Top 10)</h4>
                        <ul class="text-xs space-y-1 text-slate-300">
                            ${f.elenco.slice(0, 6).map(at => `<li><strong class="text-white">${at.nome}</strong> <span class="text-slate-500">como ${at.character_name || 'personagem'}</span></li>`).join('')}
                        </ul>
                    </div>
                </div>

            </div>
        `;
        lucide.createIcons();

    } catch (err) {
        content.innerHTML = `
            <div class="p-8 text-center space-y-3">
                <i data-lucide="alert-triangle" class="w-10 h-10 text-red-400 mx-auto"></i>
                <p class="text-sm text-red-300">Não foi possível carregar os detalhes do filme.</p>
                <button onclick="fecharModal()" class="px-4 py-2 bg-slate-800 text-xs rounded-lg text-white">Fechar</button>
            </div>
        `;
        lucide.createIcons();
    }
}

function fecharModal() {
    const modal = document.getElementById("movieModal");
    modal.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
}

// Fechar modal ao clicar fora
window.addEventListener("click", (e) => {
    const modal = document.getElementById("movieModal");
    if (e.target === modal) {
        fecharModal();
    }
});
