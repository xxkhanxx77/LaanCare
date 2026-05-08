(function () {
    const context = window.SYMPTOM_CHAT_CONTEXT || {};
    const userId = context.lineUserId || "U_DEMO";
    const messagesEl = document.getElementById("messages");
    const quickActionsEl = document.getElementById("quick-actions");
    const formEl = document.getElementById("chat-form");
    const inputEl = document.getElementById("chat-input");
    const resetButton = document.getElementById("reset-button");
    const riskEl = document.getElementById("risk-level");
    const groupEl = document.getElementById("group-name");
    const llmEl = document.getElementById("llm-status");
    const alertsEl = document.getElementById("alerts");
    const knowledgeEl = document.getElementById("knowledge");

    function addMessage(role, text) {
        if (!text) return;
        const item = document.createElement("div");
        item.className = `message ${role}`;
        item.textContent = text;
        messagesEl.appendChild(item);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function clearActions() {
        quickActionsEl.replaceChildren();
    }

    function renderActions(uiMessages) {
        clearActions();
        const actions = [];
        (uiMessages || []).forEach((item) => {
            if (item.title || item.body) {
                addMessage("bot", [item.title, item.body].filter(Boolean).join("\n"));
            }
            (item.actions || []).forEach((action) => actions.push(action));
        });

        actions.forEach((action) => {
            const button = document.createElement("button");
            button.className = "quick-button";
            button.type = "button";
            button.textContent = action.label || action.text;
            button.addEventListener("click", () => sendMessage(action.text || action.label, true));
            quickActionsEl.appendChild(button);
        });
    }

    function renderAlerts(alerts) {
        if (!alerts || !alerts.length) {
            alertsEl.textContent = "ยังไม่มี alert";
            return;
        }
        alertsEl.replaceChildren();
        alerts.forEach((alert) => {
            const item = document.createElement("div");
            item.className = "message alert";
            item.textContent = alert.message || JSON.stringify(alert, null, 2);
            alertsEl.appendChild(item);
        });
    }

    function renderKnowledge(knowledge) {
        if (!knowledge) {
            knowledgeEl.textContent = "ยังไม่มีข้อมูล";
            return;
        }
        const selected = knowledge.selected_group || {};
        const candidates = (knowledge.candidate_groups || [])
            .slice(0, 5)
            .map((item) => `${item.group_id || ""} ${item.group_name_th || ""}`.trim())
            .filter(Boolean);
        const rules = (knowledge.active_rules || [])
            .map((rule) => `${rule.rule_id}: ${rule.user_friendly_check}`)
            .join("\n");
        knowledgeEl.textContent = [
            selected.group_id ? `${selected.group_id} ${selected.group_name_th || ""}` : "",
            candidates.length ? `Candidates:\n${candidates.join("\n")}` : "",
            rules ? `Rules:\n${rules}` : "",
        ].filter(Boolean).join("\n\n") || "ยังไม่มีข้อมูล";
    }

    function renderState(result) {
        const state = result.state || {};
        const knowledge = result.knowledge_retrieved || {};
        const selected = knowledge.selected_group || {};
        riskEl.textContent = state.risk_level || "-";
        groupEl.textContent = selected.group_name_th || selected.group_id || state.active_group_id || "-";
        renderAlerts(result.alert_messages || []);
        renderKnowledge(knowledge);
    }

    function renderResult(result) {
        (result.reply_messages || []).forEach((message) => addMessage("bot", message));
        renderActions(result.ui_messages || []);
        renderState(result);
    }

    async function sendMessage(text, fromAction) {
        const value = (text || inputEl.value || "").trim();
        if (!value) return;
        if (!fromAction) inputEl.value = "";
        addMessage("user", value);
        clearActions();

        const response = await fetch("/api/symptom-chat/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                user_id: userId,
                line_user_id: context.lineUserId || "",
                group_id: context.groupId || "",
                text: value,
                session_mode: "self_checkin",
                user_can_chat: true,
            }),
        });
        const result = await response.json();
        if (!response.ok) {
            addMessage("bot", result.error || "เกิดข้อผิดพลาด");
            return;
        }
        renderResult(result);
    }

    async function resetFlow() {
        clearActions();
        const response = await fetch("/api/symptom-chat/reset", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({user_id: userId, line_user_id: context.lineUserId || ""}),
        });
        const result = await response.json();
        messagesEl.replaceChildren();
        addMessage("bot", "เริ่มรอบเช็กอินใหม่แล้ว พิมพ์ “เช็กอิน” เพื่อเริ่มได้เลย");
        renderResult(result);
    }

    async function bootstrap() {
        const response = await fetch(`/api/symptom-chat/bootstrap?user_id=${encodeURIComponent(userId)}`);
        const data = await response.json();
        llmEl.textContent = data.llm && data.llm.enabled ? data.llm.model : "local rules";
        riskEl.textContent = (data.session && data.session.state_json && data.session.state_json.risk_level) || "-";
        groupEl.textContent = (data.session && data.session.state_json && data.session.state_json.active_group_id) || "-";
        renderAlerts(data.alerts || []);
        addMessage("bot", "พร้อมเช็กอินอาการแล้วครับ พิมพ์ “เช็กอิน” หรือเล่าอาการผิดปกติได้เลย");
    }

    formEl.addEventListener("submit", (event) => {
        event.preventDefault();
        sendMessage();
    });
    resetButton.addEventListener("click", resetFlow);
    bootstrap();
})();
