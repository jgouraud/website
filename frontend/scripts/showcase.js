/* Hover selection is transient: moving away from a card restores all rows.
   Use actual pointer movement (not pointerover/out) to ignore hover changes
   caused purely by the page reflowing when rows collapse. */
(() => {
    function main() { return document.querySelector('.main-content[data-active-row]'); }
    let hoveredCard = null;
    let keyboardCard = null;
    let keyboardNavigation = false;
    let selectedRow = null; // Explicitly selected via a "Show all" link.

    function cardRow(card) {
        return card?.closest('.showcase-section')?.dataset.showcaseRow || null;
    }
    function update() {
        const root = main();
        if (!root) return;
        root.dataset.activeRow = cardRow(hoveredCard) || cardRow(keyboardCard) || selectedRow || 'all';
        root.querySelectorAll('.showcase-card.is-row-active').forEach(card => {
            card.classList.remove('is-row-active');
        });
        if (selectedRow) {
            root.querySelectorAll(`.showcase-section[data-showcase-row="${selectedRow}"] .showcase-card`).forEach(card => {
                card.classList.add('is-row-active');
            });
        }
        root.querySelectorAll('[data-showcase-toggle]').forEach(link => {
            link.setAttribute('aria-expanded', String(
                root.dataset.activeRow === link.dataset.showcaseToggle
            ));
        });
    }
    function hover(card) {
        if (card === hoveredCard) return;
        hoveredCard?.classList.remove('is-hover-active');
        hoveredCard = card;
        hoveredCard?.classList.add('is-hover-active');
        update();
    }
    function pointerMoved(event) {
        if (event.pointerType === 'touch') return;
        const root = main();
        if (!root) return;
        // elementFromPoint checks the current layout, including animated rows.
        const element = document.elementFromPoint(event.clientX, event.clientY);
        const card = element?.closest('.showcase-card') || null;
        const nextCard = card && root.contains(card) ? card : null;
        if (hoveredCard && hoveredCard !== nextCard) {
            // Restore the other rows on the first real movement outside the card.
            // Don't select a new card on the same event: restoring the layout can
            // otherwise cause rapid row switching while things animate.
            hover(null);
            return;
        }
        if (nextCard && !hoveredCard) hover(nextCard);
    }
    window.portfolioShowcase = {
        select: row => { selectedRow = row === 'all' ? null : row; hover(null); update(); },
        toggle: row => { selectedRow = selectedRow === row ? null : row; update(); },
        reset: () => { selectedRow = null; keyboardCard = null; hover(null); },
    };
    document.addEventListener('pointermove', pointerMoved, {passive: true});
    document.addEventListener('pointerout', event => {
        // Leaving the browser/document altogether also clears transient hover.
        if (!event.relatedTarget) hover(null);
    });
    document.addEventListener('pointercancel', () => hover(null));
    window.addEventListener('blur', () => hover(null));
    document.addEventListener('pointerdown', () => {
        keyboardNavigation = false;
        keyboardCard = null; // Mouse clicks must not leave a sticky focus state.
        update();
    });
    document.addEventListener('focusin', event => {
        if (!keyboardNavigation) return;
        keyboardCard = event.target.closest?.('.showcase-card') || null;
        update();
    });
    document.addEventListener('focusout', () => {
        queueMicrotask(() => {
            if (!keyboardNavigation) return;
            keyboardCard = document.activeElement?.closest?.('.showcase-card') || null;
            update();
        });
    });
    document.addEventListener('click', event => {
        const toggle = event.target.closest?.('[data-showcase-toggle]');
        if (toggle) {
            event.preventDefault();
            window.portfolioShowcase.toggle(toggle.dataset.showcaseToggle);
        }
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            window.portfolioShowcase.reset();
        } else if (event.key === 'Tab' || event.key.startsWith('Arrow')) {
            keyboardNavigation = true;
        }
    });
})();
