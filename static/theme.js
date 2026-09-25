(() => {
    const storageKey = "briefly-theme";

    let theme = "light";
    try {
        if (localStorage.getItem(storageKey) === "dark") {
            theme = "dark";
        }
    } catch {
        // Keep the light theme when browser storage is unavailable.
    }

    document.documentElement.dataset.theme = theme;

    document.addEventListener("DOMContentLoaded", () => {
        const toggle = document.querySelector("[data-theme-toggle]");
        if (!toggle) return;

        const updateButton = () => {
            const isDark = document.documentElement.dataset.theme === "dark";
            toggle.textContent = isDark ? "Light mode" : "Dark mode";
            toggle.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
            toggle.setAttribute("aria-pressed", String(isDark));
        };

        toggle.addEventListener("click", () => {
            theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            document.documentElement.dataset.theme = theme;
            try {
                localStorage.setItem(storageKey, theme);
            } catch {
                // The current page still changes theme if storage is unavailable.
            }
            updateButton();
        });

        updateButton();
    });
})();
