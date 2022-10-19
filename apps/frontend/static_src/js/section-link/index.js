export const initSectionLink = () => {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    headings.forEach((heading) => {
        if (heading.id) {
            let sectionLink = document.createElement('a');
            let link = document.createTextNode('¶');
            sectionLink.appendChild(link);
            sectionLink.setAttribute('href', '#' + heading.id);
            sectionLink.setAttribute('class', 'section-link');
            sectionLink.setAttribute('title', 'Section link');
            heading.appendChild(sectionLink);
        }
    });
};
