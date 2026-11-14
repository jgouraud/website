/* Reveal demo artwork in place while temporarily folding the academic cards. */
window.portfolioDemos = (() => {
    function setExpanded(card, expanded) {
        const content = card.closest('.main-content');
        for (const demo of content.querySelectorAll('.demo-card')) {
            const active = expanded && demo === card;
            demo.classList.toggle('is-expanded', active);
            demo.setAttribute('aria-expanded', String(active));
        }
        content.classList.toggle('demo-expanded', expanded);
        const projects = content.querySelector('.projects-collapse');
        projects.inert = expanded;
        projects.setAttribute('aria-hidden', String(expanded));
    }

    function close(card, force = false) {
        if (!card.classList.contains('is-expanded')) return;
        if (!force && (card.matches(':hover, :focus-visible') || card.querySelector(':focus-visible'))) return;
        setExpanded(card, false);
    }

    return {
        enter(event) {
            if (event.pointerType !== 'touch') setExpanded(event.currentTarget, true);
        },
        leave(event) {
            if (event.pointerType !== 'touch') close(event.currentTarget);
        },
        focus(event) {
            if (event.target.matches(':focus-visible')) setExpanded(event.currentTarget, true);
        },
        blur(event) {
            if (!event.currentTarget.contains(event.relatedTarget)) close(event.currentTarget);
        },
        key(event) {
            const card = event.currentTarget;
            if (event.key === 'Escape') {
                event.stopPropagation();
                close(card, true);
            } else if (event.target === card && ['Enter', ' '].includes(event.key)) {
                event.preventDefault();
                setExpanded(card, !card.classList.contains('is-expanded'));
            }
        },
        click(event) {
            // Arrow navigation is independent from the artwork reveal gesture.
            if (event.target.closest('a')) return;
            if (window.matchMedia('(hover: none)').matches) {
                const card = event.currentTarget;
                setExpanded(card, !card.classList.contains('is-expanded'));
            }
        },
    };
})();
