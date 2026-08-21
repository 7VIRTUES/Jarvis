from __future__ import annotations


def models_dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jarvis Models Center</title>
  <style>
    :root { color-scheme:light; --bg:#edf2f7; --surface:#fff; --soft:#f7fafc; --border:#c5d2df; --text:#172235; --muted:#526276; --accent:#155e9b; --dark:#0d4777; --warn:#8a5200; --danger:#a12626; --focus:#ffbf47; }
    * { box-sizing:border-box; } body { margin:0; background:var(--bg); color:var(--text); font:16px/1.5 "Segoe UI",system-ui,sans-serif; }
    header { background:#14263b; color:#fff; padding:24px clamp(18px,4vw,48px); border-bottom:4px solid #5e87ad; }
    header h1 { margin:0 0 5px; } header p { margin:0; color:#dce8f4; }
    main { width:min(1300px,100%); margin:auto; padding:22px clamp(14px,3vw,36px) 48px; display:grid; gap:18px; }
    section,.panel { background:var(--surface); border:1px solid var(--border); border-radius:9px; padding:18px; box-shadow:0 2px 8px rgba(15,35,55,.06); }
    .banner { border-left:6px solid var(--warn); background:#fff9e9; } .nav,.actions { display:flex; flex-wrap:wrap; gap:9px; align-items:center; } .nav { justify-content:space-between; }
    .two { display:grid; grid-template-columns:1fr 1fr; gap:18px; align-items:start; } .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:10px; }
    .card,.metric,.status { border:1px solid var(--border); border-radius:7px; padding:12px; background:var(--soft); overflow-wrap:anywhere; }
    .metric { display:grid; gap:2px; } .metric strong { font-size:1.3rem; } .status { min-height:44px; white-space:pre-wrap; }
    label { display:grid; gap:5px; font-weight:650; margin:9px 0; } input,select,button { font:inherit; } input,select { width:100%; padding:9px 10px; border:1px solid #93a3b5; border-radius:5px; }
    button,.button-link { border:1px solid var(--accent); border-radius:5px; padding:9px 13px; background:var(--accent); color:#fff; font-weight:650; cursor:pointer; text-decoration:none; }
    button.secondary { background:#fff; color:var(--accent); } button.warning { background:var(--warn); border-color:var(--warn); } button.danger { background:var(--danger); border-color:var(--danger); } button:disabled { opacity:.55; cursor:not-allowed; }
    a { color:var(--accent); } header a { color:#fff; } a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible { outline:3px solid var(--focus); outline-offset:2px; }
    h2,h3 { margin-top:0; } .muted { color:var(--muted); font-size:.92rem; } dl { display:grid; grid-template-columns:minmax(155px,.4fr) 1fr; gap:7px 12px; margin:0; } dt { font-weight:700; } dd { margin:0; }
    .pill { display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.8rem; font-weight:700; }
    .pill.active { background:#dcfce7; color:#14532d; }
    .pill.idle { background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; }
    .pill.cancelling { background:#fee2e2; color:#991b1b; }
    @media(max-width:820px){ .two { grid-template-columns:1fr; } } @media(max-width:560px){ dl { grid-template-columns:1fr; } .actions>* { width:100%; } }
  </style>
</head>
<body>
<header><div class="nav"><div><h1>Jarvis Models Center</h1><p>Controlled local generation · Explicit runtime control · Safe interruption</p></div><div class="actions"><a class="button-link" href="/assistant">Assistant</a><a class="button-link" href="/dashboard">Dashboard</a><a class="button-link" href="/knowledge">Knowledge Library</a><a class="button-link" href="/memory">Memory Center</a></div></div></header>
<main>
  <section class="banner"><h2>Generation safety boundaries</h2><ul>
    <li>Local generation is disabled by default and uses only the fixed IPv4 loopback provider.</li>
    <li>No cloud provider, API key, model installation, model pull, model start, model training, tools, or actions are supported.</li>
    <li>Active generation requests can be explicitly stopped at any time without process termination or model deletion.</li>
    <li>Thinking is discarded and never returned or persisted. Prompts, outputs, and provider bodies are not persisted.</li>
    <li>Private sessions are ephemeral and are not audited. Full prompt preview is blocked in private sessions.</li>
    <li>The deterministic response remains available. Generation never runs automatically or in the background.</li>
    <li>Generation and Knowledge Library embeddings are configured separately.</li>
  </ul></section>
  <div id="page-status" class="status" role="status" aria-live="polite">No provider or database read has been requested from this page.</div>

  <!-- Runtime Section -->
  <section>
    <div class="nav">
      <div>
        <h2>Local Generation Runtime</h2>
        <p class="muted">Live in-memory runtime control for active client requests. Concurrency is strictly 1.</p>
      </div>
      <button id="refresh-runtime" class="secondary" type="button">Refresh runtime status</button>
    </div>
    <div id="runtime-metrics" class="grid" style="margin-top:10px;"></div>
    <div id="runtime-stop-panel" style="margin-top:14px; display:none; padding:14px; border:1px solid #f87171; background:#fef2f2; border-radius:7px;">
      <h3 style="color:#991b1b; margin-top:0;">Active Generation In Flight</h3>
      <p style="margin:0 0 10px; font-size:0.9rem;">An active generation request is running. You can safely abort the client connection without stopping Ollama or disabling generation.</p>
      <label>Type CANCEL LOCAL GENERATION<input id="cancel-confirm" autocomplete="off" placeholder="CANCEL LOCAL GENERATION"></label>
      <button id="cancel-btn" class="danger" type="button">Stop active generation</button>
      <div id="cancel-result" class="status" style="margin-top:8px;">No cancellation requested.</div>
    </div>
  </section>

  <section><div class="nav"><div><h2>Generation status</h2><p class="muted">Manual refresh reads local metadata only and never contacts Ollama.</p></div><button id="refresh" class="secondary" type="button">Refresh status, profiles, and run history</button></div><div id="status-metrics" class="grid"></div></section>
  <div class="two">
    <section><h2>Probe and configure</h2><p class="muted">Probe sends fixed server-owned content only. Configure probes first, then atomically enables the selected profile.</p>
      <label>Local Ollama model name<input id="model" maxlength="120" autocomplete="off"></label>
      <button id="probe" type="button">Probe local model</button><div id="probe-result" class="status">No probe requested.</div>
      <label>Context character limit<input id="context-limit" type="number" min="8000" max="120000" value="24000"></label>
      <label>Maximum output characters<input id="output-limit" type="number" min="500" max="12000" value="4000"></label>
      <label>Temperature<input id="temperature" type="number" min="0" max="1" step="0.1" value="0.2"></label>
      <label>Keep-alive seconds<input id="keep-alive" type="number" min="0" max="3600" value="300"></label>
      <label>Type ENABLE LOCAL GENERATION<input id="configure-confirm" autocomplete="off"></label>
      <button id="configure" type="button">Configure and enable generation</button>
    </section>
    <section><h2>Disable and safe unload</h2>
      <label>Type DISABLE LOCAL GENERATION<input id="disable-confirm" autocomplete="off"></label>
      <button id="disable" class="warning" type="button">Disable generation</button>
      <p class="muted">Disabling preserves profiles and metadata-only run history and does not contact the provider.</p>
      <label>Profile for safe unload<select id="unload-profile"><option value="">Active profile</option></select></label>
      <label>Type UNLOAD LOCAL MODEL<input id="unload-confirm" autocomplete="off"></label>
      <button id="unload" class="danger" type="button">Request safe API unload</button>
      <p class="muted">Safe unload uses fixed API keep-alive semantics. It does not kill a process, stop Ollama, use a CLI, or delete a model.</p>
      <div id="admin-result" class="status">No administrative action requested.</div>
    </section>
  </div>
  <section><h2>Generation profiles</h2><p class="muted">Local configuration metadata only. Embedding profiles are managed separately in the Knowledge Library.</p><div id="profiles" class="grid"><div class="status">Use manual refresh to load profiles.</div></div></section>
  <section><h2>Generation run history</h2><p class="muted">Metadata only: no requests, prompts, generated or deterministic outputs, memory, knowledge, web content, prior context, thinking, tool calls, or provider bodies.</p><div id="runs" class="grid"><div class="status">Use manual refresh to load run metadata.</div></div></section>
</main>
<script>
  let currentActiveRuntimeId = null;
  const byId=(id)=>document.getElementById(id);
  const node=(tag,text,className)=>{const item=document.createElement(tag);if(text!==undefined)item.textContent=String(text);if(className)item.className=className;return item;};
  function fields(container,rows){const dl=node('dl');rows.forEach(([label,value])=>{dl.append(node('dt',label),node('dd',value===null||value===undefined||value===''?'—':Array.isArray(value)?value.join(', '):value));});container.append(dl);}
  async function api(path,options={}){const response=await fetch(path,{...options,headers:{'Content-Type':'application/json',...(options.headers||{})}});const data=await response.json().catch(()=>({detail:{message:'Request failed.'}}));if(!response.ok){const detail=data.detail;throw new Error(typeof detail==='string'?detail:(detail&&detail.message)||(detail&&detail.error)||'Request failed.');}return data;}
  function setPage(message){byId('page-status').textContent=message;}

  function renderRuntime(runtime){
    const target=byId('runtime-metrics');
    target.replaceChildren();
    const stopPanel=byId('runtime-stop-panel');
    if (!runtime || !runtime.active) {
      currentActiveRuntimeId = null;
      stopPanel.style.display = 'none';
      [
        ['Runtime state', 'Idle'],
        ['Phase', 'idle'],
        ['Active model', 'None'],
        ['Concurrency slot', '0 / 1 occupied'],
        ['Cancellable', '—']
      ].forEach(([label,value])=>{
        const card=node('div',undefined,'metric');
        card.append(node('span',label),node('strong',value));
        target.append(card);
      });
      return;
    }

    currentActiveRuntimeId = runtime.runtimeId;
    stopPanel.style.display = 'block';
    [
      ['Runtime state', runtime.phase === 'cancelling' ? 'Cancelling' : 'Active'],
      ['Phase', runtime.phase || 'generating'],
      ['Active model', runtime.modelName || '—'],
      ['Purpose', runtime.purpose || '—'],
      ['Runtime ID', (runtime.runtimeId || '').slice(0, 12) + '...'],
      ['Started at', runtime.startedAt || '—'],
      ['Cancellation requested', runtime.cancellationRequested ? 'Yes' : 'No']
    ].forEach(([label,value])=>{
      const card=node('div',undefined,'metric');
      card.append(node('span',label),node('strong',value));
      target.append(card);
    });
  }

  function renderStatus(status){const target=byId('status-metrics');target.replaceChildren();[
    ['Implemented',status.implemented?'yes':'no'],['Runtime enabled',status.enabled?'yes':'no'],['Provider',status.provider],['Fixed endpoint',status.fixedEndpoint],['Model',status.modelName],['Profile',status.activeProfileId],['Context limit',status.contextCharacterLimit],['Output limit',status.maximumOutputCharacters],['Temperature',status.temperature],['Keep alive',status.keepAliveSeconds],['Active / maximum',`${status.activeGenerationCount} / ${status.maximumConcurrency}`],['Recent completed / failed',`${status.recentCompletedCount} / ${status.recentFailedCount}`],['Automatic / background','no / no'],['Queue / retry / cancel','no / no / yes'],['Tools / cloud / API keys','no / no / no'],['Prompt / output persistence','no / no']
  ].forEach(([label,value])=>{const card=node('div',undefined,'metric');card.append(node('span',label),node('strong',value));target.append(card);});}

  function renderProfiles(profiles){const target=byId('profiles'),select=byId('unload-profile');target.replaceChildren();select.replaceChildren();const active=node('option','Active profile');active.value='';select.append(active);if(!profiles.length)target.append(node('div','No configured generation profiles.','status'));profiles.forEach((profile)=>{const card=node('article',undefined,'card');card.append(node('h3',profile.modelName));fields(card,[['Profile ID',profile.profileId],['Provider',profile.provider],['Context limit',profile.contextCharacterLimit],['Output limit',profile.maximumOutputCharacters],['Temperature',profile.temperature],['Keep alive',profile.keepAliveSeconds],['Structured output',profile.structuredOutputMode],['Created',profile.createdAt],['Last used',profile.lastUsedAt]]);target.append(card);const option=node('option',`${profile.modelName} (${profile.profileId})`);option.value=profile.profileId;select.append(option);});}

  function renderRuns(runs){const target=byId('runs');target.replaceChildren();if(!runs.length)target.append(node('div','No generation run metadata.','status'));runs.forEach((run)=>{const card=node('article',undefined,'card');card.append(node('h3',`${run.purpose} · ${run.status}`));fields(card,[['Run ID',run.runId],['Response ID',run.responseId],['Agent',run.agentId],['Profile',run.profileId],['Requested / actual',`${run.requestedMode} / ${run.actualMode}`],['Prompt hash',run.promptHash],['Prompt characters',run.promptCharacterCount],['Context item counts',`memory ${run.memoryItemCount}; knowledge ${run.knowledgeChunkCount}; web ${run.webSourceCount}`],['Output characters',run.outputCharacterCount],['Fallback',run.fallbackUsed?'yes':'no'],['Thinking discarded',run.thinkingDiscarded?'yes':'no'],['Error',run.errorCode],['Created',run.createdAt],['Completed',run.completedAt],['Content persisted','no']]);target.append(card);});}

  async function refreshRuntime(){
    try {
      const runtime = await api('/api/generation/active');
      renderRuntime(runtime);
    } catch(err) {
      renderRuntime(null);
    }
  }

  async function refresh(){
    byId('refresh').disabled=true;
    setPage('Loading local generation metadata. Ollama is not contacted.');
    try{
      const [status,runtime,profiles,runs]=await Promise.all([
        api('/api/generation/status'),
        api('/api/generation/active'),
        api('/api/generation/profiles'),
        api('/api/generation/runs?limit=50&offset=0')
      ]);
      renderStatus(status);
      renderRuntime(runtime);
      renderProfiles(profiles);
      renderRuns(runs);
      setPage('Local generation metadata refreshed. No provider call occurred.');
    }catch(error){
      setPage(error.message);
    }finally{
      byId('refresh').disabled=false;
    }
  }

  byId('refresh').addEventListener('click',refresh);
  byId('refresh-runtime').addEventListener('click',refreshRuntime);

  byId('cancel-btn').addEventListener('click', async()=>{
    byId('cancel-btn').disabled=true;
    byId('cancel-result').textContent='Sending cancellation request...';
    try {
      const result = await api('/api/generation/cancel', {
        method: 'POST',
        body: JSON.stringify({
          confirmation: byId('cancel-confirm').value,
          expectedRuntimeId: currentActiveRuntimeId,
          actor: 'local_user'
        })
      });
      byId('cancel-confirm').value = '';
      byId('cancel-result').textContent = `Cancellation status: ${result.status}. Runtime: ${result.runtimeId || 'none'}.`;
      setPage('Cancellation request submitted.');
      setTimeout(refreshRuntime, 600);
    } catch(error) {
      byId('cancel-result').textContent = error.message;
      setPage('Cancellation failed safely.');
    } finally {
      byId('cancel-btn').disabled=false;
    }
  });

  byId('probe').addEventListener('click',async()=>{byId('probe').disabled=true;byId('probe-result').textContent='Explicit fixed-content probe in progress.';try{const result=await api('/api/generation/probe',{method:'POST',body:JSON.stringify({modelName:byId('model').value,actor:'local_user'})});byId('probe-result').textContent=`Probe status: ${result.status}; model: ${result.modelName}; run: ${result.runId}. Generation was not enabled.`;setPage('Explicit local model probe completed.');}catch(error){byId('probe-result').textContent=error.message;setPage('Probe failed safely.');}finally{byId('probe').disabled=false;refreshRuntime();}});
  byId('configure').addEventListener('click',async()=>{byId('configure').disabled=true;setPage('Explicit configure request in progress. Prior settings remain on failure.');try{const status=await api('/api/generation/configure',{method:'POST',body:JSON.stringify({modelName:byId('model').value,contextCharacterLimit:Number(byId('context-limit').value),maximumOutputCharacters:Number(byId('output-limit').value),temperature:Number(byId('temperature').value),keepAliveSeconds:Number(byId('keep-alive').value),confirmation:byId('configure-confirm').value,actor:'local_user'})});renderStatus(status);byId('configure-confirm').value='';setPage('Local generation configured and enabled after a successful explicit probe.');await refresh();}catch(error){setPage(error.message);}finally{byId('configure').disabled=false;refreshRuntime();}});
  byId('disable').addEventListener('click',async()=>{byId('disable').disabled=true;try{const status=await api('/api/generation/disable',{method:'POST',body:JSON.stringify({confirmation:byId('disable-confirm').value,actor:'local_user'})});renderStatus(status);byId('disable-confirm').value='';byId('admin-result').textContent='Generation disabled. Configuration and metadata-only history were preserved. No provider call occurred.';setPage('Local generation disabled.');}catch(error){byId('admin-result').textContent=error.message;}finally{byId('disable').disabled=false;refreshRuntime();}});
  byId('unload').addEventListener('click',async()=>{byId('unload').disabled=true;try{const result=await api('/api/generation/unload',{method:'POST',body:JSON.stringify({confirmation:byId('unload-confirm').value,modelProfileId:byId('unload-profile').value||null,actor:'local_user'})});byId('unload-confirm').value='';byId('admin-result').textContent=`Safe API unload requested for ${result.model}; no process was killed and no model was deleted.`;setPage('Safe fixed-API unload completed.');}catch(error){byId('admin-result').textContent=error.message;}finally{byId('unload').disabled=false;refreshRuntime();}});
</script>
</body>
</html>"""
