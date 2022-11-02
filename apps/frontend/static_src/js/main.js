import debounce from 'lodash.debounce';
import './theme-detect';
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

    const resultsCountHeading = document.createElement('h2');
    resultsCountHeading.innerText = `${results.length} ${
        results.length === 1 ? 'result' : 'results'
    } found`;
    resultsCountHeading.classList.add('autocomplete__count');
    resultsCountContainer.appendChild(resultsCountHeading);

    results.forEach((result) => {
        const resultDiv = document.createElement('a');
        const resultHeading = document.createElement('h3');
        const resultDescription = document.createElement('div');
        const resultParentSection = document.createElement('div');
        resultHeading.innerText = result.title;
        resultDescription.innerText = result.search_description;
        resultParentSection.innerText = result.parent_section;
        resultDiv.href = result.full_url;
        resultDiv.appendChild(resultParentSection);
        resultDiv.appendChild(resultHeading);
        resultDiv.appendChild(resultDescription);
        resultParentSection.classList.add('autocomplete__meta');
        resultDescription.classList.add('autocomplete__description');
        resultDiv.classList.add('autocomplete__row');
        resultHeading.classList.add('autocomplete__heading');
        resultsDiv.appendChild(resultDiv);
    });
};

const onSearchInputChange = async (event) => {
    const query = event.target.value;
    try {
        const res = await fetch(
            `${window.location.origin}${
                window.languageCode ? `/${window.languageCode}` : ''
            }/search_json/?${new URLSearchParams({
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
searchInput.addEventListener('keyup', debounce(onSearchInputChange, 150));

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
