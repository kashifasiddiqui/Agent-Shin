from typing import Any, Dict, List


class DOMInspector:
    """In-browser DOM inspection scripts for visual layout and accessibility verification."""

    CHECK_OVERFLOW_SCRIPT = """
    () => {
        const winWidth = window.innerWidth;
        const docWidth = document.documentElement.scrollWidth;
        const bodyWidth = document.body ? document.body.scrollWidth : 0;
        const maxWidth = Math.max(docWidth, bodyWidth);

        if (maxWidth > winWidth + 1) {
            const elements = Array.from(document.querySelectorAll('*'));
            const offenders = elements
                .filter(el => {
                    const rect = el.getBoundingClientRect();
                    return rect.right > winWidth + 1;
                })
                .map(el => ({
                    tag: el.tagName.toLowerCase(),
                    id: el.id || null,
                    class: (typeof el.className === 'string' ? el.className : '').trim().slice(0, 80),
                    width: Math.round(el.getBoundingClientRect().width),
                    overflowX: window.getComputedStyle(el).overflowX
                }))
                .slice(0, 5);

            return {
                has_overflow: true,
                viewport_width: winWidth,
                content_width: maxWidth,
                overflow_delta: maxWidth - winWidth,
                offenders: offenders
            };
        }
        return { has_overflow: false, viewport_width: winWidth, content_width: maxWidth };
    }
    """

    CHECK_A11Y_SCRIPT = """
    () => {
        const issues = [];

        // 1. Images missing alt attribute
        document.querySelectorAll('img').forEach((img, idx) => {
            if (!img.hasAttribute('alt')) {
                issues.push({
                    type: 'missing-alt',
                    element: 'img',
                    src: img.getAttribute('src') || 'inline/unknown',
                    selector: img.id ? '#' + img.id : `img:nth-of-type(${idx + 1})`,
                    message: 'Image is missing an alt attribute'
                });
            }
        });

        // 2. Buttons missing accessible name
        document.querySelectorAll('button').forEach((btn, idx) => {
            const text = (btn.innerText || btn.textContent || '').trim();
            const ariaLabel = btn.getAttribute('aria-label') || btn.getAttribute('aria-labelledby');
            if (!text && !ariaLabel && !btn.querySelector('svg, img')) {
                issues.push({
                    type: 'empty-button',
                    element: 'button',
                    selector: btn.id ? '#' + btn.id : `button:nth-of-type(${idx + 1})`,
                    message: 'Button element has no accessible text or aria-label'
                });
            }
        });

        // 3. Links missing accessible name
        document.querySelectorAll('a').forEach((a, idx) => {
            const text = (a.innerText || a.textContent || '').trim();
            const ariaLabel = a.getAttribute('aria-label') || a.getAttribute('aria-labelledby');
            if (!text && !ariaLabel && !a.querySelector('svg, img')) {
                issues.push({
                    type: 'empty-link',
                    element: 'a',
                    href: a.getAttribute('href') || '#',
                    selector: a.id ? '#' + a.id : `a:nth-of-type(${idx + 1})`,
                    message: 'Anchor link has no accessible text or aria-label'
                });
            }
        });

        // 4. Form inputs without labels
        document.querySelectorAll('input:not([type="hidden"]), select, textarea').forEach((input, idx) => {
            const id = input.id;
            const ariaLabel = input.getAttribute('aria-label') || input.getAttribute('aria-labelledby');
            let hasLabel = false;
            if (id && document.querySelector(`label[for="${id}"]`)) {
                hasLabel = true;
            } else if (input.closest('label')) {
                hasLabel = true;
            }

            if (!hasLabel && !ariaLabel) {
                issues.push({
                    type: 'unlabeled-input',
                    element: input.tagName.toLowerCase(),
                    selector: id ? '#' + id : `${input.tagName.toLowerCase()}:nth-of-type(${idx + 1})`,
                    message: `Form control <${input.tagName.toLowerCase()}> is missing an associated <label> or aria-label`
                });
            }
        });

        // 5. Heading hierarchy inspection
        const h1s = document.querySelectorAll('h1');
        if (h1s.length === 0) {
            issues.push({
                type: 'heading-missing-h1',
                element: 'h1',
                message: 'Page is missing a top-level <h1> heading'
            });
        } else if (h1s.length > 1) {
            issues.push({
                type: 'heading-multiple-h1',
                element: 'h1',
                count: h1s.length,
                message: `Page contains multiple (${h1s.length}) <h1> headings`
            });
        }

        return issues;
    }
    """
