import debounce from 'lodash.debounce';
import { initSectionLink } from './section-link';
import { handleFeedback } from './feedback';
import MobileMenu from './mobile-menu';

initSectionLink();
handleFeedback();

const searchInput = document.querySelector('[data-search-input]');
const searchIconButton = document.querySelector('[data-search-icon-button]');

const removeExistingChildren = (parent) => {
    // eslint-disable-next-line no-param-reassign
    parent.innerHTML = '';
};

const injectResultsInHTML = (results) => {
    const resultsDiv = document.querySelector('[data-results]');
    const resultsCountContainer = document.querySelector(
        '[data-results-count-container]',
    );

    removeExistingChildren(resultsDiv);
    removeExistingChildren(resultsCountContainer);

    const resultsCountDiv = document.createElement('div');
    resultsCountDiv.innerText = `${results.length} ${
        results.length === 1 ? 'result' : 'results'
    } found`;
    resultsCountDiv.classList.add('m-3', 'mx-5');
    resultsCountContainer.appendChild(resultsCountDiv);

    results.forEach((result) => {
        const resultDiv = document.createElement('div');
        const resultLink = document.createElement('a');
        const resultDescription = document.createElement('div');
        const resultParentSection = document.createElement('div');
        resultLink.innerText = result.title;
        resultDescription.innerText = result.search_description;
        resultParentSection.innerText = result.parent_section;
        resultLink.href = result.full_url;
        resultDiv.appendChild(resultParentSection);
        resultDiv.appendChild(resultLink);
        resultDiv.appendChild(resultDescription);
        resultParentSection.classList.add('py-2');
        resultLink.classList.add(
            'fw-bold',
            'fs-5',
            'text-decoration-none',
            'text-dark',
        );
        resultDescription.classList.add('text-muted', 'py-2');
        resultDiv.classList.add('mx-5', 'py-4', 'border-top', 'border-bottom');
        resultsDiv.appendChild(resultDiv);
    });
};

const onSearchInputChange = async (event) => {
    const query = event.target.value;
    try {
        const res = await fetch(
            `${window.location.origin}/search_json/?${new URLSearchParams({
                query,
            }).toString()}`,
        );
        const data = await res.json();
        injectResultsInHTML(data);
    } catch (err) {
        // eslint-disable-next-line no-console
        console.log(err);
        // eslint-disable-next-line no-alert
        window.alert(`Error: ${err}`);
    }
};
searchInput.addEventListener('keyup', debounce(onSearchInputChange, 350));

searchIconButton.addEventListener('click', () => {
    const resultsDiv = document.querySelector('[data-results]');
    const resultsCountContainer = document.querySelector(
        '[data-results-count-container]',
    );

    removeExistingChildren(resultsDiv);
    removeExistingChildren(resultsCountContainer);
});

function initComponent(ComponentClass) {
    const items = document.querySelectorAll(ComponentClass.selector());
    items.forEach((item) => new ComponentClass(item));
}

document.addEventListener('DOMContentLoaded', () => {
    // Remove no-js class if JS is enabled
    document.documentElement.classList.remove('no-js');
    initComponent(MobileMenu);
});
