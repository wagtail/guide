export const initActiveNavItem = () => {
    const links = document.querySelectorAll('.navigation__link');
    links.forEach((link) => {
        if (new URL(link.href).pathname === window.location.pathname) {
            link.classList.add('active');
        }
    });
};
