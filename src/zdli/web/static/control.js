const adminToken = () => localStorage.getItem("zdl_admin_token") || "dev-coordinator-token";
const headers = () => ({ Authorization: "Bearer " + adminToken(), "Content-Type": "application/json" });

async function api(path, opts = {}) {
  const r = await fetch(path, { ...opts, headers: { ...headers(), ...(opts.headers || {}) } });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

async function refresh() {
  const info = await api("/api/cluster/info");
  const enroll = await api("/api/cluster/enroll-token");
  document.getElementById("pubCoord").textContent = info.public_coordinator_url;
  document.getElementById("pubGw").textContent = info.public_gateway_url;
  document.getElementById("enrollHint").textContent = enroll.enroll_token;
  document.getElementById("counts").textContent =
    `${info.healthy_workers}/${info.worker_count} workers healthy`;

  const workers = await api("/zdl/v1/workers");
  const tbody = document.querySelector("#workers tbody");
  tbody.innerHTML = "";
  for (const w of workers) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${w.worker_id}</td><td>${w.hostname || "-"}</td><td>${w.os_name || "-"}</td>
      <td>${w.site_id}</td><td class="${w.healthy ? "ok" : "err"}">${w.phase}</td>
      <td>${w.status_message || ""}</td><td>${w.healthy ? "yes" : "no"}</td>`;
    tbody.appendChild(tr);
  }

  const jobs = await api("/api/schedule");
  const jbody = document.querySelector("#jobs tbody");
  jbody.innerHTML = "";
  for (const j of jobs) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${j.name}</td><td>${j.interval_minutes}m</td><td>${j.action}</td>
      <td>${j.next_run || "-"}</td><td>${j.last_run || "-"}</td>`;
    jbody.appendChild(tr);
  }
}

document.getElementById("savePublic").addEventListener("click", async () => {
  await api("/api/cluster/public-urls", {
    method: "POST",
    body: JSON.stringify({
      public_coordinator_url: document.getElementById("inCoord").value,
      public_gateway_url: document.getElementById("inGw").value,
    }),
  });
  await refresh();
});

document.getElementById("addJob").addEventListener("click", async () => {
  await api("/api/schedule", {
    method: "POST",
    body: JSON.stringify({
      name: document.getElementById("jobName").value || "Health check",
      interval_minutes: parseInt(document.getElementById("jobInterval").value, 10) || 60,
      action: "cluster_health",
    }),
  });
  await refresh();
});

document.getElementById("bootstrap").addEventListener("click", async () => {
  const r = await fetch("/api/cluster/bootstrap-graph", { method: "POST", headers: headers() });
  document.getElementById("bootMsg").textContent = r.ok ? "Graph published (needs ingress URL on a worker)." : await r.text();
});

setInterval(refresh, 5000);
refresh();
