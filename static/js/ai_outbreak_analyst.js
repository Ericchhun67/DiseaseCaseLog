document.addEventListener('DOMContentLoaded', () => {
    const generator = document.querySelector('[data-ai-generator]');

    if (!generator) {
        return;
    }

    const output = generator.querySelector('[data-note-output]');
    const submitButton = generator.querySelector('button[type="submit"]');

    generator.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(generator);
        const originalButtonText = submitButton.textContent;

        submitButton.disabled = true;
        submitButton.textContent = 'Generating...';

        try {
            const response = await fetch('/ai_analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    case_id: formData.get('case_id'),
                    tone: formData.get('tone'),
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Could not generate note.');
            }

            output.value = result.note;
        } catch (error) {
            output.value = error.message;
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    });
});
