async function loadConfig() {
  const c = await fetch("/api/config").then((r) => r.json());
  document.getElementById("coord").value = c.coordinator_url || "";
  document.getElementById("enroll").value = c.enroll_token || "";
  document.getElementById("workerId").value = c.worker_id || "";
  document.getElementById("site").value = c.site_id || "wan";
  document.getElementById("openai").value = c.openai_base_url || "";
  document.getElementById("rpcPort").value = c.rpc_port || "";
}

async function saveAndConnect() {
  const body = {
    coordinator_url: document.getElementById("coord").value.trim(),
    enroll_token: document.getElementById("enroll").value.trim(),
    worker_id: document.getElementById("workerId").value.trim(),
    site_id: document.getElementById("site").value.trim(),
    openai_base_url: document.getElementById("openai").value.trim() || null,
    rpc_port: document.getElementById("rpcPort").value.trim() || null,
  };
  await fetch("/api/config", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  await fetch("/api/agent/start", { method: "POST" });
  pollStatus();
}

async function pollStatus() {
  const s = await fetch("/api/agent/status").then((r) => r.json());
  document.getElementById("phase").textContent = s.phase;
  document.getElementById("phase").className = s.connected ? "ok" : "err";
  document.getElementById("msg").textContent = s.message || "";
  document.getElementById("log").textContent = (s.log || []).join("\n");
}

document.getElementById("save").addEventListener("click", saveAndConnect);
document.getElementById("stop").addEventListener("click", async () => {
  await fetch("/api/agent/stop", { method: "POST" });
  pollStatus();
});

loadConfig();
setInterval(pollStatus, 3000);
pollStatus();
