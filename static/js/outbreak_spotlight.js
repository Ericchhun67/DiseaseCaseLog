document.addEventListener('DOMContentLoaded', () => {
    const carousel = document.getElementById('outbreakCarousel');

    if (!carousel) {
        return;
    }

    const spotlight = carousel.closest('.outbreak-spotlight');
    const slides = Array.from(carousel.querySelectorAll('.outbreak-spotlight__card'));
    const indicators = Array.from(document.querySelectorAll('.outbreak-spotlight__indicator'));
    const currentSlide = document.getElementById('currentSlide');
    const previousButton = document.getElementById('prevSlide');
    const nextButton = document.getElementById('nextSlide');
    const severityClassNames = ['low', 'moderate', 'high', 'critical'];

    if (slides.length === 0) {
        return;
    }

    let activeIndex = 0;
    let rotationTimer = null;

    function showSlide(nextIndex) {
        activeIndex = (nextIndex + slides.length) % slides.length;

        slides.forEach((slide, index) => {
            const isActive = index === activeIndex;
            slide.classList.toggle('is-active', isActive);
            slide.toggleAttribute('hidden', !isActive);
        });

        indicators.forEach((indicator, index) => {
            const isActive = index === activeIndex;
            indicator.classList.toggle('is-active', isActive);
            indicator.setAttribute('aria-selected', String(isActive));
        });

        if (currentSlide) {
            currentSlide.textContent = String(activeIndex + 1);
        }

        if (spotlight) {
            const activeSlide = slides[activeIndex];

            severityClassNames.forEach((severity) => {
                spotlight.classList.toggle(
                    `outbreak-spotlight--${severity}`,
                    activeSlide.classList.contains(`outbreak-spotlight__card--${severity}`)
                );
            });
        }
    }

    function startRotation() {
        if (slides.length < 2) {
            return;
        }

        stopRotation();
        rotationTimer = window.setInterval(() => showSlide(activeIndex + 1), 5000);
    }

    function stopRotation() {
        if (rotationTimer) {
            window.clearInterval(rotationTimer);
            rotationTimer = null;
        }
    }

    previousButton?.addEventListener('click', () => {
        showSlide(activeIndex - 1);
        startRotation();
    });

    nextButton?.addEventListener('click', () => {
        showSlide(activeIndex + 1);
        startRotation();
    });

    indicators.forEach((indicator) => {
        indicator.addEventListener('click', () => {
            showSlide(Number(indicator.dataset.slide));
            startRotation();
        });
    });

    spotlight?.addEventListener('mouseenter', stopRotation);
    spotlight?.addEventListener('mouseleave', startRotation);
    spotlight?.addEventListener('focusin', stopRotation);
    spotlight?.addEventListener('focusout', startRotation);

    showSlide(0);
    startRotation();
});
