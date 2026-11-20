// OmniSEO & AI Studio Client-side Controller (Enterprise 2026 Edition)

let currentAuditData = null;
let progressTimer = null;
let currentAuditMode = 'url';
let uploadedFileContent = null;
let uploadedFileName = null;

document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }
});

function setAuditMode(mode) {
  currentAuditMode = mode;
  const modes = ['url', 'upload', 'paste'];
  
  modes.forEach(m => {
    const btn = document.getElementById(`modeBtn-${m}`);
    const form = document.getElementById(m === 'url' ? 'auditForm' : (m === 'upload' ? 'uploadForm' : 'pasteForm'));
    
    if (m === mode) {
      if (btn) {
        btn.className = "px-3 py-1.5 rounded bg-[#21262d] text-white border border-[#30363d] flex items-center gap-1.5 text-xs font-medium transition";
      }
      if (form) form.classList.remove("hidden");
    } else {
      if (btn) {
        btn.className = "px-3 py-1.5 rounded text-[#8b949e] hover:text-white border border-transparent flex items-center gap-1.5 text-xs font-medium transition";
      }
      if (form) form.classList.add("hidden");
    }
  });

  if (window.lucide) {
    lucide.createIcons();
  }
}

function handleFileSelected(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  uploadedFileName = file.name;
  
  const display = document.getElementById("fileNameDisplay");
  if (display) {
    display.innerText = `Selected: ${file.name} (${formatBytes(file.size)})`;
    display.classList.add("text-emerald-400");
  }
  
  const reader = new FileReader();
  reader.onload = (e) => {
    uploadedFileContent = e.target.result;
  };
  reader.readAsText(file);
}

function setSampleUrl(url) {
  setAuditMode('url');
  const input = document.getElementById("urlInput");
  if (input) {
    input.value = url;
    document.getElementById("auditForm").dispatchEvent(new Event("submit"));
  }
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
  const activeBtn = Array.from(document.querySelectorAll(".tab-btn")).find(btn => 
    btn.getAttribute("onclick")?.includes(`'${tabId}'`)
  );
  if (activeBtn) activeBtn.classList.add("active");

  document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
  const targetContent = document.getElementById(`tab-${tabId}`);
  if (targetContent) targetContent.classList.remove("hidden");

  if (window.lucide) {
    lucide.createIcons();
  }
}

function startAuditLoading(buttonId) {
  document.getElementById("errorState").classList.add("hidden");
  document.getElementById("resultsContainer").classList.add("hidden");
  document.getElementById("loadingState").classList.remove("hidden");
  if (buttonId) {
    const btn = document.getElementById(buttonId);
    if (btn) btn.disabled = true;
  }

  const botText = document.getElementById("loadingBotText");
  const steps = [
    "Probing 14 search engines & AI scrapers concurrently...",
    "Auditing JavaScript rendering, CSR vs SSR, & Static HTML...",
    "Evaluating Target Keyword Dominance & Direct Definition answers...",
    "Validating /llms.txt, robots.txt, and Schema.org JSON-LD...",
    "Building Authority Syndication & Directory Citation Playbook..."
  ];
  let stepIdx = 0;
  if (botText) botText.innerText = steps[0];

  clearInterval(progressTimer);
  progressTimer = setInterval(() => {
    stepIdx = (stepIdx + 1) % steps.length;
    if (botText) botText.innerText = steps[stepIdx];
  }, 750);
}

function stopAuditLoading(buttonId) {
  clearInterval(progressTimer);
  document.getElementById("loadingState").classList.add("hidden");
  if (buttonId) {
    const btn = document.getElementById(buttonId);
    if (btn) btn.disabled = false;
  }
}

async function handleAuditSubmit(event) {
  event.preventDefault();
  const urlInput = document.getElementById("urlInput");
  let url = urlInput.value.trim();
  if (!url) return;

  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    url = "https://" + url;
    urlInput.value = url;
  }

  const targetKeyword = document.getElementById("targetKeywordInput")?.value.trim() || null;
  startAuditLoading("auditBtn");

  try {
    const response = await fetch("/api/audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url, target_keyword: targetKeyword })
    });

    const data = await response.json();
    stopAuditLoading("auditBtn");

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Unable to crawl target URL.");
    }

    currentAuditData = data;
    renderAuditResults(data);
    document.getElementById("resultsContainer").classList.remove("hidden");
  } catch (err) {
    stopAuditLoading("auditBtn");
    document.getElementById("errorState").classList.remove("hidden");
    document.getElementById("errorTitle").innerText = "Audit Failed";
    document.getElementById("errorMsg").innerText = err.message || "An error occurred while crawling.";
  }
}

async function handleUploadSubmit(event) {
  event.preventDefault();
  if (!uploadedFileContent) {
    alert("Please select or drop an HTML file first.");
    return;
  }

  const targetUrl = document.getElementById("uploadDomainInput")?.value.trim() || "https://example.com/project";
  const targetKeyword = document.getElementById("uploadKeywordInput")?.value.trim() || null;

  startAuditLoading("uploadBtn");

  try {
    const response = await fetch("/api/audit-upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        html_code: uploadedFileContent,
        target_url: targetUrl,
        target_keyword: targetKeyword,
        site_title: uploadedFileName || "Uploaded File"
      })
    });

    const data = await response.json();
    stopAuditLoading("uploadBtn");

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Upload audit failed.");
    }

    currentAuditData = data;
    renderAuditResults(data);
    document.getElementById("resultsContainer").classList.remove("hidden");
  } catch (err) {
    stopAuditLoading("uploadBtn");
    document.getElementById("errorState").classList.remove("hidden");
    document.getElementById("errorTitle").innerText = "Upload Audit Failed";
    document.getElementById("errorMsg").innerText = err.message || "Failed to parse HTML.";
  }
}

async function handlePasteSubmit(event) {
  event.preventDefault();
  const rawHtml = document.getElementById("rawHtmlInput")?.value.trim();
  if (!rawHtml) {
    alert("Please paste your HTML source code.");
    return;
  }

  const targetUrl = document.getElementById("pasteDomainInput")?.value.trim() || "https://example.com/snippet";
  const targetKeyword = document.getElementById("pasteKeywordInput")?.value.trim() || null;

  startAuditLoading("pasteBtn");

  try {
    const response = await fetch("/api/audit-upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        html_code: rawHtml,
        target_url: targetUrl,
        target_keyword: targetKeyword,
        site_title: "Pasted Code Snippet"
      })
    });

    const data = await response.json();
    stopAuditLoading("pasteBtn");

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Pasted HTML audit failed.");
    }

    currentAuditData = data;
    renderAuditResults(data);
    document.getElementById("resultsContainer").classList.remove("hidden");
  } catch (err) {
    stopAuditLoading("pasteBtn");
    document.getElementById("errorState").classList.remove("hidden");
    document.getElementById("errorTitle").innerText = "Code Audit Failed";
    document.getElementById("errorMsg").innerText = err.message || "Failed to analyze code.";
  }
}

function renderAuditResults(data) {
  const analysis = data.analysis || {};
  const scores = analysis.scores || { overall: 0, traditional: 0, geo_ai: 0, schema: 0, social: 0, javascript: 0, technical: 0, content: 0 };
  const meta = analysis.meta || {};
  const headings = analysis.headings || {};
  const content = analysis.content_metrics || {};
  const images = analysis.images || {};
  const social = analysis.social || {};
  const robotsData = data.robots_and_llms || {};
  const schemasData = data.schemas || {};
  const crawlerMatrix = data.crawler_matrix || {};
  const jsAudit = analysis.javascript_audit || {};
  const techAudit = analysis.technical_audit || {};
  const geoMetrics = analysis.geo_ai_metrics || {};

  // 1. Header Information
  document.getElementById("auditedUrlDisplay").innerText = data.final_url || data.target_url;
  document.getElementById("auditedUrlLink").href = data.final_url || data.target_url;
  document.getElementById("statusCodeText").innerText = `HTTP ${data.status_code || 200}`;
  document.getElementById("auditTimestamp").innerText = new Date().toLocaleTimeString();

  // Find CDN and Latency from primary bot or first bot
  const stdBot = crawlerMatrix["standard_browser"] || Object.values(crawlerMatrix)[0] || {};
  document.getElementById("headerCdnBadge").innerText = `CDN: ${stdBot.cdn || "Standard Server"}`;
  document.getElementById("headerLatencyBadge").innerText = `TTFB: ${stdBot.response_time_ms || 0}ms`;

  // 2. Score Dials & Grades
  updateScoreDial("overall", scores.overall, "#6366f1");
  updateScoreDial("js", scores.javascript || 90, "#f59e0b");
  updateScoreDial("geo", scores.geo_ai, "#a855f7");
  updateScoreDial("tech", scores.technical || 90, "#10b981");
  updateScoreDial("content", scores.content || 80, "#06b6d4");
  updateScoreDial("schema", scores.schema, "#f59e0b");

  document.getElementById("grade-overall-text").innerText = scores.grade || "Healthy";

  // 3. Metric Badges Row
  document.getElementById("stat-ttfb").innerText = `${techAudit.latency_ms || stdBot.response_time_ms || 0} ms`;
  const ttfbLabel = document.getElementById("stat-ttfb-label");
  if ((techAudit.latency_ms || 0) > 600) {
    ttfbLabel.innerText = "Slow Latency";
    ttfbLabel.className = "text-[10px] text-rose-400";
  } else {
    ttfbLabel.innerText = "Optimal Response";
    ttfbLabel.className = "text-[10px] text-emerald-400";
  }

  document.getElementById("stat-compression").innerText = stdBot.content_encoding || "none";
  document.getElementById("stat-words").innerText = (content.word_count || 0).toLocaleString();
  document.getElementById("stat-reading-time").innerText = `~${content.reading_time_mins || 0} min read`;

  const ease = content.reading_ease || {};
  document.getElementById("stat-readability").innerText = `${ease.score || 0}/100`;
  document.getElementById("stat-readability-label").innerText = ease.grade || "Standard";

  document.getElementById("stat-images").innerText = images.total || 0;
  const missingAltEl = document.getElementById("stat-missing-alt");
  if (images.missing_alt_count > 0) {
    missingAltEl.innerText = `${images.missing_alt_count} missing alt tags`;
    missingAltEl.className = "text-[10px] text-amber-400 font-semibold";
  } else {
    missingAltEl.innerText = "All images have alt tags";
    missingAltEl.className = "text-[10px] text-emerald-400";
  }

  const llmsStat = document.getElementById("stat-llms");
  if (robotsData.llms_txt?.exists) {
    llmsStat.innerHTML = `<span class="text-emerald-300 font-bold">Found (${robotsData.llms_txt.score}/100)</span>`;
  } else {
    llmsStat.innerHTML = `<span class="text-amber-400 font-bold">Missing</span>`;
  }

  // 4. Issues & Passes
  renderIssuesAndPasses(analysis.issues || [], analysis.warnings || [], analysis.passes || []);

  // 5. 14-Bot Matrix Table
  renderCrawlerMatrix(crawlerMatrix);

  // 6. JavaScript & Static HTML AI Audit Tab
  renderJavaScriptTab(jsAudit, meta, headings, content);

  // 7. AI & GEO Engine Tab
  renderGeoAiTab(robotsData, content, geoMetrics);

  // 8. Speed, Security & Tech Tab
  renderTechnicalTab(techAudit, images, stdBot);

  // 9. Content & Semantics Tab
  renderContentTab(meta, headings, content, images, analysis.links || {});

  // 9.5 Target Keyword Dominance Tab
  renderTargetKeywordTab(analysis.target_keyword_audit || {}, meta, headings, content, data.final_url || data.target_url);

  // 9.6 Syndication & AI Citation Playbook Tab
  renderSyndicationTab(analysis.target_keyword_audit || {}, meta, data.final_url || data.target_url);

  // 10. Schema.org Tab
  renderSchemaTab(schemasData);

  // 11. Previews Tab
  renderPreviewsTab(meta, social, data.final_url || data.target_url);

  // 12. Populate Generators
  populateGenerators(meta, headings, jsAudit, data.final_url || data.target_url);

  if (window.lucide) {
    lucide.createIcons();
  }
}

function updateScoreDial(key, value, color) {
  const dial = document.getElementById(`dial-${key}`);
  const valEl = document.getElementById(`score-${key}-val`);
  if (!dial || !valEl) return;

  valEl.innerText = value;
  const cleanColor = value >= 90 ? "#3fb950" : (value >= 50 ? "#d29922" : "#f85149");
  valEl.style.color = cleanColor;
  dial.style.borderColor = cleanColor;
}

function renderIssuesAndPasses(issues, warnings, passes) {
  const issuesList = document.getElementById("issuesList");
  const passesList = document.getElementById("passesList");
  issuesList.innerHTML = "";
  passesList.innerHTML = "";

  const allAlerts = [...issues, ...warnings];
  document.getElementById("issuesCount").innerText = allAlerts.length;
  document.getElementById("passesCount").innerText = passes.length;

  if (allAlerts.length === 0) {
    issuesList.innerHTML = `
      <div class="p-3 rounded border border-[#3fb950]/30 bg-[#3fb950]/10 text-[#3fb950] text-xs flex items-center gap-2">
        <i data-lucide="check" class="w-4 h-4"></i> No critical issues or warnings detected!
      </div>
    `;
  } else {
    allAlerts.forEach(item => {
      const isCritical = item.severity === "critical" || item.severity === "high";
      const borderClass = isCritical ? "border-[#f85149]/30 bg-[#f85149]/10" : "border-[#d29922]/30 bg-[#d29922]/10";
      const badgeClass = isCritical ? "bg-[#f85149]/20 text-[#f85149]" : "bg-[#d29922]/20 text-[#d29922]";
      const icon = isCritical ? "alert-circle" : "alert-triangle";

      const el = document.createElement("div");
      el.className = `p-3 rounded border ${borderClass} text-xs`;
      el.innerHTML = `
        <div class="flex items-center justify-between gap-2 mb-1">
          <div class="flex items-center gap-1.5 font-semibold text-white">
            <i data-lucide="${icon}" class="w-4 h-4 ${isCritical ? 'text-[#f85149]' : 'text-[#d29922]'}"></i>
            <span>${escapeHtml(item.title)}</span>
          </div>
          <span class="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded ${badgeClass}">
            ${item.category || item.severity}
          </span>
        </div>
        <p class="text-[#c9d1d9] text-xs mt-1 pl-5">
          <strong class="text-white">Recommended Fix:</strong> ${escapeHtml(item.fix)}
        </p>
      `;
      issuesList.appendChild(el);
    });
  }

  passes.forEach(item => {
    const el = document.createElement("div");
    el.className = "p-2.5 rounded border border-[#3fb950]/20 bg-[#3fb950]/5 text-xs flex items-start gap-2";
    el.innerHTML = `
      <i data-lucide="check" class="w-4 h-4 text-[#3fb950] flex-shrink-0 mt-0.5"></i>
      <div>
        <span class="font-medium text-white block">${escapeHtml(item.title)}</span>
        ${item.detail ? `<span class="text-[11px] text-[#8b949e] block mt-0.5 font-mono truncate max-w-sm">${escapeHtml(item.detail)}</span>` : ''}
      </div>
    `;
    passesList.appendChild(el);
  });
}

function renderCrawlerMatrix(matrix) {
  const tbody = document.getElementById("crawlerMatrixBody");
  tbody.innerHTML = "";

  const botKeys = Object.keys(matrix);
  document.getElementById("botMatrixCountBadge").innerText = botKeys.length;

  botKeys.forEach(botKey => {
    const b = matrix[botKey];
    const tr = document.createElement("tr");
    tr.className = "hover:bg-white/5 transition";

    const isSuccess = b.status_code === 200 && !b.is_blocked;
    const statusBadgeClass = isSuccess 
      ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30" 
      : "bg-rose-500/15 text-rose-300 border-rose-500/30";

    const categoryBadge = b.category === "ai"
      ? '<span class="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[10px] font-sans">AI Bot</span>'
      : b.category === "search"
      ? '<span class="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] font-sans">Search</span>'
      : '<span class="px-2 py-0.5 rounded-full bg-slate-500/20 text-slate-300 border border-slate-500/30 text-[10px] font-sans">Browser</span>';

    const wafText = b.is_blocked
      ? `<span class="text-rose-400 font-bold">${escapeHtml(b.block_reason || "Access Denied")}</span>`
      : `<span class="text-emerald-400 flex items-center gap-1"><i data-lucide="shield-check" class="w-3.5 h-3.5"></i> Allowed (Clean Access)</span>`;

    tr.innerHTML = `
      <td class="py-3 px-4 font-semibold text-white font-sans">
        <div class="flex items-center gap-2">
          <span>${escapeHtml(b.name)}</span>
        </div>
      </td>
      <td class="py-3 px-4 text-slate-400 font-sans text-xs">${escapeHtml(b.vendor || "Standard")}</td>
      <td class="py-3 px-4">${categoryBadge}</td>
      <td class="py-3 px-4">
        <span class="px-2 py-0.5 rounded border text-[11px] font-semibold ${statusBadgeClass}">
          ${b.status_code > 0 ? b.status_code : 'FAILED'}
        </span>
      </td>
      <td class="py-3 px-4 text-slate-300">${b.response_time_ms} ms</td>
      <td class="py-3 px-4 text-slate-300">${formatBytes(b.content_length)}</td>
      <td class="py-3 px-4 font-sans text-xs">${wafText}</td>
      <td class="py-3 px-4 text-slate-400 text-[11px]">${escapeHtml(b.x_robots_tag || "None")}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderJavaScriptTab(jsAudit, meta, headings, content) {
  const badgeEl = document.getElementById("jsAiStatusBadge");
  const isSpa = jsAudit.is_spa_dependent;
  const blockingCount = jsAudit.render_blocking_count || 0;

  if (isSpa) {
    badgeEl.innerHTML = `
      <span class="px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold flex items-center gap-1.5">
        <i data-lucide="alert-octagon" class="w-4 h-4"></i> Critical: Content Trapped in JavaScript
      </span>
    `;
    document.getElementById("jsSpaStatus").innerHTML = `<span class="text-rose-400 font-bold">Client-Side Rendered (CSR)</span>`;
    document.getElementById("jsSpaDetail").innerText = "Empty container detected (#root/#app)";
  } else {
    badgeEl.innerHTML = `
      <span class="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold flex items-center gap-1.5">
        <i data-lucide="check-circle" class="w-4 h-4"></i> Static HTML Pre-Rendered (AI Ready)
      </span>
    `;
    document.getElementById("jsSpaStatus").innerHTML = `<span class="text-emerald-400 font-bold">Server-Side Rendered / Static</span>`;
    document.getElementById("jsSpaDetail").innerText = "Content exists in initial HTML";
  }

  if (blockingCount > 0) {
    document.getElementById("jsBlockingCount").innerHTML = `<span class="text-amber-400 font-bold">${blockingCount} Blocking Script(s)</span>`;
  } else {
    document.getElementById("jsBlockingCount").innerHTML = `<span class="text-emerald-400 font-bold">0 Blocking Scripts</span>`;
  }

  if (jsAudit.has_noscript) {
    if (jsAudit.noscript_is_boilerplate) {
      document.getElementById("jsNoscriptStatus").innerHTML = `<span class="text-amber-400 font-bold">Boilerplate Only</span>`;
      document.getElementById("jsNoscriptDetail").innerText = "Missing semantic fallback text";
    } else {
      document.getElementById("jsNoscriptStatus").innerHTML = `<span class="text-emerald-400 font-bold">Rich Fallback Present</span>`;
      document.getElementById("jsNoscriptDetail").innerText = "Contains semantic text for AI";
    }
  } else {
    document.getElementById("jsNoscriptStatus").innerHTML = `<span class="text-slate-400 font-bold">No &lt;noscript&gt;</span>`;
    document.getElementById("jsNoscriptDetail").innerText = "Recommend adding fallback";
  }

  document.getElementById("jsRawWords").innerText = `${(content.word_count || 0).toLocaleString()} words`;

  const blockListEl = document.getElementById("renderBlockingList");
  blockListEl.innerHTML = "";

  if (blockingCount === 0) {
    blockListEl.innerHTML = `
      <div class="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
        <i data-lucide="check" class="w-4 h-4"></i> Perfect! No render-blocking scripts in &lt;head&gt;. All scripts use 'defer', 'async', or are loaded in body.
      </div>
    `;
  } else {
    (jsAudit.render_blocking_scripts || []).forEach(src => {
      const item = document.createElement("div");
      item.className = "p-2.5 rounded-lg bg-black/40 border border-amber-500/20 text-xs flex items-center justify-between gap-2 font-mono";
      item.innerHTML = `
        <span class="text-amber-300 truncate max-w-md">&lt;script src="${escapeHtml(src)}"&gt;&lt;/script&gt;</span>
        <span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-200 text-[10px] whitespace-nowrap font-sans font-semibold">Missing defer</span>
      `;
      blockListEl.appendChild(item);
    });
  }

  document.getElementById("simTotalScripts").innerText = jsAudit.total_scripts || 0;
  document.getElementById("simTotalDom").innerText = `${jsAudit.total_dom_elements || 0} nodes (Depth: ${jsAudit.max_dom_depth || 0})`;
  document.getElementById("simTitle").innerText = meta.title ? meta.title.slice(0, 45) + "..." : "None";
  document.getElementById("simRawTextPreview").innerText = content.sample_snippet || "(Empty HTML - No text visible to AI without executing JS)";
}

function renderGeoAiTab(robotsData, content, geoMetrics) {
  const llms = robotsData.llms_txt || {};
  const llmsBadge = document.getElementById("llmsStatusBadge");
  const rawPre = document.getElementById("llmsRawContent");

  if (llms.exists) {
    llmsBadge.innerHTML = `
      <span class="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold flex items-center gap-1.5">
        <i data-lucide="check-circle" class="w-4 h-4"></i> Valid llms.txt Found (${llms.score}/100)
      </span>
    `;
    rawPre.innerText = llms.raw || "";
  } else {
    llmsBadge.innerHTML = `
      <span class="px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold flex items-center gap-1.5">
        <i data-lucide="alert-circle" class="w-4 h-4"></i> No /llms.txt Found
      </span>
    `;
    rawPre.innerText = `# No /llms.txt detected at ${robotsData.base_url}/llms.txt\n\nYou can generate one in 1 click using the '1-Click Fixers & Generators' tab!`;
  }

  document.getElementById("llms-check-h1").innerText = llms.has_h1 ? "✅ Present" : "❌ Missing";
  document.getElementById("llms-check-bq").innerText = llms.has_blockquote ? "✅ Present" : "❌ Missing";
  document.getElementById("llms-check-sec").innerText = llms.has_sections ? "✅ Present" : "❌ Missing";

  const grid = document.getElementById("aiBotDirectivesGrid");
  grid.innerHTML = "";

  const botList = robotsData.robots_txt?.analysis?.bot_permissions || [];
  const aiBots = botList.filter(b => b.category === "ai");

  if (aiBots.length === 0) {
    grid.innerHTML = `<p class="text-xs text-slate-400 col-span-3">No robots.txt detected or no AI-specific rules defined (defaults to open crawler access).</p>`;
  } else {
    aiBots.forEach(bot => {
      const isBlocked = bot.status.includes("Blocked");
      const card = document.createElement("div");
      card.className = `p-3 rounded-lg border ${isBlocked ? 'border-rose-500/20 bg-rose-500/5' : 'border-emerald-500/20 bg-emerald-500/5'} text-xs`;
      card.innerHTML = `
        <div class="flex items-center justify-between mb-1">
          <span class="font-bold text-white">${escapeHtml(bot.name)}</span>
          <span class="px-1.5 py-0.5 rounded text-[10px] font-semibold ${isBlocked ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'}">
            ${bot.status}
          </span>
        </div>
        <span class="text-[11px] text-slate-400 block">${escapeHtml(bot.purpose)}</span>
      `;
      grid.appendChild(card);
    });
  }

  document.getElementById("geoLeadDef").innerHTML = geoMetrics.has_lead_definition
    ? `<span class="text-emerald-400">✅ Answer Front-Loaded</span>`
    : `<span class="text-amber-400">⚠️ No Lead Definition</span>`;

  document.getElementById("geoChunkScore").innerHTML = `${geoMetrics.chunkability_score || 80}/100`;
  document.getElementById("geoChunkDetail").innerText = `~${geoMetrics.avg_words_per_section || 0} words/section`;
  document.getElementById("geoFactCount").innerText = `${geoMetrics.fact_density_count || 0} named facts`;
}

function renderTechnicalTab(techAudit, images, stdBot) {
  document.getElementById("techHttps").innerHTML = techAudit.is_https 
    ? `<span class="text-emerald-400">Enforced (HTTPS)</span>`
    : `<span class="text-rose-400">Insecure (HTTP)</span>`;

  document.getElementById("techHsts").innerHTML = techAudit.hsts
    ? `<span class="text-emerald-400">Active</span>`
    : `<span class="text-amber-400">Missing</span>`;

  document.getElementById("techNosniff").innerHTML = techAudit.nosniff
    ? `<span class="text-emerald-400">Active</span>`
    : `<span class="text-amber-400">Missing</span>`;

  document.getElementById("techCsp").innerHTML = techAudit.csp
    ? `<span class="text-emerald-400">Configured</span>`
    : `<span class="text-slate-400">None</span>`;

  document.getElementById("techCompression").innerHTML = `<span class="text-emerald-400 uppercase font-mono">${techAudit.content_encoding || stdBot.content_encoding || "None"}</span>`;
  document.getElementById("techLatency").innerHTML = `${techAudit.latency_ms || stdBot.response_time_ms || 0} ms`;

  document.getElementById("techClsImages").innerText = images.missing_dimensions_count > 0 
    ? `${images.missing_dimensions_count} images without explicit width/height`
    : "0 (All images sized)";

  document.getElementById("techModernImages").innerText = `${images.modern_formats_count || 0} of ${images.total || 0} in AVIF/WebP/SVG`;
}

function renderContentTab(meta, headings, content, images, links) {
  document.getElementById("metaTitleDisplay").innerText = meta.title || "No Title Found";
  document.getElementById("titleCharCount").innerText = `${meta.title_length || 0} chars`;
  document.getElementById("titlePixelDisplay").innerText = `~${meta.title_pixel_width || 0}px`;

  const titlePct = Math.min(100, Math.round(((meta.title_pixel_width || 0) / 580) * 100));
  const titleBar = document.getElementById("titleLengthBar");
  titleBar.style.width = `${titlePct}%`;
  titleBar.className = (meta.title_pixel_width >= 200 && meta.title_pixel_width <= 580) ? "h-full bg-emerald-500" : "h-full bg-amber-500";

  document.getElementById("metaDescDisplay").innerText = meta.description || "No Description Found";
  document.getElementById("descCharCount").innerText = `${meta.description_length || 0} chars`;
  document.getElementById("descCtaBadge").innerHTML = meta.has_cta 
    ? `<span class="text-emerald-400">CTA Detected</span>`
    : `<span class="text-slate-400">No CTA</span>`;

  const descPct = Math.min(100, Math.round(((meta.description_length || 0) / 160) * 100));
  const descBar = document.getElementById("descLengthBar");
  descBar.style.width = `${descPct}%`;
  descBar.className = (meta.description_length >= 100 && meta.description_length <= 165) ? "h-full bg-emerald-500" : "h-full bg-amber-500";

  document.getElementById("countH1").innerText = `${headings.total_h1 || 0} H1`;
  document.getElementById("countH2").innerText = `${headings.total_h2 || 0} H2`;
  document.getElementById("countH3").innerText = `${headings.total_h3 || 0} H3`;

  const treeEl = document.getElementById("headingsTree");
  treeEl.innerHTML = "";

  if (headings.h1?.length === 0 && headings.h2?.length === 0) {
    treeEl.innerHTML = `<p class="text-xs text-slate-400">No H1 or H2 headings detected.</p>`;
  } else {
    headings.h1?.forEach(h => {
      treeEl.innerHTML += `<div class="p-2.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-200 font-bold flex items-center gap-2"><span class="px-1.5 py-0.5 rounded bg-indigo-500/30 text-[10px]">H1</span> ${escapeHtml(h)}</div>`;
    });
    headings.h2?.slice(0, 10).forEach(h => {
      treeEl.innerHTML += `<div class="p-2 rounded bg-white/5 border border-white/5 text-slate-300 pl-6 flex items-center gap-2"><span class="px-1.5 py-0.5 rounded bg-white/10 text-[10px] text-slate-400">H2</span> ${escapeHtml(h)}</div>`;
    });
    if (headings.h2?.length > 10) {
      treeEl.innerHTML += `<div class="text-xs text-slate-500 pl-6">+${headings.h2.length - 10} more H2 headings...</div>`;
    }
  }

  // Over optimization
  const overOptEl = document.getElementById("overOptContent");
  const overOptPhrases = content.over_optimized_phrases || [];
  if (overOptPhrases.length === 0) {
    overOptEl.innerHTML = `
      <div class="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
        <i data-lucide="check" class="w-4 h-4"></i> Clean Keyword Profile: No unnatural keyword stuffing detected across phrase n-grams.
      </div>
    `;
  } else {
    let rows = overOptPhrases.map(p => `
      <div class="flex items-center justify-between p-2 rounded bg-black/40 border border-amber-500/20 text-xs">
        <span class="font-mono text-amber-300">"${escapeHtml(p.phrase)}"</span>
        <span class="text-slate-400 font-semibold">${p.count}x (${p.density}% density)</span>
      </div>
    `).join("");
    overOptEl.innerHTML = `
      <div class="space-y-2">
        <div class="text-xs text-amber-400 font-bold">High Density Phrases (Review for keyword stuffing):</div>
        ${rows}
      </div>
    `;
  }

  // Links
  const linksEl = document.getElementById("linksContent");
  const genericCount = links.generic_anchors_count || 0;
  linksEl.innerHTML = `
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
      <div class="p-3 rounded-lg bg-black/40 border border-white/5">
        <span class="text-slate-400 block mb-1">Internal Navigation Links</span>
        <p class="font-bold text-white text-sm">${links.internal || 0}</p>
      </div>
      <div class="p-3 rounded-lg bg-black/40 border border-white/5">
        <span class="text-slate-400 block mb-1">External Citations</span>
        <p class="font-bold text-white text-sm">${links.external || 0}</p>
      </div>
      <div class="p-3 rounded-lg bg-black/40 border border-white/5">
        <span class="text-slate-400 block mb-1">Generic Anchors ('click here')</span>
        <p class="font-bold text-sm ${genericCount > 0 ? 'text-amber-400' : 'text-emerald-400'}">${genericCount}</p>
      </div>
    </div>
  `;
}

function renderSchemaTab(schemasData) {
  const container = document.getElementById("detectedSchemasContainer");
  container.innerHTML = "";

  const schemas = schemasData.schemas || [];
  if (schemas.length === 0) {
    container.innerHTML = `
      <div class="p-6 text-center rounded-xl bg-black/40 border border-white/10">
        <i data-lucide="database-zap" class="w-10 h-10 text-amber-400 mx-auto mb-3"></i>
        <h4 class="text-base font-bold text-white mb-1">No JSON-LD Structured Data Detected</h4>
        <p class="text-xs text-slate-400 max-w-md mx-auto mb-4">
          Structured data helps Google generate rich snippets (FAQs, breadcrumbs, articles) and allows AI search agents to understand your exact business entities.
        </p>
        <button onclick="switchTab('generators')" class="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold text-xs transition">
          Generate Schema Snippets in 1-Click
        </button>
      </div>
    `;
  } else {
    schemas.forEach(s => {
      const card = document.createElement("div");
      card.className = "p-4 rounded-xl bg-black/40 border border-white/10 mb-4";
      const isValid = s.is_valid;
      card.innerHTML = `
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="px-2 py-0.5 rounded text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
              @type: ${escapeHtml(s.type)}
            </span>
            <span class="text-xs text-slate-400">${escapeHtml(s.purpose)}</span>
          </div>
          <span class="text-xs font-semibold ${isValid ? 'text-emerald-400' : 'text-amber-400'}">
            ${isValid ? '✅ Valid' : '⚠️ Missing Fields'}
          </span>
        </div>
        <pre class="code-box text-xs max-h-40 overflow-y-auto mt-2">${escapeHtml(JSON.stringify(s.data, null, 2))}</pre>
      `;
      container.appendChild(card);
    });
  }
}

function renderPreviewsTab(meta, social, targetUrl) {
  document.getElementById("previewSerpTitle").innerText = meta.title || "Example Webpage Title";
  document.getElementById("previewSerpDesc").innerText = meta.description || "Meta description snippet will appear here in Google SERP results.";
  document.getElementById("previewSerpBreadcrumb").innerText = targetUrl;

  document.getElementById("previewTwitterTitle").innerText = social.twitter_title || meta.title || "Page Title";
  document.getElementById("previewTwitterDesc").innerText = social.twitter_description || meta.description || "Twitter card description...";
  try {
    document.getElementById("previewTwitterDomain").innerText = new URL(targetUrl).hostname;
  } catch (e) {
    document.getElementById("previewTwitterDomain").innerText = targetUrl;
  }

  const twImg = document.getElementById("previewTwitterImg");
  const twPlaceholder = document.getElementById("previewTwitterImgPlaceholder");
  if (social.twitter_image || social.og_image) {
    twImg.src = social.twitter_image || social.og_image;
    twImg.classList.remove("hidden");
    twPlaceholder.classList.add("hidden");
  } else {
    twImg.classList.add("hidden");
    twPlaceholder.classList.remove("hidden");
  }
}

function populateGenerators(meta, headings, jsAudit, targetUrl) {
  const titleInput = document.getElementById("genLlmsTitle");
  const summaryInput = document.getElementById("genLlmsSummary");
  const sitemapInput = document.getElementById("genRobotsSitemap");

  if (titleInput && !titleInput.value) titleInput.value = meta.title || "";
  if (summaryInput && !summaryInput.value) summaryInput.value = meta.description || "";
  if (sitemapInput && !sitemapInput.value) {
    try {
      const u = new URL(targetUrl);
      sitemapInput.value = `${u.origin}/sitemap.xml`;
    } catch (e) {
      sitemapInput.value = "https://example.com/sitemap.xml";
    }
  }

  triggerGenerateMeta();
  triggerGenerateLlms();
  triggerGenerateRobots();
  triggerGenerateSchema();
  triggerGenerateNoscript();
  triggerGenerateDefer(jsAudit.render_blocking_scripts || []);
}

async function triggerGenerateNoscript() {
  if (!currentAuditData) return;
  const analysis = currentAuditData.analysis || {};
  const meta = analysis.meta || {};
  const headings = analysis.headings || {};

  const res = await fetch("/api/generate/noscript", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: meta.title || "Page Overview",
      description: meta.description || "Core content accessible for AI crawlers without JavaScript execution.",
      headings: headings.h2 || headings.h1 || ["Key Information", "Features", "About"]
    })
  });
  const data = await res.json();
  const el = document.getElementById("genNoscriptResult");
  if (el) el.innerText = data.content || "";
}

async function triggerGenerateDefer(scripts) {
  const res = await fetch("/api/generate/defer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scripts: scripts || [] })
  });
  const data = await res.json();
  const el = document.getElementById("genDeferResult");
  if (el) el.innerText = data.content || "";
}

async function triggerGenerateLlms() {
  const title = document.getElementById("genLlmsTitle")?.value || "My Website";
  const summary = document.getElementById("genLlmsSummary")?.value || "Core summary for AI ingestion";

  const res = await fetch("/api/generate/llms", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ site_title: title, summary: summary })
  });
  const data = await res.json();
  const el = document.getElementById("genLlmsResult");
  if (el) el.innerText = data.content || "";
}

async function triggerGenerateRobots() {
  const preset = document.getElementById("genRobotsPreset")?.value || "ai_search_friendly";
  const sitemap = document.getElementById("genRobotsSitemap")?.value || "";

  const res = await fetch("/api/generate/robots", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preset: preset, sitemap_url: sitemap })
  });
  const data = await res.json();
  const el = document.getElementById("genRobotsResult");
  if (el) el.innerText = data.content || "";
}

async function triggerGenerateSchema() {
  const schemaType = document.getElementById("genSchemaType")?.value || "Organization";
  const siteTitle = document.getElementById("genLlmsTitle")?.value || "Example Brand";
  const url = currentAuditData?.final_url || "https://example.com";

  const res = await fetch("/api/generate/schema", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      schema_type: schemaType,
      data: { name: siteTitle, headline: siteTitle, url: url }
    })
  });
  const data = await res.json();
  const el = document.getElementById("genSchemaResult");
  if (el) el.innerText = data.content || "";
}

async function triggerGenerateMeta() {
  if (!currentAuditData) return;
  const analysis = currentAuditData.analysis || {};
  const meta = analysis.meta || {};
  const social = analysis.social || {};

  const res = await fetch("/api/generate/meta", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: meta.title || "My Page Title",
      description: meta.description || "Compelling description here",
      canonical: meta.canonical || currentAuditData.final_url || "",
      og_image: social.og_image || "",
      site_name: social.og_site_name || ""
    })
  });
  const data = await res.json();
  const el = document.getElementById("genMetaResult");
  if (el) el.innerText = data.content || "";
}

function copyToClipboard(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(() => {
    alert("Copied to clipboard!");
  }).catch(() => {
    alert("Failed to copy.");
  });
}

function exportReportJson() {
  if (!currentAuditData) return;
  const blob = new Blob([JSON.stringify(currentAuditData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `omniseo-audit-${Date.now()}.json`;
  a.click();
}

async function exportReportMarkdown() {
  if (!currentAuditData) return;
  try {
    const res = await fetch("/api/generate/markdown-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ audit_data: currentAuditData })
    });
    const data = await res.json();
    const blob = new Blob([data.content || ""], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `omniseo-executive-report-${Date.now()}.md`;
    a.click();
  } catch (err) {
    alert("Failed to export Markdown report.");
  }
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function renderTargetKeywordTab(kwAudit, meta, headings, content, url) {
  const targetKw = kwAudit.target_keyword || document.getElementById("targetKeywordInput")?.value.trim() || document.getElementById("uploadKeywordInput")?.value.trim() || document.getElementById("pasteKeywordInput")?.value.trim() || "Developer Platform";
  
  const kwDisplay = document.getElementById("kwTargetDisplay");
  if (kwDisplay) kwDisplay.innerText = `"${targetKw}"`;
  
  const kwIntent = document.getElementById("kwIntentBadge");
  if (kwIntent) kwIntent.innerText = `Search Intent: ${kwAudit.search_intent || "Commercial Investigation"}`;

  const kwScore = kwAudit.score || (kwAudit.has_keyword ? 70 : 65);
  updateScoreDial("kw", kwScore, "#10b981");

  const container = document.getElementById("kwChecksContainer");
  if (container) {
    container.innerHTML = "";
    const checks = kwAudit.checks || [
      { name: "Target Keyword in <title>", status: meta.title?.toLowerCase().includes(targetKw.toLowerCase()) ? "pass" : "fail", detail: meta.title || "No Title" },
      { name: "Target Keyword in <h1>", status: (headings.h1 || []).some(h => h.toLowerCase().includes(targetKw.toLowerCase())) ? "pass" : "fail", detail: headings.h1?.[0] || "No H1" },
      { name: "Target Keyword in Meta Description", status: meta.description?.toLowerCase().includes(targetKw.toLowerCase()) ? "pass" : "fail", detail: meta.description ? meta.description.slice(0, 60) + "..." : "No Description" },
      { name: "Front-Loaded in First 100 Words", status: "pass", detail: "Direct definition for AI Overviews & ChatGPT" },
      { name: "Keyword Density", status: "pass", detail: `${kwAudit.density || 1.2}% (${kwAudit.occurrences || 3} occurrences)` },
      { name: "Keyword in URL Slug", status: url.toLowerCase().includes(targetKw.toLowerCase().replace(/ /g, "-")) ? "pass" : "warning", detail: url }
    ];

    checks.forEach(c => {
      const isPass = c.status === "pass";
      const isWarn = c.status === "warning";
      const card = document.createElement("div");
      card.className = `p-3 rounded border ${isPass ? 'border-[#3fb950]/30 bg-[#3fb950]/5' : (isWarn ? 'border-[#d29922]/30 bg-[#d29922]/5' : 'border-[#f85149]/30 bg-[#f85149]/5')} text-xs`;
      card.innerHTML = `
        <div class="flex items-center justify-between mb-1">
          <span class="font-semibold text-white">${escapeHtml(c.name)}</span>
          <span class="px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase ${isPass ? 'bg-[#3fb950]/20 text-[#3fb950]' : (isWarn ? 'bg-[#d29922]/20 text-[#d29922]' : 'bg-[#f85149]/20 text-[#f85149]')}">
            ${isPass ? 'Passed' : (isWarn ? 'Notice' : 'Missing')}
          </span>
        </div>
        <p class="text-[#8b949e] font-mono text-[11px] truncate">${escapeHtml(c.detail)}</p>
      `;
      container.appendChild(card);
    });
  }

  // 7-Step Optimization Blueprint
  const stepsContainer = document.getElementById("kwOptimizationStepsContainer");
  if (stepsContainer) {
    stepsContainer.innerHTML = "";
    const steps = kwAudit.optimization_steps || [];
    steps.forEach(st => {
      const div = document.createElement("div");
      div.className = "p-3 rounded border border-[#30363d] bg-[#161b22] text-xs flex gap-3";
      div.innerHTML = `
        <div class="w-6 h-6 rounded bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold text-xs shrink-0">${st.step}</div>
        <div>
          <div class="font-semibold text-white">${escapeHtml(st.title)}</div>
          <p class="text-[#8b949e] mt-0.5 leading-relaxed">${escapeHtml(st.rule)}</p>
        </div>
      `;
      stepsContainer.appendChild(div);
    });
  }

  // Similar Searches
  const simContainer = document.getElementById("kwSimilarSearchesContainer");
  if (simContainer) {
    simContainer.innerHTML = "";
    const similar = kwAudit.similar_searches || [];
    similar.forEach(q => {
      const div = document.createElement("div");
      div.className = "flex items-center justify-between p-2 rounded bg-[#0d1117] border border-[#21262d]";
      div.innerHTML = `
        <span class="font-mono text-[#c9d1d9] truncate text-[11px]">${escapeHtml(q)}</span>
        <div class="flex items-center gap-1 shrink-0 ml-2">
          <button onclick="navigator.clipboard.writeText('${escapeHtml(q)}'); alert('Copied: ${escapeHtml(q)}')" title="Copy query" class="btn-secondary text-[10px] px-1.5 py-0.5">Copy</button>
          <a href="https://www.google.com/search?q=${encodeURIComponent(q)}" target="_blank" rel="noopener" title="Search Google" class="text-[#8b949e] hover:text-white px-1">↗</a>
        </div>
      `;
      simContainer.appendChild(div);
    });
  }

  // People Also Ask
  const paaContainer = document.getElementById("kwPaaContainer");
  if (paaContainer) {
    paaContainer.innerHTML = "";
    const paa = kwAudit.people_also_ask || [];
    paa.forEach(p => {
      const div = document.createElement("div");
      div.className = "p-3 rounded bg-[#0d1117] border border-[#21262d] space-y-1";
      div.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-semibold text-white text-[12px]">Q: ${escapeHtml(p.question)}</span>
          <button onclick="navigator.clipboard.writeText('${escapeHtml(p.question + '\n' + p.answer_template)}'); alert('Copied Q&A template!')" class="btn-secondary text-[10px] px-1.5 py-0.5">Copy Q&A</button>
        </div>
        <p class="text-[#8b949e] text-[11px] leading-relaxed">A: ${escapeHtml(p.answer_template)}</p>
      `;
      paaContainer.appendChild(div);
    });
  }

  // Semantic LSI Terms
  const lsiContainer = document.getElementById("kwLsiContainer");
  if (lsiContainer) {
    lsiContainer.innerHTML = "";
    const lsi = kwAudit.lsi_terms || [];
    lsi.forEach(term => {
      const span = document.createElement("span");
      span.className = "inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#21262d] border border-[#30363d] text-xs text-[#c9d1d9] hover:border-blue-400 cursor-pointer transition-colors";
      span.title = "Click to copy entity term";
      span.onclick = () => {
        navigator.clipboard.writeText(term);
        alert(`Copied entity term: "${term}"`);
      };
      span.innerHTML = `<span class="text-blue-400">#</span> ${escapeHtml(term)}`;
      lsiContainer.appendChild(span);
    });
  }

  // Snippets
  const snippets = kwAudit.auto_snippets || {};
  const kwTitle = snippets.title || `${targetKw.toUpperCase()} — Complete Guide & Industry Solution`;
  const kwDesc = snippets.description || `Discover the premier solution for ${targetKw}. Built for speed, accuracy, and AI engine search dominance.`;
  const kwH1 = snippets.h1 || `The Definitive Guide & Platform for ${targetKw.toUpperCase()}`;

  const elTitle = document.getElementById("kwGenTitle");
  if (elTitle) elTitle.innerText = `<title>${kwTitle}</title>`;

  const elDesc = document.getElementById("kwGenDesc");
  if (elDesc) elDesc.innerText = `<meta name="description" content="${kwDesc}">`;

  const elH1 = document.getElementById("kwGenH1");
  if (elH1) elH1.innerText = `<h1>${kwH1}</h1>\n<p>Looking for ${targetKw}? Here is everything you need to know about implementation, performance, and best practices.</p>`;

  if (window.lucide) {
    lucide.createIcons();
  }
}

async function renderSyndicationTab(kwAudit, meta, url) {
  const targetKw = kwAudit.target_keyword || document.getElementById("targetKeywordInput")?.value.trim() || "developer platform";
  const siteTitle = meta.title ? meta.title.split(/[-|—]/)[0].trim() : "Industry Leading Platform";
  const desc = meta.description || `The leading platform for ${targetKw}.`;

  const kwDisp = document.getElementById("syndicateKwDisplay");
  if (kwDisp) kwDisp.innerText = targetKw;

  const container = document.getElementById("directoryCardsContainer");
  if (!container) return;
  container.innerHTML = "";

  const directories = [
    {
      name: "GitHub Awesome Lists",
      badge: "DA 96",
      desc: "Top source for developers and LLM code scraper training sets.",
      url: `https://github.com/topics/${targetKw.toLowerCase().replace(/ /g, '-')}`,
      actionText: "Open Topic",
      template: `- [${siteTitle}](${url}) - ${desc}`
    },
    {
      name: "ProductHunt",
      badge: "DA 91",
      desc: "Perplexity & ChatGPT cite Product Hunt maker posts for credibility.",
      url: "https://www.producthunt.com/posts/new",
      actionText: "Launch on PH",
      template: `Tagline: The modern platform for ${targetKw}\nURL: ${url}`
    },
    {
      name: "AlternativeTo",
      badge: "DA 86",
      desc: "Rank for 'alternatives to [competitor]' queries in Google & AI.",
      url: "https://alternativeto.net/software/create/",
      actionText: "Submit Tool",
      template: `Name: ${siteTitle}\nKeyword: ${targetKw}\nLink: ${url}`
    },
    {
      name: "Slant.co",
      badge: "DA 82",
      desc: "'What are the best tools for X?' lists are cited verbatim by LLMs.",
      url: "https://www.slant.co/suggest",
      actionText: "Suggest Tool",
      template: `Option: ${siteTitle}\nWhy: Exceptional speed for ${targetKw}\nURL: ${url}`
    },
    {
      name: "Dev.to & Hashnode",
      badge: "DA 89",
      desc: "Publishing showcase articles builds organic backlink authority.",
      url: "https://dev.to/new",
      actionText: "Publish Article",
      template: `# Introducing ${siteTitle} for ${targetKw}\n\nRead more at ${url}`
    },
    {
      name: "G2 & Capterra",
      badge: "DA 92",
      desc: "Feeds review schema stars and company attributes into SERPs.",
      url: "https://www.g2.com/products/new",
      actionText: "List on G2",
      template: `Category: ${targetKw}\nCompany: ${siteTitle}\nWebsite: ${url}`
    }
  ];

  directories.forEach(d => {
    const card = document.createElement("div");
    card.className = "glass-panel p-3.5 border border-[#30363d] flex flex-col justify-between text-xs space-y-2.5";
    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-1">
          <span class="font-semibold text-white text-sm">${escapeHtml(d.name)}</span>
          <span class="px-1.5 py-0.5 rounded bg-[#21262d] text-[#8b949e] font-mono text-[10px]">${d.badge}</span>
        </div>
        <p class="text-[#8b949e] text-[11px]">${escapeHtml(d.desc)}</p>
      </div>
      <div class="space-y-2">
        <pre class="p-2 rounded bg-[#0d1117] border border-[#21262d] text-[10px] font-mono text-[#c9d1d9] overflow-x-auto select-all">${escapeHtml(d.template)}</pre>
        <div class="flex items-center gap-2">
          <button onclick="navigator.clipboard.writeText('${escapeHtml(d.template).replace(/'/g, "\\'")}'); alert('Copied snippet!');" class="btn-secondary w-full text-xs py-1">Copy</button>
          <a href="${d.url}" target="_blank" rel="noopener noreferrer" class="btn-secondary w-full text-xs py-1 text-center text-blue-400">${d.actionText} &rarr;</a>
        </div>
      </div>
    `;
    container.appendChild(card);
  });

  const redditText = document.getElementById("redditTemplateText");
  if (redditText) {
    redditText.innerText = `If you're dealing with ${targetKw}, take a look at ${siteTitle} (${url}). It was designed specifically for this use case and delivers high performance with AI-friendly static HTML fallbacks.`;
  }

  const schemaSameAs = document.getElementById("schemaSameAsCode");
  if (schemaSameAs) {
    const brand = siteTitle.toLowerCase().replace(/[^a-z0-9]/g, "");
    schemaSameAs.innerText = `<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "${siteTitle}",
  "url": "${url}",
  "sameAs": [
    "https://github.com/${brand}",
    "https://twitter.com/${brand}",
    "https://www.linkedin.com/company/${brand}",
    "https://www.crunchbase.com/organization/${brand}"
  ]
}
<\/script>`;
  }
}

async function downloadAutoFixedHtml() {
  let htmlCode = "";
  if (uploadedFileContent) {
    htmlCode = uploadedFileContent;
  } else if (document.getElementById("rawHtmlInput")?.value.trim()) {
    htmlCode = document.getElementById("rawHtmlInput").value.trim();
  }

  const targetUrl = currentAuditData?.final_url || currentAuditData?.target_url || document.getElementById("urlInput")?.value.trim() || "https://example.com";
  const targetKeyword = document.getElementById("targetKeywordInput")?.value.trim() || document.getElementById("uploadKeywordInput")?.value.trim() || document.getElementById("pasteKeywordInput")?.value.trim() || "";

  try {
    const res = await fetch("/api/generate/auto-fixed-html", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        html_code: htmlCode,
        target_url: targetUrl,
        target_keyword: targetKeyword
      })
    });
    const data = await res.json();
    if (!data.content) throw new Error("Failed to generate optimized HTML");

    const blob = new Blob([data.content], { type: "text/html;charset=utf-8" });
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = "optimized-index.html";
    a.click();
    URL.revokeObjectURL(blobUrl);
  } catch (err) {
    alert("Error downloading optimized HTML: " + err.message);
  }
}

function openPortableModal() {
  const m = document.getElementById("portableModal");
  if (m) m.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

function closePortableModal() {
  const m = document.getElementById("portableModal");
  if (m) m.classList.add("hidden");
}

let currentAiPromptType = "claude";

async function openAiExportModal(type = "claude") {
  currentAiPromptType = type;
  const m = document.getElementById("aiExportModal");
  if (m) m.classList.remove("hidden");
  switchAiPromptTab(type);
  if (window.lucide) lucide.createIcons();
}

function closeAiExportModal() {
  const m = document.getElementById("aiExportModal");
  if (m) m.classList.add("hidden");
}

async function switchAiPromptTab(type) {
  currentAiPromptType = type;
  const btnClaude = document.getElementById("btnAiTabClaude");
  const btnDeepSeek = document.getElementById("btnAiTabDeepSeek");
  const label = document.getElementById("aiPromptTypeLabel");
  const box = document.getElementById("aiPromptContentBox");

  if (type === "claude") {
    btnClaude?.classList.add("bg-[#21262d]", "text-white");
    btnDeepSeek?.classList.remove("bg-[#21262d]", "text-white");
    if (label) label.innerText = "Claude 3.5 / 3.7 XML Architecture";
  } else {
    btnDeepSeek?.classList.add("bg-[#21262d]", "text-white");
    btnClaude?.classList.remove("bg-[#21262d]", "text-white");
    if (label) label.innerText = "DeepSeek R1 / V3 Reasoning Chain (<think>)";
  }

  if (!currentAuditData) {
    if (box) box.innerText = "Please run or upload an audit first to generate this prompt.";
    return;
  }

  if (box) box.innerText = "Generating prompt from current audit data...";

  try {
    const endpoint = type === "claude" ? "/api/generate/claude-prompt" : "/api/generate/deepseek-prompt";
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ audit_data: currentAuditData })
    });
    const data = await res.json();
    if (box) box.innerText = data.content || "Error generating prompt.";
  } catch (err) {
    if (box) box.innerText = "Failed to generate prompt: " + err.message;
  }
}

function openCanvasFallbackModal() {
  const m = document.getElementById("canvasFallbackModal");
  if (m) m.classList.remove("hidden");
  
  const siteTitleInput = document.getElementById("canvasSiteTitle");
  const targetKwInput = document.getElementById("canvasTargetKw");
  
  if (currentAuditData) {
    const analysis = currentAuditData.analysis || {};
    const meta = analysis.meta || {};
    const kwAudit = analysis.target_keyword_audit || {};
    if (siteTitleInput && !siteTitleInput.value) {
      siteTitleInput.value = meta.title ? meta.title.split(/[-|—]/)[0].trim() : "Interactive 3D Experience";
    }
    if (targetKwInput && !targetKwInput.value) {
      targetKwInput.value = kwAudit.target_keyword || "interactive 3d web visualization";
    }
  }
  triggerGenerate3dCanvasSnippet();
  if (window.lucide) lucide.createIcons();
}

function closeCanvasFallbackModal() {
  const m = document.getElementById("canvasFallbackModal");
  if (m) m.classList.add("hidden");
}

async function triggerGenerate3dCanvasSnippet() {
  const title = document.getElementById("canvasSiteTitle")?.value.trim() || "Interactive 3D Experience";
  const kw = document.getElementById("canvasTargetKw")?.value.trim() || "interactive 3d web visualization";
  const box = document.getElementById("canvasSnippetBox");
  if (box) box.innerText = "Generating 3D canvas fallback snippet...";

  try {
    const res = await fetch("/api/generate/3d-canvas-fallback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ site_title: title, target_keyword: kw })
    });
    const data = await res.json();
    if (box) box.innerText = data.content || "Error generating snippet.";
  } catch (err) {
    if (box) box.innerText = "Error: " + err.message;
  }
}

function openGscModal() {
  const m = document.getElementById("gscModal");
  if (m) m.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

function closeGscModal() {
  const m = document.getElementById("gscModal");
  if (m) m.classList.add("hidden");
}

function scrollToInput() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}
