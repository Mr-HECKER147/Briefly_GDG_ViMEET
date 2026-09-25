document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy-summary]");
    if (!button) return;

    const result = button.closest(".result");
    const summary = result?.querySelector("[data-summary-content]");
    const status = result?.querySelector("[data-copy-status]");
    if (!summary || !status) return;

    try {
        await navigator.clipboard.writeText(summary.innerText.trim());
        status.textContent = "Copied to clipboard.";
    } catch {
        status.textContent = "Copy failed. Select the summary and copy it manually.";
    }
});
