document.addEventListener('DOMContentLoaded', () => {
    const recordsSection = document.querySelector('[data-case-records]');

    if (!recordsSection) {
        return;
    }

    const searchInput = recordsSection.querySelector('#caseRecordsSearch');
    const filterButtons = Array.from(recordsSection.querySelectorAll('[data-severity-filter]'));
    const records = Array.from(recordsSection.querySelectorAll('[data-case-record]'));
    const emptyState = recordsSection.querySelector('[data-empty-state]');
    const visibleCount = recordsSection.querySelector('#caseRecordsVisibleCount');
    let activeSeverity = 'all';

    function updateRecords() {
        const searchTerm = searchInput?.value.trim().toLowerCase() || '';
        let shownRecords = 0;

        records.forEach((record) => {
            const matchesSeverity = activeSeverity === 'all' || record.dataset.severity === activeSeverity;
            const matchesSearch = !searchTerm || record.dataset.search.toLowerCase().includes(searchTerm);
            const isVisible = matchesSeverity && matchesSearch;

            record.hidden = !isVisible;

            if (isVisible) {
                shownRecords += 1;
            }
        });

        if (visibleCount) {
            visibleCount.textContent = String(shownRecords);
        }

        emptyState?.toggleAttribute('hidden', shownRecords > 0);
    }

    filterButtons.forEach((button) => {
        button.addEventListener('click', () => {
            activeSeverity = button.dataset.severityFilter;

            filterButtons.forEach((filterButton) => {
                const isActive = filterButton === button;
                filterButton.classList.toggle('is-active', isActive);
                filterButton.setAttribute('aria-pressed', String(isActive));
            });

            updateRecords();
        });
    });

    searchInput?.addEventListener('input', updateRecords);
    updateRecords();
});
